"""Widget to start / stop 3D Ortho viewer."""
from typing import List
from typing import Optional

import napari
from napari_plugin_engine import napari_hook_implementation
import numpy as np
from magicgui.widgets import Checkbox
from napari.layers import Image
from napari.layers import Labels
from qtpy.QtWidgets import QVBoxLayout
from qtpy.QtWidgets import QWidget

from .toggle_visibility import ToggleTwoVisibleLayers

# from napari.layers.utils._link_layers import link_layers
# from napari.layers.utils._link_layers import unlink_layers
# from qtpy.QtWidgets import QDesktopWidget


class OrthoViewerWidget(QWidget):
    """Widget to organize the ortho viewer."""

    def __init__(self, viewer: napari.Viewer):
        """Initialize widget with viewer and empty variables."""
        super().__init__()
        if not viewer.dims.ndim == 3:
            raise RuntimeError("Ortho view only possible with 3 dimensions!")

        # Old viewer will be used as 3d viewer
        self.old_viewer = viewer

        self.shape = tuple(int(r[1]) for r in self.old_viewer.dims.range)

        self.xy_viewer: Optional[napari.Viewer] = None
        self.yz_viewer: Optional[napari.Viewer] = None
        self.xz_viewer: Optional[napari.Viewer] = None

        self.lbl_layers: List[Labels] = []
        self.img_layers: List[Image] = []
        self.sliced_img_layers: List[Image] = []
        self.toggle_img_layers: List[ToggleTwoVisibleLayers] = []
        self.old_len_undo_histories: Optional[int] = None

        self.setLayout(QVBoxLayout())
        self.checkbox = Checkbox(text="Start/Stop Ortho View")
        self.checkbox.changed.connect(self.checkbox_changed)
        self.layout().addWidget(self.checkbox.native)

    def checkbox_changed(self, event=None) -> None:
        """Either start or stop 3D Ortho viewer."""
        if self.checkbox.value:
            self.start_ortho_viewer()
        else:
            self.delete_viewer(self.xy_viewer)
            self.delete_viewer(self.yz_viewer)
            self.delete_viewer(self.xz_viewer)
            self.xy_viewer = None
            self.yz_viewer = None
            self.xz_viewer = None

            self.delete_named_layer(self.old_viewer, "slicing plane")
            self.delete_named_layer(self.old_viewer, "slicing lines")
            for layer in self.sliced_img_layers:
                self.delete_named_layer(self.old_viewer, layer.name)

            self.lbl_layers.clear()
            self.img_layers.clear()
            self.sliced_img_layers.clear()
            self.toggle_img_layers.clear()

    @staticmethod
    def delete_viewer(viewer: napari.Viewer) -> None:
        """Disconnect layers and close viewer."""
        # for layer in viewer.layers:
        #     unlink_layers([layer])
        viewer.dims.events.current_step.disconnect()
        viewer.close()

    @staticmethod
    def delete_named_layer(viewer: napari.Viewer, name: str) -> None:
        """Remove layer from viewer based on name."""
        layer_names = [layer.name for layer in viewer.layers]
        viewer.layers.pop(layer_names.index(name))

    def add_slicing(self, viewer: napari.Viewer, name: str = "slicing") -> None:
        """Add labels layer initialized with zeros of same shape."""
        return viewer.add_labels(np.zeros(self.shape, dtype=int), name=name)

    def add_layers(
        self,
        viewer: napari.Viewer,
    ) -> None:
        """Copy layers from old_viewer to viewer."""
        for layer in self.old_viewer.layers:
            data = layer.as_layer_data_tuple()
            name = data[1]["name"]
            if not (name.startswith("slicing") or name.startswith("sliced")):
                new_layer = viewer._add_layer_from_data(*data)[0]
                # change contour of copied lbl layers
                if isinstance(layer, Labels):
                    new_layer.contour = 1

    def prepare_old_viewer(self) -> None:
        """Find lbl and img layers and add sliced img layer."""
        for layer in self.old_viewer.layers:
            layer.refresh()
            if isinstance(layer, Labels):
                layer.events.set_data.connect(self.refresh_on_set_data)
                self.lbl_layers.append(layer)
            if isinstance(layer, Image):
                self.img_layers.append(layer)

        for layer in self.img_layers:
            name = f"sliced {layer.name}"
            new_layer = self.old_viewer.add_image(
                np.zeros_like(layer.data), name=name, rendering="iso"
            )
            toggle = ToggleTwoVisibleLayers(layer, new_layer)
            self.sliced_img_layers.append(new_layer)
            self.toggle_img_layers.append(toggle)

    def create_other_viewers(self) -> None:
        """Create ortho viewers and populate them with copied layers."""
        self.xy_viewer = napari.Viewer(title="Ortho view 3d | xy | middle")
        self.add_layers(self.xy_viewer)
        self.yz_viewer = napari.Viewer(title="Ortho view 3d | yz | side")
        self.add_layers(self.yz_viewer)
        self.xz_viewer = napari.Viewer(title="Ortho view 3d | xz | bottom")
        self.add_layers(self.xz_viewer)

    def add_slicing_layers(self) -> None:
        """Add a slicing layer per viewer to indicate current position in volume."""
        self.xy_slicing = self.add_slicing(self.xy_viewer)
        self.yz_slicing = self.add_slicing(self.yz_viewer)
        self.xz_slicing = self.add_slicing(self.xz_viewer)

        self.vol_slicing_plane = self.add_slicing(self.old_viewer, name="slicing plane")
        self.vol_slicing_lines = self.add_slicing(self.old_viewer, name="slicing lines")
        self.toggle_vol_slicing = ToggleTwoVisibleLayers(
            self.vol_slicing_plane, self.vol_slicing_lines
        )
        # by default select not the slicing layers
        for v in [self.xy_viewer, self.yz_viewer, self.xz_viewer]:
            v.layers.selection = [v.layers[-2]]
        self.old_viewer.layers.selection = [self.old_viewer.layers[-3]]

    def orient_all_viewers(self) -> None:
        """First reset current_step and then roll some views accordingly."""
        for v in [self.old_viewer, self.xy_viewer, self.yz_viewer, self.xz_viewer]:
            ndim = v.dims.ndim
            v.dims.current_step = (0,) * ndim
            v.dims.order = tuple(range(ndim))

        self.old_viewer.dims.ndisplay = 3

        self.yz_viewer.dims._roll()
        self.yz_viewer.dims._transpose()

        self.xz_viewer.dims._roll()
        self.xz_viewer.dims._roll()
        self.xz_viewer.dims._transpose()

    def maximize(self) -> None:
        """Show all viewer windows at corrent positions on Desktop."""
        # geom = QDesktopWidget().availableGeometry()
        # print(geom)

        # total_height = geom.height()
        # # This seems to be a constant
        # top = 31
        # height = (total_height - 2 * top) // 2
        # width = (geom.width() - 4) // 2

        # xy_geom = (1, top, width, height)
        # yz_geom = (3 + width, top, width, height)
        # xz_geom = (1, 2 * top + height, width, height)
        # old_geom = (3 + width, 2 * top + height, width, height)
        top = 31
        width = 1278
        height = 665
        xy_geom = (1, top, width, height)
        yz_geom = (3 + width, top, width, height)
        xz_geom = (1, 2 * top + height, width, height)
        old_geom = (3 + width, 2 * top + height, width, height)

        for v, g in zip(
            [self.xy_viewer, self.yz_viewer, self.xz_viewer, self.old_viewer],
            [xy_geom, yz_geom, xz_geom, old_geom],
        ):
            w = v.window._qt_window
            w.setGeometry(*g)

    def start_ortho_viewer(self) -> None:
        """Start the 3D Ortho viewer."""
        # this is needed to avoid errors and warnings if the old viewer is in 3d mode
        self.old_viewer.dims.ndisplay = 2

        self.prepare_old_viewer()

        self.create_other_viewers()

        # Initialize this variable after all viewers have been created
        self.old_len_undo_histories = self.len_undo_histories()

        self.add_slicing_layers()

        self.orient_all_viewers()

        self.maximize()

        # connect the update step to synchronize viewers
        self.z_ind = 0
        self.y_ind = 0
        self.x_ind = 0
        for v in [self.xy_viewer, self.yz_viewer, self.xz_viewer]:
            v.dims.events.current_step.connect(self.update_all)

        # display changes in the lbl layers in all viewers and connect double clicks
        for v in [self.xy_viewer, self.yz_viewer, self.xz_viewer, self.old_viewer]:
            v.mouse_double_click_callbacks.append(self.mouse_click)
            for layer in v.layers:
                name = layer.name
                if not name.startswith("slicing"):
                    if isinstance(layer, Labels):
                        layer.events.set_data.connect(self.refresh_on_set_data)
                        self.lbl_layers.append(layer)

        self.update_all()

    def len_undo_histories(self) -> int:
        """Calculate the length of all undo histories of all lbl layers."""
        return sum(len(layer._undo_history) for layer in self.lbl_layers)

    def refresh_on_set_data(self, event=None) -> None:
        """Refresh lbl layers in all viewers when lbl layer was changed."""
        # source = event.sources[0]
        len_history = self.len_undo_histories()
        if len_history != self.old_len_undo_histories:
            self.old_len_undo_histories = len_history
            for layer in self.lbl_layers:
                layer.refresh()
            # print(event.sources)
            # print(self.current_sources)
            # print(len(self.current_sources), len(self.lbl_layers))
            # if source not in self.current_sources:
            #     print("not in", event.sources)
            #     self.current_sources.append(source)
            #     i = (self.lbl_layers.index(source) + 1) % len(self.lbl_layers)
            #     print(f"refreshing {i}")
            #     self.lbl_layers[i].refresh()
            # if len(self.current_sources) == len(self.lbl_layers):
            #     print("clearing")
            #     self.current_sources.clear()

    def update_all(self, event=None) -> None:
        """Update the slicing layers."""
        z_ind = self.xy_viewer.dims.current_step[0]
        y_ind = self.xz_viewer.dims.current_step[1]
        x_ind = self.yz_viewer.dims.current_step[2]

        # volume slicing via planes
        self.vol_slicing_plane.data[self.z_ind, ...] = 0
        self.vol_slicing_plane.data[:, self.y_ind, :] = 0
        self.vol_slicing_plane.data[..., self.x_ind] = 0

        self.vol_slicing_plane.data[z_ind, ...] = 1
        self.vol_slicing_plane.data[:, y_ind, :] = 2
        self.vol_slicing_plane.data[..., x_ind] = 3

        # volume slicing via lines
        self.vol_slicing_lines.data[self.z_ind, self.y_ind, :] = 0
        self.vol_slicing_lines.data[self.z_ind, :, self.x_ind] = 0
        self.vol_slicing_lines.data[:, self.y_ind, self.x_ind] = 0

        self.vol_slicing_lines.data[z_ind, y_ind, :] = 1
        self.vol_slicing_lines.data[z_ind, :, x_ind] = 2
        self.vol_slicing_lines.data[:, y_ind, x_ind] = 3

        # slicing in ortho views
        self.xy_slicing.data[:, self.y_ind, :] = 0
        self.xy_slicing.data[..., self.x_ind] = 0
        self.xy_slicing.data[:, y_ind, :] = 2
        self.xy_slicing.data[..., x_ind] = 3

        self.yz_slicing.data[self.z_ind, ...] = 0
        self.yz_slicing.data[:, self.y_ind, :] = 0
        self.yz_slicing.data[z_ind, ...] = 1
        self.yz_slicing.data[:, y_ind, :] = 2

        self.xz_slicing.data[self.z_ind, ...] = 0
        self.xz_slicing.data[..., self.x_ind] = 0
        self.xz_slicing.data[z_ind, ...] = 1
        self.xz_slicing.data[..., x_ind] = 3

        for layer, sl_layer in zip(self.img_layers, self.sliced_img_layers):
            sl_layer.data[self.z_ind, ...] = 0
            sl_layer.data[:, self.y_ind, :] = 0
            sl_layer.data[..., self.x_ind] = 0

            sl_layer.data[z_ind, ...] = layer.data[z_ind, ...]
            sl_layer.data[:, y_ind, :] = layer.data[:, y_ind, ...]
            sl_layer.data[..., x_ind] = layer.data[..., x_ind]

            sl_layer.refresh()

        for s in [
            self.vol_slicing_lines,
            self.vol_slicing_plane,
            self.xy_slicing,
            self.xz_slicing,
            self.yz_slicing,
        ]:
            s.refresh()

        self.z_ind = z_ind
        self.y_ind = y_ind
        self.x_ind = x_ind

    def mouse_click(self, viewer, event):
        """Change current step of other viewers on mouse click."""
        data_coordinates = viewer.layers[0].world_to_data(event.position)
        coords = np.round(data_coordinates).astype(int)

        for i, c in enumerate(coords):
            self.xy_viewer.dims.set_current_step(i, c)
            self.yz_viewer.dims.set_current_step(i, c)
            self.xz_viewer.dims.set_current_step(i, c)


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return OrthoViewerWidget
