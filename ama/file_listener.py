# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: file_listener
   :platform: Unix
   :synopsis: Funciones útiles para la detección de cambios en directorios. Ej. cuando se agrega un nuevo archivo de radar.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

import ama.utils as utils
import ama.processor as processor
import os
import time

from watchdog.events import FileSystemEventHandler

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
        # dormir la hebra por 15 segundos, para esperar que el archivo sea copiado por completo.
        time.sleep(15)

        print(utils.Colors.BOLD + "INFO: Detectado archivo nuevo. Procesando..." + utils.Colors.ENDC)
        try:
            if utils.Utils.should_process_file(event.src_path, processor.Processor.FILE_SIZE_LIMIT, True):
                print(utils.Colors.BOLD + "ARCHIVO: {0}".format(event.src_path) + utils.Colors.ENDC)
                # procesar el archivo.
                processor.Processor().single_correlate_dbz_to_location_to_json(event.src_path, self.layer)
            else:
                print(utils.Colors.FAIL + "ERROR: El archivo detectado no cumple con los requisitos de procesamiento." + utils.Colors.ENDC)
                print(utils.Colors.FAIL + "ARCHIVO: {0}".format(event.src_path) + utils.Colors.ENDC)
        except Exception as e:
            print(utils.Colors.FAIL + "ERROR: Procesando archivo nuevo." + utils.Colors.ENDC)
            print(utils.Colors.FAIL + "DESC: {0}".format(e) + utils.Colors.ENDC)
        finally:
            # siempre borrar el archivo que fue procesado.
            if processor.Processor.SHOULD_REMOVE_PROCESSED_FILES == 1:
                try:
                    os.remove(event.src_path)
                except Exception as e:
                    print(utils.Colors.FAIL + "ERROR: Borrando archivo original." + utils.Colors.ENDC)
                    print(utils.Colors.FAIL + "DESC: {0}".format(e) + utils.Colors.ENDC)
