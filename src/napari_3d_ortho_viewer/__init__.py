try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._dock_widget import OrthoViewerWidget
from ._crop_dock_list_widget import CropListLabelsWidget
from ._crop_dock_widget import CropLabelsWidget

__all__ = (
    "OrthoViewerWidget",
    "CropListLabelsWidget",
    "CropLabelsWidget",
)
