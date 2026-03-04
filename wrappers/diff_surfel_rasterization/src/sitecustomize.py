from __future__ import annotations

import importlib


def _inject() -> None:
    try:
        pkg = importlib.import_module("diff_surfel_rasterization")
        api = importlib.import_module("diff_surfel_rasterization._api")
    except Exception:
        # If torch isn't installed yet, extension isn't built, etc.
        # we don't want to break *every* python invocation.
        return

    for name in ("GaussianRasterizationSettings", "GaussianRasterizer"):
        if hasattr(api, name) and not hasattr(pkg, name):
            setattr(pkg, name, getattr(api, name))


_inject()
