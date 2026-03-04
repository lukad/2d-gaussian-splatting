# wrappers/diff_surfel_rasterization/setup.py
from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import find_packages, setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

HERE = Path(__file__).parent
SUB = HERE / ".." / ".." / "submodules" / "diff-surfel-rasterization"  # don't resolve()
VENDOR = HERE / "vendor" / "diff-surfel-rasterization"

SRC_PKG = HERE / "src" / "diff_surfel_rasterization"
SUB_PKG = SUB / "diff_surfel_rasterization"  # the python package in submodule

# write _api module
SRC_PKG.mkdir(parents=True, exist_ok=True)
# Copy upstream __init__.py into a non-__init__ module
shutil.copy2(SUB_PKG / "__init__.py", SRC_PKG / "_api.py")

# vendor tree
SRC_PKG.mkdir(parents=True, exist_ok=True)
for p in SUB_PKG.glob("*.py"):
    if p.name == "__init__.py":
        continue
    shutil.copy2(p, SRC_PKG / p.name)

if VENDOR.exists():
    shutil.rmtree(VENDOR)
VENDOR.parent.mkdir(parents=True, exist_ok=True)

# Copy entire dirs
shutil.copytree(SUB / "cuda_rasterizer", VENDOR / "cuda_rasterizer")
shutil.copytree(SUB / "diff_surfel_rasterization", VENDOR / "diff_surfel_rasterization")
shutil.copytree(SUB / "third_party" / "glm", VENDOR / "third_party" / "glm")

# Copy required top-level sources
for f in ["rasterize_points.cu", "rasterize_points.h", "ext.cpp"]:
    shutil.copy2(SUB / f, VENDOR / f)

    hdr = VENDOR / "cuda_rasterizer" / "rasterizer_impl.h"
    txt = hdr.read_text(encoding="utf-8")

    if "<cstdint>" not in txt:
        # Prepend required includes for std::uintptr_t and uint{32,64}_t
        patch = "#include <cstdint>\n#include <cstddef>\n"
        hdr.write_text(patch + txt, encoding="utf-8")


def v(*parts: str) -> str:
    return "/".join(["vendor", "diff-surfel-rasterization", *parts])


ext_modules = [
    CUDAExtension(
        name="diff_surfel_rasterization._C",
        sources=[
            v("cuda_rasterizer", "rasterizer_impl.cu"),
            v("cuda_rasterizer", "forward.cu"),
            v("cuda_rasterizer", "backward.cu"),
            v("rasterize_points.cu"),
            v("ext.cpp"),
        ],
        extra_compile_args={"nvcc": [f"-I{v('third_party', 'glm')}"]},
    )
]

setup(
    name="diff_surfel_rasterization",
    version="0.0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["sitecustomize"],
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExtension},
    zip_safe=False,
)
