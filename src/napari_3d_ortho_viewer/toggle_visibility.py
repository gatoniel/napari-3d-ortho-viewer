"""Synchronize visibility between two layers."""
from napari.layers import Layer


class ToggleTwoVisibleLayers:
    """Toggle visibility between two layers."""

    def __init__(
        self, layer1: Layer, layer2: Layer, inverse: bool = True, visible: bool = True
    ):
        """Inverse describes how vibility between layer1 and layer2 is related."""
        self.layer1 = layer1
        self.layer2 = layer2

        if inverse:
            self.layer1.visible = True
            self.layer2.visible = False
            self.layer1.events.visible.connect(self.toggle_inverse1)
            self.layer2.events.visible.connect(self.toggle_inverse2)
        else:
            raise NotImplementedError("inverse = False is not implemented yet")
            # self.layer1.visible = visible
            # self.layer2.visible = visible
            # self.layer1.events.visible.connect(self.toggle_simultaneous1)
            # self.layer2.events.visible.connect(self.toggle_simultaneous2)

    def toggle_inverse(self, layer1, layer2) -> None:
        """Toggle visibiliy between layer1 and layer2."""
        visible1 = layer1.visible
        visible2 = layer2.visible

        if visible1 and visible2:
            layer2.visible = False
        if not visible1 and not visible2:
            layer2.visible = True

    def toggle_inverse1(self, event=None) -> None:
        """Toggle visibility of self.layer2 based on self.layer1."""
        self.toggle_inverse(self.layer1, self.layer2)

    def toggle_inverse2(self, event=None) -> None:
        """Toggle visibility of self.layer1 based on self.layer2."""
        self.toggle_inverse(self.layer2, self.layer1)
