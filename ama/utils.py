# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: utils
   :platform: Unix
   :synopsis: Funciones útiles varias.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

import os

__author__ = "Andreas P. Koenzen"
__copyright__ = "Copyright 2016, Proyecto de Tesis / Universidad Católica de Asunción."
__credits__ = "Andreas P. Koenzen"
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Andreas P. Koenzen"
__email__ = "akc@apkc.net"
__status__ = "Prototype"


class Colors:
    """
    Clase de colores para la terminal.
    """

    def __init__(self):
        pass

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Utils:
    """
    Clase utilitaria.
    """

    def __init__(self):
        pass

    @staticmethod
    def files_for_processing(origin, qt, file_size_limit):
        """
        Procesa un directorio y devuelve todos los archivos que deben ser
        procesados. Esta función devuelve los archivos de forma relativa
        desde la variable de entorno WRADLIB_DATA.

        :param origin:          El directorio origen de datos.
        :param qt:              La cantidad de archivos a procesar.
        :param file_size_limit: El tamaño máximo de un archivo a procesar. \
            Los archivos que sobrepasen el tamaño serán obviados.

        :return: Una lista con todos los archivos a procesar.
        """
        matches = []
        counter = 0

        for filename in os.listdir(origin):
            if filename.endswith(".mvol"):
                if qt != -1 and counter >= qt:
                    break

                full_path = os.path.join(origin, filename)
                relative_path = os.path.relpath(full_path, os.environ["WRADLIB_DATA"])

                if os.stat(full_path).st_size < file_size_limit:
                    if qt != -1:
                        counter += 1

                    matches.append(relative_path)

        return matches

    @staticmethod
    def deduplicate_correlated_data(ri, lat, lon, data):
        for i, (r, la, lo) in enumerate(data):
            if la == lat and lo == lon:
                print(Colors.WARNING + "Dato duplicado => RI={0:.2f}={1:.2f} Lat={2:.5f}={3:.5f} Long={4:.5f}={5:.5f}".format(
                    r, ri, la, lat, lo, lon) + Colors.ENDC)
                return False

        return True
