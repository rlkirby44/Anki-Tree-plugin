import os
from aqt import mw
from aqt.deckbrowser import DeckBrowser
from aqt.qt import QPoint, QRectF, QTimer, QWidget, QPainter, QPen, QColor, Qt, QEvent, QLineF
import math
from . import canopy, cards, gallery, growth, settings


with open(os.path.join(os.path.dirname(__file__), "web", "measure.js"), encoding="utf-8") as f:
    MEASURE_JS = f.read()

overlay = None
measure_timer = None


class TreeOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.obstacles = []
        self.raw_obstacles = []
        self.nodes = []
        self.items = []
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        parent.installEventFilter(self)
        self.setGeometry(parent.rect())
        self.raise_()


    def menubar_obstacle(self):
        # One rectangle around the File/Edit/View/Tools/Help items, so branches keep clear of them.
        bar = mw.menuBar()
        if not bar.isVisible():
            return []
        spans = [bar.actionGeometry(action) for action in bar.actions()]
        spans = [r for r in spans if r.width() > 0]
        if not spans:
            return []
        left = min(r.left() for r in spans)
        right = max(r.right() for r in spans)
        corner = self.mapFromGlobal(bar.mapToGlobal(QPoint(left, 0)))
        pad = settings.MENUBAR_BLOCK_PADDING
        return [(corner.x() - pad, corner.y() - pad, right - left + 1 + 2 * pad, bar.height() + 2 * pad)]


    def set_obstacles(self, rects):
        self.raw_obstacles = rects
        self.obstacles = (growth.pad_obstacles(rects)
                          + growth.manual_obstacles(self.width(), self.height())
                          + self.menubar_obstacle())
        if not self.isVisible():
            return
        canopy.start_growth(self.width(), self.height(), self.obstacles, self.set_tree)

    def set_tree(self, nodes):
        self.nodes = nodes
        self.items = canopy.build(nodes)
        self.update()

    def eventFilter(self, obj, event):
        if obj is self.parent() and event.type() == QEvent.Type.Resize:
            self.setGeometry(self.parent().rect())
            self.raise_()
            schedule_measure()
        return False
    def paintEvent(self, event):
        painter = QPainter(self)
        if settings.DEBUG_SHOW_OBSTACLES:
            for x, y, w, h in self.obstacles:
                painter.fillRect(QRectF(x, y, w, h), QColor(0, 0, 255, 90))

        if settings.DEBUG_SHOW_FIELD:
            w, h = self.width(), self.height()
            for gx in range(0, w, 20):
                for gy in range(0, h, 20):
                    fx, fy = growth.push_from_boundaries(gx, gy, w, h, self.obstacles)
                    strength = min(1.0, math.hypot(fx, fy))
                    if strength > 0.01:
                        painter.fillRect(gx - 2, gy - 2, 4, 4,
                                         QColor(255, 140, 0, int(60 + 195 * strength)))

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for node in self.nodes:
            if node.parent is not None:
                tree_pen = QPen(QColor(110, 70, 30))
                tree_pen.setWidthF(node.display_width)
                tree_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(tree_pen)
                painter.drawLine(QLineF(node.parent.x, node.parent.y, node.x, node.y))

        canopy.paint(painter, self.items)

        if settings.DEBUG_SHOW_OUTLINE:
            pen = QPen(QColor("red"))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawRect(self.rect().adjusted(1, 1, -2, -2))

        gallery.paint_gallery(painter)


def create_overlay():
    global overlay, measure_timer
    overlay = TreeOverlay(mw)
    overlay.setVisible(mw.state == "deckBrowser")
    measure_timer = QTimer()
    measure_timer.setSingleShot(True)
    measure_timer.timeout.connect(measure_obstacles)


def to_overlay_coords(view, rects):
    origin = overlay.mapFromGlobal(view.mapToGlobal(QPoint(0, 0)))
    zoom = view.zoomFactor()

    left, top = origin.x(), origin.y()
    right, bottom = left + view.width(), top + view.height()

    clipped = []
    for r in rects:
        x1 = max(left, origin.x() + r["x"] * zoom)
        y1 = max(top, origin.y() + r["y"] * zoom)
        x2 = min(right, origin.x() + (r["x"] + r["w"]) * zoom)
        y2 = min(bottom, origin.y() + (r["y"] + r["h"]) * zoom)
        if x2 > x1 and y2 > y1:
            clipped.append((x1, y1, x2 - x1, y2 - y1))
    return clipped


def measure_obstacles():
    if overlay is None or not overlay.isVisible():
        return
    views = [mw.web, mw.toolbar.web, mw.bottomWeb]
    results = [None] * len(views)

    def make_callback(index, view):
        def on_result(rects):
            results[index] = to_overlay_coords(view, rects or [])
            if all(r is not None for r in results):
                overlay.set_obstacles([rect for part in results for rect in part])
        return on_result

    for i, view in enumerate(views):
        view.evalWithCallback(MEASURE_JS, make_callback(i, view))


def schedule_measure():
    if measure_timer is not None:
        measure_timer.start(300)


def create_overlay():
    global overlay, measure_timer
    overlay = TreeOverlay(mw)
    overlay.setVisible(mw.state == "deckBrowser")
    measure_timer = QTimer()
    measure_timer.setSingleShot(True)
    measure_timer.timeout.connect(measure_obstacles)


def refresh_data():
    # Reload the card snapshot for Anki's current deck. Does nothing while no collection is open.
    if mw.col is None:
        return
    cards.refresh_cards()


def on_state_change(new_state, old_state):
    if overlay is not None:
        overlay.setVisible(new_state == "deckBrowser")
        overlay.raise_()
        if new_state == "deckBrowser":
            refresh_data()
            schedule_measure()
        else:
            canopy.cancel()


def on_js_message(handled, message, context):
    if message == "tree_changed" and isinstance(context, DeckBrowser):
        schedule_measure()
        return (True, None)
    return handled


def on_deck_browser_render(deck_browser):
    refresh_data()
    schedule_measure()
