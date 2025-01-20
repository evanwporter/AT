from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules=cythonize("src/metrics/metrics.pyx", annotate=True, language_level=3),
    include_dirs=[np.get_include()],
    packages=["metrics"],
    package_dir={"metrics": "src/metrics"},
    zip_safe=False,
)

# python setup.py build_ext --inplace
