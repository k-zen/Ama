# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: file_listener
   :platform: Unix
   :synopsis: Funciones útiles para la detección de cambios en directorios. Ej. cuando se agrega un nuevo archivo de radar.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

from watchdog.events import FileSystemEventHandler
from ama.utils import Colors

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
        print(Colors.OKGREEN + "\tINFO: Detectado archivo nuevo: {0}".format(event.src_path) + Colors.ENDC)
