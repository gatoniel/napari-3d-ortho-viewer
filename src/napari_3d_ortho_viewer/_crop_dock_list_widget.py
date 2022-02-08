"""Widget to crop images around certain labels to introspect them better."""
from typing import Optional, List, Tuple
import napari
import numpy as np
from napari.layers import Labels, Image
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget
from qtpy.QtWidgets import QVBoxLayout
from magicgui.widgets import PushButton
from magicgui.widgets import LineEdit
from magicgui.widgets import ComboBox
from magicgui.widgets import Select


def str_to_int_list(s: str, delimiter=",") -> List[int]:
    return [int(i) for i in s.split(delimiter) if i.isdigit()]


class CropListLabelsWidget(QWidget):
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

        self.padding_field = LineEdit(name="padding_field", label="Pad crop", value=2)
        self.layout().addWidget(self.padding_field.native)

        # add update id list button
        self.update_button = PushButton(name="update_button", label="Update IDs")
        self.update_button.changed.connect(self.update_ids)
        self.layout().addWidget(self.update_button.native)

        self.id_selection = None
        self.create_id_selection()

    def create_id_selection(self) -> None:
        """Create new id selection."""
        if self.id_selection is not None:
            self.layout().removeWidget(self.id_selection.native)

        self.id_selection = Select(
            name="labels_ids_dropdown", label="Label IDs", choices=self.labels_list()
        )
        self.layout().addWidget(self.id_selection.native)

    def labels_list(self) -> List[int]:
        """Return label ids of labels layer ordered by biggest area first."""
        from skimage.measure import regionprops

        try:
            selected_layer = list(self.old_viewer.layers.selection)[0]
        except IndexError:
            selected_layer = self.old_viewer.layers[0]

        if not isinstance(selected_layer, Labels):
            first_labels_layer_ind = [
                isinstance(layer, Labels) for layer in self.old_viewer.layers
            ].index(True)
            selected_layer = self.old_viewer.layers[first_labels_layer_ind]

        self.regions = regionprops(selected_layer.data)
        area = np.array([reg.area for reg in self.regions])
        labels_list = np.array([reg.label for reg in self.regions])

        sorted_area = np.argsort(area)[::-1]
        sorted_labels = labels_list[sorted_area]

        self.label_id_to_ind = {l: i for l, i in zip(sorted_labels, sorted_area)}

        return list(sorted_labels)

    def update_ids(self) -> None:
        self.create_id_selection()

    def get_slices(self) -> Tuple[slice]:
        ndim = self.old_viewer.dims.ndim
        padd = int(self.padding_field.value)
        if padd < 0:
            padd = 0

        slices = []

        ids_from_labels = [self.label_id_to_ind[j] for j in self.id_selection.value]
        bboxes = [self.regions[j].bbox for j in ids_from_labels]

        for i in range(ndim):
            min_ = min([bbox[i] - padd for bbox in bboxes])
            if min_ < 0:
                min_ = 0
            max_ = max([bbox[i + ndim] + padd for bbox in bboxes])
            slices.append(slice(min_, max_))
        return tuple(slices)

    def button_changed(self) -> None:
        """Start cropping when button was clicked."""
        if len(self.id_selection.value) > 0:
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


@napari_hook_implementation(specname="napari_experimental_provide_dock_widget")
def napari_register_crop_list_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return CropListLabelsWidget
