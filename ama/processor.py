# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: processor
   :platform: Unix
   :synopsis: Funciones útiles para el procesamiento de datos de radar.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

import wradlib as wrl
import pylab as pl
import matplotlib.pyplot as plt
import numpy as np
import paho.mqtt.client as mqtt
import os
import ntpath
import time
import sys

from ama.utils import Colors
from ama.utils import Utils
from haversine import haversine

__author__ = "Andreas P. Koenzen"
__copyright__ = "Copyright 2016, Proyecto de Tesis / Universidad Católica de Asunción."
__credits__ = "Andreas P. Koenzen"
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Andreas P. Koenzen"
__email__ = "akc@apkc.net"
__status__ = "Prototype"


class Processor:
    """
    Procesador de datos de radar. Clase principal donde se encuentran todas las funciones de
    procesamiento de datos.
    """

    def __init__(self):
        pass

    DEBUG = False
    """
    boolean: Bandera para habilitar/deshabilitar modo DEBUG.
    """
    FILE_SIZE_LIMIT = 2 * 1024 * 1024  # 2MB para los archivos del GAMIC con zoom out.
    """
    int: Tamaño máximo de archivos a procesar. Todos los archivos que sobrepasen este tamaño serán obviados.
    """
    QT = -1
    """
    int: La cantidad de archivos a procesar dentro de un directorio.
    """

    @staticmethod
    def process(filename):
        """
        Procesa un archivo de datos de radar en formato GAMIC HDF5 y devuelve
        los datos.

        Todo:
        * Agregar soporte para Excepciones.

        :param filename: El nombre del archivo a procesar. El formato debe ser \
            *WRADLIB_DATA/<filename>*.

        :return: Los datos de radar procesados.
        """
        filename = wrl.util.get_wradlib_data_file(filename)
        start = time.time()
        data, metadata = wrl.io.read_GAMIC_hdf5(filename)
        end = time.time()

        print(Colors.OKGREEN + "\tINFO: Procesado \"{0}\" en {1} segundos.".format(filename, (end - start)) + Colors.ENDC)

        return data, metadata

    def process_directory_generate_raw_images_from_reflectivity(self, origin, destination):
        """
        Procesa todos los archivos que se encuentran en el directorio
        de datos de forma recursiva y genera imagenes para cada set de datos
        utilizando los datos de reflectividad.

        Todo:
        * Agregar soporte para Excepciones.

        :param origin: El directorio origen de datos.
        :param destination: El directorio destino de las imagenes.

        :return: void
        """
        origin = os.path.join(os.environ["WRADLIB_DATA"], origin)
        destination = os.path.join(os.environ["AMA_EXPORT_DATA"], destination)
        matches = Utils.files_for_processing(origin, self.QT, self.FILE_SIZE_LIMIT)

        if len(matches) > 0:
            for item in matches:
                data, metadata = Processor.process(item)
                fig = pl.figure(figsize=(10, 8))
                wrl.vis.plot_cg_ppi(data[u"SCAN0"][u"Z"]["data"], fig=fig)

                if not os.path.exists(destination):
                    print(Colors.WARNING + "\tWARN: Destino no existe, creando ..." + Colors.ENDC)
                    os.makedirs(destination)

                clean_filename = os.path.splitext(ntpath.basename(item))[0]
                pl.savefig(os.path.join(destination, (clean_filename + ".png")), bbox_inches="tight")
                plt.close(fig)

            if self.DEBUG == 1:
                print(metadata)
                print("------")
                print(data)

                for index, item in enumerate(matches):
                    print("{0} => {1}".format(index, item))

                for index, item in enumerate(matches):
                    print("{0} => {1}".format(index, os.path.splitext(ntpath.basename(item))[0]))
        else:
            print(Colors.FAIL + "\tERROR: No hay archivos para procesar en *{0}*!".format(
                os.environ["WRADLIB_DATA"] + origin) + Colors.ENDC)

    def process_directory_generate_raw_images_from_rainfall_intensity(self, origin, destination):
        """
        Procesa todos los archivos que se encuentran en el directorio
        de datos de forma recursiva y genera imagenes para cada set de datos
        utilizando los datos de intensidad de lluvia.

        Todo:
        * Agregar soporte para Excepciones.

        :param origin: El directorio origen de datos.
        :param destination: El directorio destino de las imagenes.

        :return: void
        """
        origin = os.path.join(os.environ["WRADLIB_DATA"], origin)
        destination = os.path.join(os.environ["AMA_EXPORT_DATA"], destination)
        matches = Utils.files_for_processing(origin, self.QT, self.FILE_SIZE_LIMIT)

        if len(matches) > 0:
            for item in matches:
                data, metadata = Processor.process(item)

                Z = wrl.trafo.idecibel(data[u"SCAN0"][u"Z"]["data"])
                R = wrl.zr.z2r(Z, a=200., b=1.6)

                fig = pl.figure(figsize=(10, 8))
                ax, cf = wrl.vis.plot_ppi(R, cmap="spectral")
                pl.xlabel("Este del Radar (km)")
                pl.ylabel("Norte del Radar (km)")
                pl.title("Radar DINAC Fac. Veterinaria UNA\n6 min. profundidad de lluvia, " + metadata[u"SCAN0"]["Time"])
                cb = pl.colorbar(cf, shrink=0.8)
                cb.set_label("mm/h")
                pl.xlim(-128, 128)
                pl.ylim(-128, 128)
                pl.grid(color="grey")

                if not os.path.exists(destination):
                    print(Colors.WARNING + "\tWARN: Destino no existe, creando ..." + Colors.ENDC)
                    os.makedirs(destination)

                clean_filename = os.path.splitext(ntpath.basename(item))[0]
                pl.savefig(os.path.join(destination, (clean_filename + ".png")), bbox_inches="tight")
                plt.close(fig)

            if self.DEBUG == 1:
                print(metadata)
                print("------")
                print(data)

                for index, item in enumerate(matches):
                    print("{0} => {1}".format(index, item))

                for index, item in enumerate(matches):
                    print("{0} => {1}".format(index, os.path.splitext(ntpath.basename(item))[0]))
        else:
            print(Colors.FAIL + "ERROR: No hay archivos para procesar en *{0}*!".format(
                os.environ["WRADLIB_DATA"] + origin) + Colors.ENDC)

    def single_correlate_dbz_to_location(self, filename, destination, report_to_mqtt=False, use_filter=False, radius=50):
        """
        Esta funcion realiza la correlacion entre dbZ y sus coordenadas geograficas en el mapa.

        Formato del archivo a generar:
        ==============================
        Se genera un archivo *.ama, el cual no es nada mas que un archivo de texto separado por
        lineas, en el cual cada registro a su vez se encuentra separado por comas.

        Ejemplo:
            dbZ,rainfall_intensity,latitude:longitude

        Todo:
        * Agregar soporte para Excepciones.
        * Agregar soporte para escribir resultado a archivo.

        :param filename: El nombre del archivo a procesar.
        :param destination: El nombre del directorio en donde colocar los archivos resultantes.
        :param report_to_mqtt: Si debemos enviar los resultados a un tópico MQTT.
        :param use_filter: Si los filtros deben estar habilitados.
        :param radius: El radio para los filtros. En km desde la ubicación del radar. Todos \
            los puntos que se encuentren dentro de este radio serán incluidos en el archivo \
            resultante.

        :return: void
        """
        start = time.time()
        cdata = ""
        destination = os.path.join(os.environ["AMA_EXPORT_DATA"], destination, (os.path.splitext(ntpath.basename(filename))[0] + ".ama"))
        data, metadata = Processor.process(filename)
        clean_data = []

        if report_to_mqtt:
            client = mqtt.Client()
            client.connect("devel.apkc.net", 1883, 60)

        file = open(destination, "w")

        radar_latitude = float(metadata["VOL"]["Latitude"])
        radar_longitude = float(metadata["VOL"]["Longitude"])

        for (r, c), value in np.ndenumerate(data[u"SCAN0"][u"Z"]["data"]):
            if value > -64.:
                rng = metadata[u"SCAN0"]["r"][c]
                azi = metadata[u"SCAN0"]["az"][r]
                z = wrl.trafo.idecibel(value)
                ri = wrl.zr.z2r(z, a=200., b=1.6)
                lon, lat = wrl.georef.polar2lonlat(rng, azi, (radar_longitude, radar_latitude))

                # realizar los redondeos
                rainfall_intensity = float("{0:.2f}".format(ri))
                latitude = float("{0:.5f}".format(lat))
                longitude = float("{0:.5f}".format(lon))

                if (haversine((radar_latitude, radar_longitude), (latitude, longitude)) < radius and ri > 5) or not use_filter:
                    clean_data.append((rainfall_intensity, latitude, longitude))

        for i, (ri, lat, lon) in enumerate(clean_data):
            line = "{0:.2f},{1:.5f}:{2:.5f}".format(ri, lat, lon)

            file.write(line + "\n")

            if report_to_mqtt:
                client.publish("ama-export-data", line, 2)
                client.loop(1)

            cdata += line

            if self.DEBUG == 1:
                print(line)

        if report_to_mqtt:
            client.disconnect()

        file.close()

        end = time.time()

        if self.DEBUG == 1:
            print(Colors.HEADER + "---" + Colors.ENDC)
            print(Colors.HEADER + "Tamaño Datos Enviados: {0}kb".format(sys.getsizeof(cdata) / 1024) + Colors.ENDC)
            print(Colors.HEADER + "Tiempo de Procesamiento: {0:.1f} minutos".format((end - start) / 60) + Colors.ENDC)

    def correlate_dbz_to_location(self, filename, destination, process_all, report_to_mqtt=False, use_filter=False, radius=50):
        """
        Esta funcion realiza la correlacion entre dbZ y sus coordenadas geograficas en el mapa.

        Formato del archivo a generar:
        ==============================
        Se genera un archivo *.ama, el cual no es nada mas que un archivo de texto separado por
        lineas, en el cual cada registro a su vez se encuentra separado por comas.

        Ejemplo:
            dbZ,rainfall_intensity,latitude:longitude

        Todo:
        * Agregar soporte para Excepciones.
        * Agregar soporte para escribir resultado a archivo.

        :param filename: El nombre del archivo a procesar.
        :param destination: El nombre del directorio en donde colocar los archivos resultantes.
        :param report_to_mqtt: Si debemos enviar los resultados a un tópico MQTT.
        :param use_filter: Si los filtros deben estar habilitados.
        :param radius: El radio para los filtros. En km desde la ubicación del radar. Todos \
            los puntos que se encuentren dentro de este radio serán incluidos en el archivo \
            resultante.
        :param process_all Procesar todos los archivos en la carpeta donde se encuentra el archivo \
            pasado como *filename*.

        :return: void
        """
        if process_all:
            origin = os.path.join(os.environ["WRADLIB_DATA"], os.path.split(filename)[0])
            destination = os.path.join(os.environ["AMA_EXPORT_DATA"], destination)
            matches = Utils.files_for_processing(origin, self.QT, self.FILE_SIZE_LIMIT)

            if len(matches) > 0:
                for item in matches:
                    self.single_correlate_dbz_to_location(item, destination, report_to_mqtt, use_filter, radius)
        else:
            self.single_correlate_dbz_to_location(filename, destination, report_to_mqtt, use_filter, radius)
