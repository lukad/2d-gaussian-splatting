from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import find_packages, setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

HERE = Path(__file__).parent
SUB = HERE / ".." / ".." / "submodules" / "simple-knn"
VENDOR = HERE / "vendor" / "simple-knn"

if VENDOR.exists():
    shutil.rmtree(VENDOR)
VENDOR.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(SUB, VENDOR)


def v(*parts: str) -> str:
    return "/".join(["vendor", "simple-knn", *parts])


ext_modules = [
    CUDAExtension(
        name="simple_knn._C",
        sources=[
            v("spatial.cu"),
            v("simple_knn.cu"),
            v("ext.cpp"),
        ],
        extra_compile_args={
            "nvcc": [],
            "cxx": [],
        },
    )
]

setup(
    name="simple_knn",
    version="0.0.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExtension},
    zip_safe=False,
)
