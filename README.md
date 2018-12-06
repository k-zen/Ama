# Ama
Ama es una librería de utilidades hecha completamente en Python como parte de mi proyecto de Tesis de Grado para la Universidad Católica de Asunción. Ama realiza inferencias utilizando datos de radar GAMIC generados en el formato binario jerárquico HDF5, los cuales son convertidos a estructuras de datos nativas en Python, [pandas](https://pandas.pydata.org) y [numpy](http://www.numpy.org) utilizando la librería [wradlib](http://wradlib.org).

Ama es una aplicación ejecutable desde la línea de comandos. Para lanzarla ejecutar:

    $ python -m ama

## Ayuda
Para listar la ayuda de Ama, utilizar el siguiente comando::

    $ python -m ama --help

## Funciones
1. **Process Reflectivity:** Procesa un directorio de datos de forma recursiva y genera imágenes con mapas de reflectividad.
1. **Process Rainfall:** Procesa un directorio de datos de forma recursiva y genera imágenes con mapas de profundidad de lluvia.
1. **Correlate dBZ Location:** Procesa un archivo de datos y correlaciona dBZ con coordenadas geográficas.
1. **Show Data:** Muestra los datos en pantalla (DEBUG).
1. **Run:** Lanza un proceso que escucha por el ultimo archivo generado por el radar, lo procesa y lo insertado en una base de datos utilzando un servicio Web como interfaz.
1. **DBSCAN:** Agrupa reflectividades utilizando el algoritmo DBSCAN.

## Sitio Web
1. GitHub (<https://github.com/k-zen/Ama>)
1. Tesis de Grado / UCA (<http://apkc.net/_4>)

## Licencia
> Copyright (c) 2016, Andreas P. Koenzen <akc at apkc.net>
> All rights reserved.
>
> Redistribution and use in source and binary forms, with or without
> modification, are permitted provided that the following conditions are met:
>
> * Redistributions of source code must retain the above copyright notice, this
>   list of conditions and the following disclaimer.
> * Redistributions in binary form must reproduce the above copyright notice,
>   this list of conditions and the following disclaimer in the documentation
>   and/or other materials provided with the distribution.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
> AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
> IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
> ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
> LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
> CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
> SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
> INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
> CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
> ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
> POSSIBILITY OF SUCH DAMAGE.
