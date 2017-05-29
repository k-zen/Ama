# -*- coding: utf-8 -*-

"""
Clase perteneciente al módulo de procesamiento de datos e inferencias Ama.

.. module:: show_data
   :platform: Unix
   :synopsis: Funciones útiles para la visualización de datos.

.. moduleauthor:: Andreas P. Koenzen <akc@apkc.net>
"""

import ama.utils as utils
import ama.processor as processor

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
        data, metadata = processor.Processor().process(filename)

        print(utils.Colors.HEADER + "METADATOS" + utils.Colors.ENDC)
        for k in range(0, 11):
            key = u"SCAN{0}".format(k)
            if key in metadata:
                print("Metadata => AZ => Shape: " + str(metadata[key]["az"].shape))
                print("Metadata => R  => Shape: " + str(metadata[key]["r"].shape))
                print("---")

        print(metadata)
        print("")

        print(utils.Colors.HEADER + "DATOS" + utils.Colors.ENDC)
        for k in range(0, 11):
            key = u"SCAN{0}".format(k)
            if key in metadata:
                print("Data => Z  => Shape: " + str(data[u"SCAN0"][u"Z"]["data"].shape))
                print("---")

        print(data)
