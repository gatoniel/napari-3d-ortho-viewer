"""Test the 3D Ortho viewer widget."""
from collections import namedtuple

import napari
import numpy as np
import pytest

import napari_3d_ortho_viewer

# from qtpy import QtCore

# this is your plugin name declared in your napari.plugins entry point
MY_PLUGIN_NAME = "3D Ortho viewer"
# the name of your widget(s)
MY_WIDGET_NAMES = ["Ortho Viewer Widget"]

DUMMY_IMG = np.ones((100, 100, 100))


@pytest.mark.parametrize("widget_name", MY_WIDGET_NAMES)
def test_dock_to_viewer(widget_name, make_napari_viewer, napari_plugin_manager):
    """Does widget dock to viewer."""
    napari_plugin_manager.register(napari_3d_ortho_viewer, name=MY_PLUGIN_NAME)
    viewer = make_napari_viewer()
    viewer.add_image(DUMMY_IMG)
    num_dw = len(viewer.window._dock_widgets)
    viewer.window.add_plugin_dock_widget(
        plugin_name=MY_PLUGIN_NAME, widget_name=widget_name
    )
    assert len(viewer.window._dock_widgets) == num_dw + 1


@pytest.mark.parametrize("widget_name", MY_WIDGET_NAMES)
def test_runtime_error_with_2dim_img(
    widget_name, make_napari_viewer, napari_plugin_manager
):
    """Does widget dock to viewer."""
    napari_plugin_manager.register(napari_3d_ortho_viewer, name=MY_PLUGIN_NAME)
    viewer = make_napari_viewer()
    viewer.add_image(np.ones((100, 100)))
    with pytest.raises(RuntimeError):
        viewer.window.add_plugin_dock_widget(
            plugin_name=MY_PLUGIN_NAME, widget_name=widget_name
        )


@pytest.mark.parametrize("widget_name", MY_WIDGET_NAMES)
def test_runtime_error_with_no_img(
    widget_name, make_napari_viewer, napari_plugin_manager
):
    """Does widget dock to viewer."""
    napari_plugin_manager.register(napari_3d_ortho_viewer, name=MY_PLUGIN_NAME)
    viewer = make_napari_viewer()
    with pytest.raises(RuntimeError):
        viewer.window.add_plugin_dock_widget(
            plugin_name=MY_PLUGIN_NAME, widget_name=widget_name
        )


@pytest.mark.parametrize("widget_name", MY_WIDGET_NAMES)
def test_checkbox_changed(
    widget_name, make_napari_viewer, napari_plugin_manager, qtbot
):
    """Does widget dock to viewer."""
    napari_plugin_manager.register(napari_3d_ortho_viewer, name=MY_PLUGIN_NAME)
    viewer = make_napari_viewer()
    viewer.add_image(DUMMY_IMG)
    viewer.add_labels(DUMMY_IMG.astype(int))
    dw, widget = viewer.window.add_plugin_dock_widget(
        plugin_name=MY_PLUGIN_NAME, widget_name=widget_name
    )

    widget.checkbox.value = True

    assert isinstance(widget.xy_viewer, napari.Viewer)

    widget.lbl_layers[1].paint((5, 5, 5), 1)

    Event = namedtuple("Event", ["position"])
    event = Event(position=(0.0, 0.0, 0.0))
    widget.mouse_click(widget.xy_viewer, event)

    widget.checkbox.value = False
    assert widget.xy_viewer is None
