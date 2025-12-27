"""
Setup script for compiling Cython modules.
Run: python setup_cython.py build_ext --inplace
"""

import numpy
from Cython.Build import cythonize
from setuptools import Extension, setup

extensions = [
    Extension(
        "app.core.audio.audio_processing_cython",
        ["app/core/audio/audio_processing_cython.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=(
            ["/O2"]
            if hasattr(__builtins__, "__import__")
            and hasattr(__builtins__, "__import__")
            else ["-O3"]
        ),
    ),
    Extension(
        "app.core.engines.quality_metrics_cython",
        ["app/core/engines/quality_metrics_cython.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=(
            ["/O2"]
            if hasattr(__builtins__, "__import__")
            and hasattr(__builtins__, "__import__")
            else ["-O3"]
        ),
    ),
]

setup(
    name="VoiceStudio Cython Extensions",
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
    zip_safe=False,
)
