"""cfncli version."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("cfncli")
except PackageNotFoundError:  ## local development
    __version__ = "0.0"
