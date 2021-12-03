"""Test the toggle visibility class."""
import numpy as np
import pytest

from napari_3d_ortho_viewer.toggle_visibility import ToggleTwoVisibleLayers

IMG = np.ones((10, 10))


def test_visible_after_init(make_napari_viewer):
    """After initialization one layer should be visible=false."""
    viewer = make_napari_viewer()
    layer1 = viewer.add_image(IMG)
    layer2 = viewer.add_image(IMG)

    ToggleTwoVisibleLayers(layer1, layer2)

    assert layer1.visible
    assert not layer2.visible


def test_visible_after_toggle_layer1(make_napari_viewer):
    """Check layer2.visible after layer1.visible changes."""
    viewer = make_napari_viewer()
    layer1 = viewer.add_image(IMG)
    layer2 = viewer.add_image(IMG)

    toggle = ToggleTwoVisibleLayers(layer1, layer2)

    layer1.visible = False
    toggle.toggle_inverse1()
    assert layer2.visible

    layer1.visible = True
    toggle.toggle_inverse1()
    assert not layer2.visible


def test_visible_after_toggle_layer2(make_napari_viewer):
    """Check layer1.visible after layer2.visible changes."""
    viewer = make_napari_viewer()
    layer1 = viewer.add_image(IMG)
    layer2 = viewer.add_image(IMG)

    toggle = ToggleTwoVisibleLayers(layer1, layer2)

    layer2.visible = True
    toggle.toggle_inverse2()
    assert not layer1.visible

    layer2.visible = False
    toggle.toggle_inverse2()
    assert layer1.visible


def test_notimplemented_simultaneous(make_napari_viewer):
    """Test for NotImplementedError when inverse=False."""
    viewer = make_napari_viewer()
    layer1 = viewer.add_image(IMG)
    layer2 = viewer.add_image(IMG)

    with pytest.raises(NotImplementedError):
        ToggleTwoVisibleLayers(layer1, layer2, inverse=False)
