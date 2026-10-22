from aqt.qt import QBrush, QColor, QFont, QPainter, QPointF, QRectF
from . import appearance, settings, shapes


def build_rows():
    # Each row is a list of (label, shape, colour, size) items. Size is a multiple of LEAF_SIZE.
    interval_row = []
    for days in settings.DEBUG_GALLERY_INTERVALS:
        size = appearance.leaf_size(days)
        interval_row.append((f"{days}d", "leaf", settings.COLOR_MATURE, size))

    size = appearance.leaf_size(settings.DEBUG_GALLERY_COLOR_INTERVAL)
    colours = [
        ("young", settings.COLOR_YOUNG),
        ("mature", settings.COLOR_MATURE),
        ("due", settings.COLOR_DUE),
        ("suspended", settings.COLOR_SUSPENDED),
        ("leech", settings.COLOR_LEECH),
    ]
    colour_row = []
    for name, colour in colours:
        colour_row.append((name, "leaf", colour, size))

    other_row = [
        ("new", "bud", settings.COLOR_NEW, settings.BUD_SIZE_RATIO),
        ("susp.", "bud", settings.COLOR_SUSPENDED, settings.BUD_SIZE_RATIO),
        ("learning", "flower", settings.COLOR_LEARNING, settings.FLOWER_SIZE_RATIO),
        ("relearn", "flower", settings.COLOR_RELEARNING, settings.FLOWER_SIZE_RATIO),
    ]
    return [interval_row, colour_row, other_row]


def item_box(shape, size, zoom):
    # Width and height in px of one item at this zoom level.
    box = shapes.cached_path(shape, size).boundingRect()
    return box.width() * zoom, box.height() * zoom


def paint_gallery(painter):
    if not settings.DEBUG_SHOW_GALLERY:
        return
    pad = settings.DEBUG_GALLERY_PADDING
    rows = build_rows()

    # First pass: work out the cell width and row heights for each zoom level, and the panel size.
    layout = []
    panel_width = 0
    panel_height = pad
    for zoom in settings.DEBUG_GALLERY_ZOOMS:
        widest = settings.DEBUG_GALLERY_MIN_CELL
        heights = []
        for row in rows:
            tallest = 0
            for label, shape, colour, size in row:
                w, h = item_box(shape, size, zoom)
                widest = max(widest, w)
                tallest = max(tallest, h)
            heights.append(tallest)
        cell_width = widest + pad
        layout.append((zoom, cell_width, heights))
        panel_height += 2 * pad + sum(h + 2 * pad for h in heights)
        for row in rows:
            panel_width = max(panel_width, len(row) * cell_width)
    panel_width += 2 * pad
    panel_height += pad

    # Second pass: draw.
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = QFont()
    font.setPixelSize(10)
    painter.setFont(font)

    left = settings.DEBUG_GALLERY_X
    top = settings.DEBUG_GALLERY_Y
    painter.fillRect(QRectF(left, top, panel_width, panel_height),
                     QColor(settings.DEBUG_GALLERY_BACKGROUND))

    y = top + pad
    for zoom, cell_width, heights in layout:
        painter.setPen(QColor("#aaaaaa"))
        painter.drawText(QPointF(left + pad, y + pad), f"zoom x{zoom}")
        y += 2 * pad
        for row, tallest in zip(rows, heights):
            x = left + pad
            for label, shape, colour, size in row:
                painter.setPen(QColor("#dddddd"))
                painter.drawText(QPointF(x, y + tallest + pad), label)
                painter.save()
                painter.translate(x, y + tallest / 2)
                painter.scale(zoom, zoom)
                painter.fillPath(shapes.cached_path(shape, size), QBrush(QColor(colour)))
                painter.restore()
                x += cell_width
            y += tallest + 2 * pad
    painter.restore()
