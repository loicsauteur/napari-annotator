try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from ._dock_widget import Annotator

__all__ = ("Annotator",)
