from setuptools import setup

setup(
    name='Ama',
    version='0.1',
    author='Andreas P. Koenzen',
    author_email='akc@apkc.net',
    packages=['ama'],
    url='http://apkc.net/_4',
    license='LICENSE.txt',
    description='Libreria para procesar datos de radar.',
    long_description=open('README.txt').read(),
    entry_points={'console_scripts': ['ama = ama.__main__:main']},
    install_requires=[
        "wradlib >= 0.9",
        "haversine >= 0.4.5",
        "numpy >= 1.6.1",
        "matplotlib	>= 1.1.0",
        "scipy >= 0.9",
        "h5py >= 2.0.1",
        "netCDF4 >= 1.0",
        "gdal >= 1.9",
        "watchdog >= 0.8.3",
        "requests >= 2.13.0"
    ]
)
