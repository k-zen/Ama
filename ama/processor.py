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
import os
import ntpath
import time
import sys
import requests

from ama.utils import Colors
from ama.utils import Utils

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

    ###### OPCIONES MISCELANEAS ######
    DEBUG = False
    """
    boolean: Bandera para habilitar/deshabilitar modo DEBUG.
    """
    FILE_SIZE_LIMIT = 4 * 1024 * 1024  # 4MB para los archivos del GAMIC con zoom out.
    """
    int: Tamaño máximo de archivos a procesar. Todos los archivos que sobrepasen este tamaño serán obviados.
    """
    QT = -1
    """
    int: La cantidad de archivos a procesar dentro de un directorio.
    """
    SHOULD_REMOVE_PROCESSED_FILES = False
    """
    boolean: Bandera para habilitar el borrado de archivos luego de procesarlos. Solo para modo *run*.
    """

    @staticmethod
    def process(filename):
        """
        Procesa un archivo de datos de radar en formato GAMIC HDF5 y devuelve
        los datos.
        
        Esta función esta diseñada para archivos de modalidad Simple y Doppler.

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
        
        Esta función esta diseñada para archivos de modalidad Simple.

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

        Esta función esta diseñada para archivos de modalidad Simple.

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
            print(Colors.FAIL + "\tERROR: No hay archivos para procesar en *{0}*!".format(
                os.environ["WRADLIB_DATA"] + origin) + Colors.ENDC)

    def single_correlate_dbz_to_location(self, filename, destination, layer):
        """
        Esta funcion realiza la correlacion entre dBZ y sus coordenadas geograficas en el mapa.
        
        Esta función esta diseñada para archivos de modalidad Simple y Doppler.

        Formato del archivo a generar:
        ==============================
        Se genera un archivo *.ama, el cual no es nada mas que un archivo de texto separado por
        lineas, en el cual cada registro a su vez se encuentra separado por comas.

        Ejemplo:
            dBZ,latitude:longitude

        :param filename: El nombre del archivo a procesar.
        :param destination: El nombre del directorio en donde colocar los archivos resultantes.
        :param layer: La capa de datos a procesar. Cada capa corresponde a un ángulo de elevación del radar.

        :return: void
        """
        start = time.time()
        cdata = ""
        destination = os.path.join(os.environ["AMA_EXPORT_DATA"], destination,
                                   (os.path.splitext(ntpath.basename(filename))[0] + ".layer_{0}.ama".format(layer)))
        data, metadata = Processor.process(filename)
        clean_data = []
        layer_key = u"SCAN{0}".format(layer)

        file = open(destination, "w")

        radar_latitude = float(metadata["VOL"]["Latitude"])
        radar_longitude = float(metadata["VOL"]["Longitude"])

        for (row, column), value in np.ndenumerate(data[layer_key][u"Z"]["data"]):
            if value > -64.:
                rng = metadata[layer_key]["r"][column]
                azi = metadata[layer_key]["az"][row]
                dBZ = wrl.trafo.idecibel(value)
                lon, lat = wrl.georef.polar2lonlat(rng, azi, (radar_longitude, radar_latitude))

                # realizar los redondeos
                dBZ_value = float("{0:.1f}".format(dBZ))
                latitude_value = float("{0:.5f}".format(lat))
                longitude_value = float("{0:.5f}".format(lon))

                if dBZ_value > 0.0:
                    clean_data.append((dBZ_value, latitude_value, longitude_value))

        for i, (dBZ, lat, lon) in enumerate(sorted(clean_data, key=lambda tup: tup[0])):
            line = "{0:.1f},{1:.5f}:{2:.5f}".format(dBZ, lat, lon)

            file.write(line + "\n")

            cdata += line

            if self.DEBUG == 1:
                print(line)

        file.close()

        end = time.time()

        print(Colors.HEADER + "---" + Colors.ENDC)
        print(Colors.HEADER + "Tamaño Datos Enviados: {0}kb".format(sys.getsizeof(cdata) / 1024) + Colors.ENDC)
        print(Colors.HEADER + "Tiempo de Procesamiento: {0:.1f} minutos".format((end - start) / 60) + Colors.ENDC)

    def correlate_dbz_to_location(self, filename, destination, process_all, layer):
        """
        Esta funcion procesa todo un directorio de archivos y por cada uno realiza la 
        correlacion entre dBZ y sus coordenadas geograficas en el mapa.
        
        Esta función esta diseñada para archivos de modalidad Simple y Doppler.

        Formato del archivo a generar:
        ==============================
        Se genera un archivo *.ama, el cual no es nada mas que un archivo de texto separado por
        lineas, en el cual cada registro a su vez se encuentra separado por comas.

        Ejemplo:
            dBZ,latitude:longitude

        :param filename: El nombre del archivo a procesar.
        :param destination: El nombre del directorio en donde colocar los archivos resultantes.
        :param process_all Procesar todos los archivos en la carpeta donde se encuentra el archivo \
            pasado como *filename*.
        :param layer: La capa de datos a procesar. Cada capa corresponde a un ángulo de elevación del radar.

        :return: void
        """
        if process_all:
            origin = os.path.join(os.environ["WRADLIB_DATA"], os.path.split(filename)[0])
            destination = os.path.join(os.environ["AMA_EXPORT_DATA"], destination)
            matches = Utils.files_for_processing(origin, self.QT, self.FILE_SIZE_LIMIT)

            if len(matches) > 0:
                for item in matches:
                    if Utils.should_process_file(item, self.FILE_SIZE_LIMIT, True):
                        self.single_correlate_dbz_to_location(item, destination, layer)
        else:
            self.single_correlate_dbz_to_location(filename, destination, layer)

    def single_correlate_dbz_to_location_to_json(self, filename, layer):
        """
        Esta funcion realiza la correlacion entre dBZ y sus coordenadas geograficas en el mapa.
        
        Esta función esta diseñada para archivos de modalidad Simple y Doppler.

        Formato del JSON a generar:
        ===========================
        Se genera un texto en formato JSON, el cual no es nada mas que un arreglo en donde cada registro
        es un String separado por comas. Este texto JSON se utiliza para insertar los datos en la base de
        datos vía el Web Service correspondiente.
            Metadatos a enviar:
            ===================
            1. La hora/fecha que corresponde al archivo de los cuales provienen los datos. Generalmente
            esta hora se encuentra en GMT y es manejada por el radar.

        Ejemplo:
            dBZ,latitude:longitude

        :param filename: El nombre del archivo a procesar.
        :param layer: La capa de datos a procesar. Cada capa corresponde a un ángulo de elevación del radar.
        
        :return: void
        """
        try:
            start = time.time()
            cdata = ""
            destination = os.path.join(os.environ["AMA_EXPORT_DATA"], "NoiseData.noise")
            data, metadata = Processor.process(filename)
            clean_data = []
            layer_key = u"SCAN{0}".format(layer)

            file = open(destination, "a")

            radar_latitude = float(metadata["VOL"]["Latitude"])
            radar_longitude = float(metadata["VOL"]["Longitude"])

            for (row, column), value in np.ndenumerate(data[layer_key][u"Z"]["data"]):
                if value > -64.:
                    rng = metadata[layer_key]["r"][column]
                    azi = metadata[layer_key]["az"][row]
                    dBZ = wrl.trafo.idecibel(value)
                    lon, lat = wrl.georef.polar2lonlat(rng, azi, (radar_longitude, radar_latitude))

                    # realizar los redondeos
                    dBZ_value = float("{0:.1f}".format(dBZ))
                    latitude_value = float("{0:.5f}".format(lat))
                    longitude_value = float("{0:.5f}".format(lon))

                    if dBZ_value > 0.0:
                        clean_data.append((dBZ_value, latitude_value, longitude_value))

            # construir el texto JSON.
            # cabecera
            cdata += "{{\"fechaCarga\":\"{0}\",\"arrayDatos\":[".format(metadata[layer_key]["Time"])

            for i, (dBZ, lat, lon) in enumerate(sorted(clean_data, key=lambda tup: tup[0])):
                line = "\"{0:.1f};{1:.5f}:{2:.5f}\",".format(dBZ, lat, lon)

                # si es el último registro remover la coma al final.
                if i == (len(clean_data) - 1):
                    line = line[:-1]

                file.write("{0}\t{1:.1f}\t{2:.5f}\t{3:.5f}\n".format(metadata[layer_key]["Time"], dBZ, lat, lon))

                # cuerpo
                cdata += line

            # pie
            cdata += "]}"

            file.close()

            if self.DEBUG == 1:
                print(cdata)

            # insertar los datos.
            # IMPORTANTE! Añadir timeout de 30 segundos para el pedido.
            url = "http://127.0.0.1:80/ama/insertar"
            headers = {'Content-type': 'application/json'}
            response = requests.post(url, data=cdata, headers=headers, timeout=30)
            if response.status_code != requests.codes.ok:
                print(Colors.FAIL + "\tERROR: Insertando datos en WS." + Colors.ENDC)
            else:
                print(Colors.OKGREEN + "\tINFO: Datos insertados." + Colors.ENDC)

            end = time.time()

            print(Colors.HEADER + "---" + Colors.ENDC)
            print(Colors.HEADER + "Tamaño Datos Enviados: {0}kb".format(sys.getsizeof(cdata) / 1024) + Colors.ENDC)
            print(Colors.HEADER + "Tiempo de Procesamiento: {0:.1f} segundos".format((end - start)) + Colors.ENDC)
        except Exception as e:
            print(Colors.FAIL + "\tERROR: Corriendo trabajo de inserción." + Colors.ENDC)
            print(Colors.FAIL + "\t\tDESC: {0}".format(e) + Colors.ENDC)
        finally:
            # siempre borrar el archivo que fue procesado.
            if self.SHOULD_REMOVE_PROCESSED_FILES == 1:
                try:
                    os.remove(filename)
                except Exception as e:
                    print(Colors.FAIL + "\tERROR: Borrando archivo original." + Colors.ENDC)
                    print(Colors.FAIL + "\t\tDESC: {0}".format(e) + Colors.ENDC)
