"""
Build script to compile vault.py into a native .pyd binary.
This makes reverse engineering of the obfuscated key fragments significantly harder.

Usage:
    python setup_vault.py build_ext --inplace
    Then copy app/security/vault*.pyd to your dist folder and delete vault.py
"""
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="icescript_vault",
    ext_modules=cythonize(
        "app/security/vault.py",
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
        },
    ),
)
