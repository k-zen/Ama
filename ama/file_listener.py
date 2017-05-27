# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: file_listener
   :platform: Unix
   :synopsis: Funciones útiles para la detección de cambios en directorios. Ej. cuando se agrega un nuevo archivo de radar.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

import os
import time

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

    layer = 0
    """
    int: La capa de datos a procesar.
    """

    def __init__(self, layer):
        self.layer = layer

    def on_created(self, event):
        # dormir la hebra por 45 segundos, para esperar que el archivo sea copiado por completo.
        time.sleep(45)

        print(Colors.OKGREEN + "\tINFO: Detectado archivo nuevo. Procesando..." + Colors.ENDC)
        if Utils.should_process_file(event.src_path, Processor.FILE_SIZE_LIMIT, True):
            print(Colors.OKGREEN + "\t\tARCHIVO: {0}".format(event.src_path) + Colors.ENDC)
            # procesar el archivo.
            Processor().single_correlate_dbz_to_location_to_json(event.src_path, self.layer)
        else:
            print(Colors.FAIL + "\tERROR: El archivo detectado no cumple con los requisitos de procesamiento." + Colors.ENDC)
            print(Colors.FAIL + "\t\tARCHIVO: {0}".format(event.src_path) + Colors.ENDC)
            # siempre borrar el archivo que fue procesado.
            if Processor.SHOULD_REMOVE_PROCESSED_FILES == 1:
                try:
                    os.remove(event.src_path)
                except Exception as e:
                    print(Colors.FAIL + "\tERROR: Borrando archivo original." + Colors.ENDC)
                    print(Colors.FAIL + "\t\tDESC: {0}".format(e) + Colors.ENDC)
