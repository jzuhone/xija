from distutils.core import setup, Extension

long_description = """
Xija (pronounced "kiy - yuh", rhymes with Maya) is the thermal modeling
framework used Chandra thermal modeling:

* Modular and extensible modeling framework
* Single-step integration instead of analytic state-based solutions
* Model definition via Python code or static data structure
* Interactive and iterative model development and fitting
* Predictively model a node or use telemetry during development
* GUI interface for model development
* Matlab interface
"""

from xija.version import version

core6_ext = Extension('xija.core', ['xija/core.c'])

setup(name='xija',
      version=version,
      description='Thermal modeling framework for Chandra',
      long_description=long_description,
      author='Tom Aldcroft',
      author_email='aldcroft@head.cfa.harvard.edu',
      url='https://github.com/sot/xija',
      license='BSD',
      platforms=['any'],
      ext_modules=[core6_ext],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Astronomy',
          'Topic :: Scientific/Engineering :: Physics',
          'Programming Language :: Python :: 2',
          ],
      packages=['xija'],
      package_data={'xija': ['libcore.so']},
      )