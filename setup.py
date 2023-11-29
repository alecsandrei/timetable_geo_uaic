import io
from os import path as op
from setuptools import find_packages
from setuptools import setup


version = '0.0.2'
description = 'A PyQt app where the bachelor students from the University "Alexandru Ioan Cuza" Iași, Faculty of Geography and Geology can view their timetable.'
here = op.abspath(op.dirname(__file__))

with open('README.md') as f:
    long_description = f.read()

with io.open(op.join(here, "requirements.txt"), encoding="utf-8") as f:
    core_reqs = f.read().split("\n")


setup(
    name='timetable_geo_uaic',
    version=version,
    author='Cuvuliuc Alex-Andrei',
    author_email="<cuvuliucalexandrei@gmail.com>",
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/alecsandrei/timetable-geo-uaic',
    packages=find_packages(),
    install_requires=core_reqs,
    keywords=['python', 'pyqt'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
    ],
)
