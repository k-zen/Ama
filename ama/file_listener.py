# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: file_listener
   :platform: Unix
   :synopsis: Funciones útiles para la detección de cambios en directorios. Ej. cuando se agrega un nuevo archivo de radar.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

from watchdog.events import FileSystemEventHandler
from ama.processor import Processor
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


class FileListener(FileSystemEventHandler):
    """
    Manejador de cambios en un directorio previamente establecido.
    """

    def on_created(self, event):
        if Utils.should_process_file(event.src_path, Processor.FILE_SIZE_LIMIT):
            print(Colors.OKGREEN + "\tINFO: Detectado archivo nuevo. Procesando..." + Colors.ENDC)
            print(Colors.OKGREEN + "\t\tARCHIVO: {0}".format(event.src_path) + Colors.ENDC)

            # procesar el archivo.
            Processor().single_correlate_dbz_to_location_to_json(event.src_path, True)
        else:
            print(Colors.FAIL + "\tERROR: El archivo detectado no cumple con los requisitos de procesamiento." + Colors.ENDC)
            print(Colors.FAIL + "\t\tARCHIVO: {0}".format(event.src_path) + Colors.ENDC)
