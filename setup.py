#!/usr/bin/env python3

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

from pumila.info import program as p

cython_files = ('generate', 'primitives')
ext_modules = [Extension('pumila.{}'.format(f), ['pumila/{}.pyx'.format(f)])
               for f in cython_files]

setup(
    name=p.name,
    version=p.version.text,
    author=p.author,
    author_email=p.author_email,
    url=p.url,
    description=p.description,
    long_description=open('README.txt').read(),
    license=p.short_license_name,
    packages=['pumila'],
    scripts=['scripts/pumila'],
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'License :: DFSG approved',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.1',
                 'Programming Language :: Cython',
                 'Environment :: Console',
                 'Topic :: Utilities',
                 'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis',
                 ])
