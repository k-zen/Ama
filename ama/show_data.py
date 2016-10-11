# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: show_data
   :platform: Unix
   :synopsis: Funciones útiles para la visualización de datos.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

from ama.processor import Processor
from ama.utils import Colors

__author__ = "Andreas P. Koenzen"
__copyright__ = "Copyright 2016, Proyecto de Tesis / Universidad Católica de Asunción."
__credits__ = "Andreas P. Koenzen"
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Andreas P. Koenzen"
__email__ = "akc@apkc.net"
__status__ = "Prototype"


class ShowData:
    """
    Clase para mostrar datos en pantalla.
    """

    def __init__(self):
        pass

    @staticmethod
    def show_data(filename):
        """
        Imprime en pantalla los datos de radar, a modo de informacion.

        :param filename: El nombre del archivo a procesar.

        :return: void
        """
        data, metadata = Processor().process(filename)

        print Colors.HEADER + "METADATOS" + Colors.ENDC
        print "Metadata => AZ => Shape: " + str(metadata[u'SCAN0']['az'].shape)
        print "Metadata => R  => Shape: " + str(metadata[u'SCAN0']['r'].shape)
        print "---"
        print metadata
        print ""
        print Colors.HEADER + "DATOS" + Colors.ENDC
        print "Data => Z  => Shape: " + str(data[u'SCAN0'][u'Z']['data'].shape)
        print "---"
        print data
