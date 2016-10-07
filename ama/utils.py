# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: ama
   :platform: Unix
   :synopsis: Funciones útiles para el procesamiento de datos de radar.

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

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
        :param file_size_limit: El tamaño máximo de un archivo a procesar.
        Los archivos que sobrepasen el tamaño serán obviados.

        :return: Una lista con todos los archivos a procesar.
        """
        matches = []
        counter = 0

        for filename in os.listdir(origin):
            if filename.endswith('.mvol'):
                full_path = os.path.join(origin, filename)
                relative_path = os.path.relpath(full_path, os.environ['WRADLIB_DATA'])

                if qt != -1:
                    counter += 1

                if os.stat(full_path).st_size < file_size_limit:
                    matches.append(relative_path)

                if qt != -1 and counter >= qt:
                    break

        return matches
