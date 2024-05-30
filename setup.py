from distutils.core import setup
from pathlib import Path
from setuptools import find_namespace_packages

SCRIPTS = sorted([str(fpath) for fpath in Path("./src/scripts").glob("**/*") if fpath.is_file()])

INIT_PATH = Path("src").joinpath("drapi",
                                 "__init__.py")
with open(INIT_PATH) as file:
    for line in file:
        if line.startswith("__version__"):
            VERSION = line.split('"')[1]

setup(name='drapi-lemur',
      package_dir={"": "src"},
      include_package_data=True,
      packages=find_namespace_packages(where="src"),
      scripts=SCRIPTS,
      version=VERSION,
      description='Data Request API for the Integrated Data Repository Research Services of University of Florida.',
      long_description="Data Request API for the Integrated Data Repository Research Services of University of Florida.",
      author='Herman Autore',
      author_email='hf.autore+drapi@gmail.com',
      url='https://github.com/ChemGuy88/hermanCode/archive/refs/tags/v1.0.0.tar.gz',
      keywords=['CTSI',
                'Clinical and Translational Science Institute',
                'IDR',
                'Integrated Data Repository',
                'Integrated Data Repository Research Services',
                'ODSRI',
                'Office of Data Science and Research Implementation',
                'Shands',
                'Sloth 🦥',
                'UF',
                'UF Health',
                'UFHealth',
                'University of Florida'])
