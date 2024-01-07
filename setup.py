from distutils.core import setup
from setuptools import find_packages

setup(name='drapiPackage',
      packages=find_packages(include="drapiPackage/*"),
      version='1.0.0',
      description='Data Request API for the Integrated Data Repository Research Services of University of Florida.',
      author='Herman Autore',
      author_email='hf.autore+drapi@gmail.com',
      url='https://github.com/ChemGuy88/hermanCode/archive/refs/tags/v1.0.0.tar.gz',
      download_url='download link you saved',
      keywords=['CTSI',
                'Clinical and Translational Science Institute',
                  'IDR',
                  'Integrated Data Repository',
                  'Integrated Data Repository Research Services',
                  'ODSRI',
                  'Office of Data Science and Research Implementation',
                  'Shands',
                  'Sloth',
                  'UF',
                  'UF Health',
                  'UFHealth',
                  'University of Florida'],
      classifiers=[]
      )
