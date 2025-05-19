#!/usr/bin/env python3

from distutils.core import setup, Extension

setup(
    name = "pytinicard",
    version = "1.0",
    ext_modules = [Extension("pytinicard", [
            "IntPool.cpp",
            "SatSolver.cpp",
            "PyModuleUtils.cpp",
            "PyTiniCard.cpp",
            "PyTiniCardExtensions.cpp",
            "PyModule.cpp",
            "progressbar/progressbar.c",
            "tinicard_extensions/ExtensionUtils.cpp",
            "tinicard_extensions/VectorRangeSet.cpp"
        ], 
#        extra_compile_args=['-O5'],
#        extra_compile_args=['-g', '-O0', '-std=c++20'],
        extra_compile_args=['-O5', '-Ofast', '-std=c++20'],
#        extra_compile_args=['-O5', '-Ofast', '-std=c++20', "-g"],
#        libraries=['termcap'],
        language="c++",

        )]
    );
