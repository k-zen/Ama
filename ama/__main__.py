# -*- coding: utf-8 -*-

"""
==------------------------------------------==
==               Ama v0.1                   ==
==          http://apkc.net/_4              ==
== Autor: Andreas P. Koenzen <akc@apkc.net> ==
==------------------------------------------==
Uso:
====
ama [--process-reflectivity] [-t=target] [-d=destination]
    [--process-rainfall] [-t=target] [-d=destination]
    [--correlate-dbz-location] [-f=filename] [-d=destination]
    [--show-data] [-t=target]
    [--run]

Opciones:
=========
    --process-reflectivity      procesa un directorio de datos de forma recursiva
                                y genera imagenes de reflectividad
    --process-rainfall          procesa un directorio de datos de forma recursiva
                                y genera imagenes de profundidad de lluvia
    --correlate-dbz-location    procesa un archivo de datos y correlaciona dbZ con
                                coordenadas geograficas
    --show-data                 muestra los datos en pantalla (DEBUG)
    --run                       lanza un proceso que escucha por el ultimo archivo
                                generado por el radar, lo procesa y envia los datos
                                al servidor *devel.apkc.net*

    ---

    -t  El PATH al directorio de datos de radar. Tomar en cuenta que se parte siempre
        desde la variable de entorno WRADLIB_DATA
    -d  El PATH al directorio donde se guardaran los datos procesados. Tomar en cuenta
        que se parte siempre desde la variable de entorno AMA_EXPORT_DATA
    -f  El nombre del archivo a procesar. Tomar en cuenta que se parte siempre
        desde la variable de entorno WRADLIB_DATA

Banderas:
=========
    --help  muestra este mensaje de ayuda
"""

import getopt
import sys

from ama.processor import Processor
from ama.show_data import ShowData
from ama.utils import Colors

__author__ = "Andreas P. Koenzen"
__copyright__ = "Copyright 2016, Proyecto de Tesis / Universidad Católica de Asunción."
__credits__ = "Andreas P. Koenzen"
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Andreas P. Koenzen"
__email__ = "akc@apkc.net"
__status__ = "Prototype"


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def usage():
    print sys.exit(__doc__)


def main(argv=None):
    command = 0
    target = ""
    destination = ""
    filename = ""

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(
                argv[1:],
                "t:d:f",
                [
                    "help",
                    "process-reflectivity",
                    "process-rainfall",
                    "correlate-dbz-location",
                    "show-data",
                    "run",
                ]
            )
            if not opts:
                usage()
        except getopt.error, msg:
            raise Usage(msg)

        for opt, arg in opts:
            if opt == '--help':
                usage()
            elif opt == "--process-reflectivity":
                command = 1
            elif opt == "--process-rainfall":
                command = 2
            elif opt == "--correlate-dbz-location":
                command = 3
            elif opt == "--show-data":
                command = 4
            elif opt == "--run":
                command = 5
                # TODO Agregar soporte para escuchar por ultimo archivo.
            elif opt == "-t":
                target = arg
            elif opt == "-d":
                destination = arg
            elif opt == "-f":
                filename = arg

        # tomar la decision.
        if command == 1:
            if not target and not destination:
                print Colors.FAIL + "\tERROR: Origen y destino no definidos." + Colors.ENDC
                return 2
            Processor().process_directory_generate_raw_images_from_reflectivity(target, destination)
        elif command == 2:
            if not target and not destination:
                print Colors.FAIL + "\tERROR: Origen y destino no definidos." + Colors.ENDC
                return 2
            Processor().process_directory_generate_raw_images_from_rainfall_intensity(target, destination)
        elif command == 3:
            if not filename and not destination:
                print Colors.FAIL + "\tERROR: Nombre de archivo y destino no definidos." + Colors.ENDC
                return 2
            Processor().correlate_dbz_to_location(filename, destination)
        elif command == 4:
            if not target:
                print Colors.FAIL + "\tERROR: Origen no definido." + Colors.ENDC
                return 2
            ShowData.show_data(target)
    except Usage, err:
        print >> sys.stderr, Colors.FAIL + "\tERROR: {0}".format(err.msg) + Colors.ENDC
        print >> sys.stderr, Colors.HEADER + "\tINFO: para ayuda utilizar --help" + Colors.ENDC
        return 2


if __name__ == "__main__":
    sys.exit(main())
