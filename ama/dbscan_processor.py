# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: dbscan_processor
   :platform: Unix
   :synopsis: Detección de clusters de tormenta utilizando el algoritmo DBSCAN.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

import ama.utils as utils
import ama.processor as processor
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import wradlib as wrl

from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from sklearn.cluster import DBSCAN

__author__ = "Andreas P. Koenzen"
__copyright__ = "Copyright 2016, Proyecto de Tesis / Universidad Católica de Asunción."
__credits__ = "Andreas P. Koenzen"
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Andreas P. Koenzen"
__email__ = "akc@apkc.net"
__status__ = "Prototype"


class DBSCANProcessor:
    """
    Detección de clusters de tormenta utilizando el algoritmo DBSCAN.
    
    Valores óptimos Epsilon = 10.0, Densidad = 300
    """

    def __init__(self):
        pass

    ###### OPCIONES DE PROCESAMIENTO ######
    KMS_PER_RADIAN = 6371.0088
    """
    float: La cantidad de kilómetros en un radián. 
    """
    EPSILON = 10. / KMS_PER_RADIAN
    """
    float: El espacio radial o distancia entre puntos. 
    """
    MIN_SAMPLES = 300
    """
    int: La cantidad mínima de puntos para ser considerado un cluster. 
    """
    TESTING_POINTS = 20
    """
    int: La cantidad máxima de puntos a utilizar para las pruebas y verificaciones. 
    """

    def get_centermost_point(self, clusters):
        """
        Función que detecta el centroide para cada cluster de tormenta.

        :param clusters: Un vector con los clusters detectados por DBSCAN.

        :return: Un vector con tuplas de Latitud, Longitud correspondientes a cada centroide.
        """
        result = []

        for cluster in clusters:
            if len(cluster):
                centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
                centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)

                result.append(tuple(centermost_point))

        return result

    def detect_dbz_clusters(self, filename, layer, test=False):
        """
        Función que detecta los clusters de tormenta.

        :param filename: El archivo con datos de Radar a procesar.
        :param layer: La capa de datos a procesar. Cada capa corresponde a un ángulo de elevación del radar.
        :param test: Habilitar modo verificación de datos. En modo verificación se utilizan pocos datos \
            para poder verificar cada uno de los datos.

        :return: matrix = Una matriz de Nx3 con los valores originales. \
            no_noise = Un vector de vectores con todos los puntos detectados como no-ruido. \
            centermost_points = Un vector de tuplas con las coordenadas de los centroides detectados. \
            time = Fecha/hora de los datos. \
            radar = Tupla con las coordenadas del radar.
        """
        data, metadata = processor.Processor.process(filename)
        lat_vector = []
        lon_vector = []
        dBZ_vector = []
        layer_key = u"SCAN{0}".format(layer)

        radar_latitude = float(metadata["VOL"]["Latitude"])
        radar_longitude = float(metadata["VOL"]["Longitude"])

        for (row, column), value in np.ndenumerate(data[layer_key][u"Z"]["data"]):
            if value > -64.:
                rng = metadata[layer_key]["r"][column]
                azi = metadata[layer_key]["az"][row]
                dBZ = value
                lon, lat = wrl.georef.polar2lonlat(rng, azi, (radar_longitude, radar_latitude))

                # realizar los redondeos
                dBZ_value = float("{0:.1f}".format(dBZ))
                latitude_value = float("{0:.5f}".format(lat))
                longitude_value = float("{0:.5f}".format(lon))

                # filtrar los datos.
                if dBZ_value >= processor.Processor.MINIMUM_REFLECTIVITY and dBZ_value <= processor.Processor.MAXIMUM_REFLECTIVITY:
                    lat_vector.append(latitude_value)
                    lon_vector.append(longitude_value)
                    dBZ_vector.append(dBZ_value)

                    if test == 1:
                        if len(lat_vector) > self.TESTING_POINTS:
                            break

        ###### DBSCAN ######
        #
        # Convertir los vectores de latitud, longitud y dBZ a una matriz de Nx3.
        #
        # Ejemplo:
        #   -25.29036 -57.52304 20.0
        #   -25.28811 -57.52302 30.0
        #
        matrix = np.column_stack((lat_vector, lon_vector, dBZ_vector))
        print("")
        print(utils.Colors.BOLD + "### Matriz Latitud-Longitud-dBZ ###" + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "Tamaño: {0}".format(matrix.shape) + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "{0}".format(np.matrix(matrix)) + utils.Colors.ENDC)
        print("")

        #
        # Ejecutar el algoritmo DBSCAN sobre la matriz recién generada, pero los valores
        # deben ser convertidos a radianes para poder aplicar la función haversine sobre cada
        # punto.
        #
        start_time = time.time()
        db = DBSCAN(eps=self.EPSILON, min_samples=self.MIN_SAMPLES, algorithm='ball_tree', metric='haversine').fit(
            np.radians(np.column_stack((lat_vector, lon_vector))))
        cluster_labels = db.labels_
        num_clusters = len(set(cluster_labels))
        end_time = time.time()
        print("")
        print(utils.Colors.BOLD + "### DBSCAN sobre matriz Latitud-Longitud ###" + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "Nro. Puntos: {0}".format(len(matrix)) + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "Nro. Clusteres: {0}".format(num_clusters) + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "Compresión: {0}".format(100 * (1 - float(num_clusters) / len(matrix))) + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "Tiempo: {0} segundos".format(end_time - start_time) + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "Tamaño: {0}".format(cluster_labels.shape) + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "{0}".format(np.array(cluster_labels)) + utils.Colors.ENDC)
        print("")

        clusters = pd.Series([matrix[cluster_labels == n] for n in range(num_clusters)])
        print("")
        print(utils.Colors.BOLD + "### Lista de Clusteres ###" + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "Tamaño: {0}".format(clusters.shape) + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "{0}".format(clusters.to_string()) + utils.Colors.ENDC)
        print("###")
        print(utils.Colors.BOLD + "Clusteres:" + utils.Colors.ENDC)
        for cluster in clusters:
            print(utils.Colors.BOLD + "Tamaño: {0}".format(cluster.shape) + utils.Colors.ENDC)
            print(utils.Colors.BOLD + "{0}".format(cluster) + utils.Colors.ENDC)
        print("")

        #
        # Vector de tuplas con todos los centroides.
        #
        # Ejemplo:
        #   [(-25.29036,-57.52304),...]
        #
        centermost_points = self.get_centermost_point(clusters)
        print("")
        print(utils.Colors.BOLD + "### Centroides ###" + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "Tamaño: {0}".format(len(centermost_points)) + utils.Colors.ENDC)
        print(utils.Colors.BOLD + "{0}".format(centermost_points) + utils.Colors.ENDC)
        print("")

        #
        # Juntar todos los puntos detectados como no-ruido.
        #
        no_noise = []
        for cluster in clusters:
            for row in cluster:
                no_noise.append(row)

        return matrix, no_noise, centermost_points, metadata[layer_key]["Time"], (radar_latitude, radar_longitude)

    def plot_all_points(self, filename, layer, test=False):
        """
        Función que genera un gráfico con los datos detectados por la función DBSCAN.

        :param filename: El archivo con datos de Radar a procesar.
        :param layer: La capa de datos a procesar. Cada capa corresponde a un ángulo de elevación del radar.
        :param test: Habilitar modo verificación de datos. En modo verificación se utilizan pocos datos \
            para poder verificar cada uno de los datos.

        :return: void
        """
        #
        # Datos que retorna el proceso de detección de clusters.
        #
        original, clustered, centroids, time, radar_coordinates = self.detect_dbz_clusters(filename, layer, test)
        if len(clustered) > 0:
            original_lats, original_lons, original_dBZ = zip(*original)
            clustered_lats, clustered_lons, clustered_dBZ = zip(*clustered)
            centroid_lats, centroid_lons, centroid_dBZ = zip(*centroids)

            ###### PLOTEAR ######
            #
            # Aquí ploteamos los datos completos con una capa extra encima donde se
            # muestran los clusteres detectados con sus correpondientes centroides.
            #
            plt.style.use(u'ggplot')
            fig1, ax1 = plt.subplots(figsize=[10, 6])
            original_scatter = ax1.scatter(original_lons, original_lats, c=original_dBZ, alpha=1.0, s=6)
            clustered_scatter = ax1.scatter(clustered_lons, clustered_lats, c='black', alpha=1.0, s=12)
            centroids_scatter = ax1.scatter(centroid_lons, centroid_lats, c='red', edgecolor='None', alpha=0.7, s=120)
            radar_scatter = ax1.scatter(radar_coordinates[1], radar_coordinates[0], c='green', edgecolor='None', alpha=1.0, s=80)
            ax1.set_title(
                u"Reflectividades (dBZ) entre los valores {0} a {1}. Elevación Radar = Capa {2} / {3}".format(
                    processor.Processor.MINIMUM_REFLECTIVITY,
                    processor.Processor.MAXIMUM_REFLECTIVITY,
                    layer + 1,
                    time),
                fontsize=11,
                fontweight="bold",
                y=1.05)
            ax1.set_xlabel('Longitud')
            ax1.set_ylabel('Latitud')
            ax1.legend(
                [original_scatter, clustered_scatter, centroids_scatter, radar_scatter],
                [
                    "dBZ {0} - {1}".format(processor.Processor.MINIMUM_REFLECTIVITY, processor.Processor.MAXIMUM_REFLECTIVITY),
                    "Datos Limpios",
                    "Centroides Clusters",
                    u"Ubicación Radar"
                ],
                loc='upper right')
            plt.show()
        else:
            print(utils.Colors.BOLD + "---" + utils.Colors.ENDC)
            print(utils.Colors.BOLD + "No se detectaron clusters." + utils.Colors.ENDC)
