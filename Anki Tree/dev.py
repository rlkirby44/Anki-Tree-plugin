import importlib
from . import settings, appearance, shapes, gallery, growth, debug_deck, placement, canopy, overlay


def redraw():
    # Reload the drawing and placement files, rebuild the items on the current tree, repaint. Does not regrow the tree.
    for module in (settings, appearance, shapes, gallery, debug_deck, placement, canopy):
        importlib.reload(module)
    w = overlay.overlay
    w.items = canopy.build(w.nodes)
    print(canopy.report)
    w.update()


def regrow():
    # Reload everything and start a regrow in the background. The new tree appears when it is ready.
    for module in (settings, growth, appearance, shapes, gallery, debug_deck, placement, canopy):
        importlib.reload(module)
    w = overlay.overlay
    w.set_obstacles(w.raw_obstacles)
    print("growing in the background; run dev.report() once the tree has appeared")


def report():
    print(canopy.report)
