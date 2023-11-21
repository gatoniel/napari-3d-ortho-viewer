"""Widget to crop images around certain labels to introspect them better."""
from typing import Optional, List, Tuple
import napari
import numpy as np
from napari.layers import Labels, Image
from qtpy.QtWidgets import QWidget
from qtpy.QtWidgets import QVBoxLayout
from magicgui.widgets import PushButton
from magicgui.widgets import LineEdit


def str_to_int_list(s: str, delimiter=",") -> List[int]:
    return [int(i) for i in s.split(delimiter) if i.isdigit()]


class CropLabelsWidget(QWidget):
    """A widget that provides cropping functionality based on labels layer."""

    def __init__(self, viewer: napari.Viewer):
        """Initialize widget with viewer."""
        super().__init__()
        labels_layer = [isinstance(layer, Labels) for layer in viewer.layers]
        if not any(labels_layer):
            raise RuntimeError("Crop only possible with labels layer present.")

        self.old_viewer = viewer
        self.crop_viewer: Optional[napari.Viewer] = None

        self.setLayout(QVBoxLayout())

        # add crop button
        self.crop_button = PushButton(name="crop_button", label="Crop")
        self.crop_button.changed.connect(self.button_changed)
        self.layout().addWidget(self.crop_button.native)

        self.padding_field = LineEdit(
            name="padding_field", label="Pad crop", value=2
        )
        self.layout().addWidget(self.padding_field.native)

        self.labels_field = LineEdit(
            name="labels_field", label="Labels to crop"
        )
        self.layout().addWidget(self.labels_field.native)

    def get_slices(self) -> Tuple[slice]:
        from skimage.measure import regionprops

        ndim = self.old_viewer.dims.ndim
        padd = int(self.padding_field.value)
        if padd < 0:
            padd = 0

        try:
            selected_layer = list(self.old_viewer.layers.selection)[0]
        except IndexError:
            selected_layer = self.old_viewer.layers[0]

        if not isinstance(selected_layer, Labels):
            first_labels_layer_ind = [
                isinstance(layer, Labels) for layer in self.old_viewer.layers
            ].index(True)
            selected_layer = self.old_viewer.layers[first_labels_layer_ind]

        labels = selected_layer.data
        selected_labels = [
            int(lbl) for lbl in self.labels_field.value.split(",")
        ]

        selected_area = np.zeros_like(labels, dtype=bool)
        for lbl in selected_labels:
            selected_area = np.logical_or(selected_area, labels == lbl)

        regions = regionprops(selected_area.astype(np.uint8))

        slices = []
        for i in range(ndim):
            bboxes = [region.bbox for region in regions]
            min_ = min([bbox[i] - padd for bbox in bboxes])
            if min_ < 0:
                min_ = 0
            max_ = max([bbox[i + ndim] + padd for bbox in bboxes])
            slices.append(slice(min_, max_))
        return tuple(slices)

    def button_changed(self) -> None:
        """Start cropping when button was clicked."""
        if len(self.labels_field.value.split(",")) > 0:
            new_viewer = napari.Viewer()
            self.add_layers(new_viewer, self.get_slices())

    def add_layers(
        self,
        viewer: napari.Viewer,
        slices: Tuple[slice],
    ) -> None:
        """Copy layers from old_viewer to viewer."""
        for layer in self.old_viewer.layers:
            name = layer.name
            if isinstance(layer, Labels):
                viewer.add_labels(layer.data[slices], name=name)
            if isinstance(layer, Image):
                if layer.data.ndim == len(slices):
                    data = layer.data[slices]
                else:
                    slices = List(slices)
                    slices.append(slice(None, None))
                    data = layer.data[Tuple(slices)]
                viewer.add_image(data, name=name)
