"""
Package resource access based on ``importlib.resources`` (replaces the
deprecated ``pkg_resources`` API, which is not available in virtual
environments without setuptools).
"""

from __future__ import absolute_import
import os
import pathlib
import sys

try:
    from importlib.resources import files as _files
except ImportError:  # Python < 3.9
    from importlib_resources import files as _files


def package_files(module_name):
    """
    Returns a ``Traversable`` for the directory of the package that contains
    the specified module. This mirrors how ``pkg_resources`` resolved resource
    names for a module: relative to the directory containing the module file.

    :param module_name: The fully qualified name of an imported module or package
    :return: A ``Traversable`` for the package directory
    """
    module = sys.modules[module_name]
    if not hasattr(module, "__path__"):
        # Plain module: resources live next to it in its package
        module_name = module.__package__
    if not module_name:
        # Top-level module (for example a script executed as ``__main__``)
        return pathlib.Path(os.path.dirname(os.path.abspath(module.__file__)))
    return _files(module_name)
