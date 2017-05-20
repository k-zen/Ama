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
    [--correlate-dbz-location] [-f=filename] [-d=destination] [-l=0] [--all]
    [--show-data] [-t=target]
    [--run] [-t=target] [-l=0]

Opciones:
=========
    --process-reflectivity   procesa un directorio de datos de forma recursiva
                             y genera imagenes de reflectividad
    --process-rainfall       procesa un directorio de datos de forma recursiva
                             y genera imagenes de profundidad de lluvia
    --correlate-dbz-location procesa un archivo de datos y correlaciona dbZ con
                             coordenadas geograficas
    --show-data              muestra los datos en pantalla (DEBUG)
    --run                    lanza un proceso que escucha por el ultimo archivo
                             generado por el radar, y lo procesa

    ---

    -t El PATH al directorio de datos de radar. Tomar en cuenta que se parte siempre
       desde la variable de entorno WRADLIB_DATA
    -d El PATH al directorio donde se guardaran los datos procesados. Tomar en cuenta
       que se parte siempre desde la variable de entorno AMA_EXPORT_DATA
    -f El nombre del archivo a procesar. Tomar en cuenta que se parte siempre
       desde la variable de entorno WRADLIB_DATA
    -l La capa de datos a utilizar. Valores correctos son: 0 hasta 10

    ---

    --all    Procesar todos los archivos en un directorio.

Banderas:
=========
    --help  muestra este mensaje de ayuda
"""

import getopt
import os
import sys
import time

from ama.file_listener import FileListener
from ama.processor import Processor
from ama.show_data import ShowData
from ama.utils import Colors
from watchdog.observers import Observer

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
    print(sys.exit(__doc__))


def main(argv=None):
    command = 0
    target = ""
    destination = ""
    filename = ""
    layer = 0
    process_all = False

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(
                argv[1:],
                "t:d:f:r:",
                [
                    "help",
                    "process-reflectivity",
                    "process-rainfall",
                    "correlate-dbz-location",
                    "show-data",
                    "run",
                    "all"
                ]
            )
            if not opts:
                usage()
        except getopt.error, msg:
            raise Usage(msg)

        # DEBUG:
        # print opts

        for opt, arg in opts:
            if opt == "--help":
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
            elif opt == "-t":
                target = arg
            elif opt == "-d":
                destination = arg
            elif opt == "-f":
                filename = arg
            elif opt == "-l":
                layer = int(arg)
            elif opt == "--all":
                process_all = True

        # tomar la decision.
        if command == 1:
            if not target and not destination:
                print(Colors.FAIL + "\tERROR: Origen y destino no definidos." + Colors.ENDC)
                return 2

            Processor().process_directory_generate_raw_images_from_reflectivity(target, destination)
        elif command == 2:
            if not target and not destination:
                print(Colors.FAIL + "\tERROR: Origen y destino no definidos." + Colors.ENDC)
                return 2

            Processor().process_directory_generate_raw_images_from_rainfall_intensity(target, destination)
        elif command == 3:
            if not filename and not destination:
                print(Colors.FAIL + "\tERROR: Nombre de archivo y destino no definidos." + Colors.ENDC)
                return 2

            Processor().correlate_dbz_to_location(filename, destination, process_all, layer)
        elif command == 4:
            if not target:
                print(Colors.FAIL + "\tERROR: Origen no definido." + Colors.ENDC)
                return 2

            ShowData.show_data(target)
        elif command == 5:
            if not target:
                print(Colors.FAIL + "\tERROR: Origen no definido." + Colors.ENDC)
                return 2

            directory = os.path.join(os.environ["WRADLIB_DATA"], target)
            print(Colors.OKBLUE + "\tINFO: Escuchando por adiciones en {0}.".format(directory) + Colors.ENDC)

            event_handler = FileListener(layer)
            observer = Observer()
            observer.schedule(event_handler, path=directory, recursive=False)
            observer.start()  # lanzar el proceso que observa adiciones en el directorio.
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()  # agregar opcion de parar el observador con Ctrl+C.
            observer.join()
    except Usage, err:
        print(Colors.FAIL + "\tERROR: {0}".format(err.msg) + Colors.ENDC)
        print(Colors.HEADER + "\tINFO: para ayuda utilizar --help" + Colors.ENDC)
        return 2


if __name__ == "__main__":
    sys.exit(main())
