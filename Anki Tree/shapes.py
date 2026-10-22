import math
from aqt.qt import QPainterPath, QPainterPathStroker, QTransform, Qt
from . import settings

# Finished shapes, so each distinct one is built only once.
_cache = {}


def leaf_outline(length, half_width):
    # Plain leaf outline: base at (0, 0), tip at (length, 0), widest part half_width above and below.
    near = settings.LEAF_CONTROL_NEAR * length
    far = settings.LEAF_CONTROL_FAR * length
    handle = half_width * 4 / 3
    path = QPainterPath()
    path.moveTo(0, 0)
    path.cubicTo(near, -handle, far, -handle, length, 0)
    path.cubicTo(far, handle, near, handle, 0, 0)
    path.closeSubpath()
    return path


def leaf_path(size):
    # One leaf of the given size (1.0 = LEAF_SIZE long), with the veins cut out.
    length = size * settings.LEAF_SIZE
    half_width = length * settings.LEAF_WIDTH_RATIO / 2
    leaf = leaf_outline(length, half_width)

    veins = QPainterPath()
    veins.moveTo(0, 0)
    veins.lineTo(length, 0)
    angle = math.radians(settings.VEIN_LATERAL_ANGLE)
    side_veins = sum(1 for threshold in settings.VEIN_SIZE_THRESHOLDS if size >= threshold)
    for i in range(side_veins):
        side = settings.VEIN_LATERAL_SIDES[i]
        start_x = settings.VEIN_LATERAL_STARTS[i] * length
        veins.moveTo(start_x, 0)
        veins.lineTo(start_x + length * math.cos(angle), side * length * math.sin(angle))

    stroker = QPainterPathStroker()
    stroker.setWidth(max(settings.VEIN_MIN_WIDTH, settings.VEIN_WIDTH_RATIO * length))
    stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
    cut = stroker.createStroke(veins)

    shrink = settings.VEIN_INSET
    inner = leaf_outline(length * shrink, half_width * shrink)
    inner.translate(length * (1 - shrink) / 2, 0)
    cut = cut.intersected(inner)

    return leaf.subtracted(cut)


def oval(length, half_width, near_ratio, far_ratio):
    # Pointed oval: base at (0, 0), tip at (length, 0), widest part half_width above and below.
    near = near_ratio * length
    far = far_ratio * length
    handle = half_width * 4 / 3
    path = QPainterPath()
    path.moveTo(0, 0)
    path.cubicTo(near, -handle, far, -handle, length, 0)
    path.cubicTo(far, handle, near, handle, 0, 0)
    path.closeSubpath()
    return path


def bud_path(size):
    # A teardrop: round at the stem end, pointed at the tip.
    length = size * settings.LEAF_SIZE
    half_width = length * settings.BUD_WIDTH_RATIO / 2
    return oval(length, half_width, settings.BUD_CONTROL_NEAR, settings.BUD_CONTROL_FAR)


def flower_path(size):
    # Five petals around a centre, with five tiny lines cut out of the middle.
    # size is twice the petal length, as a multiple of LEAF_SIZE. The stem end is at (0, 0).
    radius = size * settings.LEAF_SIZE / 2
    half_width = radius * settings.FLOWER_PETAL_WIDTH_RATIO / 2
    petal = oval(radius, half_width, settings.FLOWER_CONTROL_NEAR, settings.FLOWER_CONTROL_FAR)

    flower = petal
    for k in range(1, 5):
        turn = QTransform()
        turn.rotate(72 * k)
        flower = flower.united(turn.map(petal))

    lines = QPainterPath()
    reach = settings.FLOWER_CENTER_LINE_LENGTH * radius
    for k in range(5):
        angle = math.radians(36 + 72 * k)
        lines.moveTo(0, 0)
        lines.lineTo(reach * math.cos(angle), reach * math.sin(angle))
    stroker = QPainterPathStroker()
    stroker.setWidth(max(settings.VEIN_MIN_WIDTH, settings.FLOWER_CENTER_LINE_WIDTH_RATIO * 2 * radius))
    stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
    flower = flower.subtracted(stroker.createStroke(lines))

    return flower.translated(settings.FLOWER_CENTER_OFFSET_RATIO * radius, 0)


BUILDERS = {"leaf": leaf_path, "bud": bud_path, "flower": flower_path}


def cached_path(shape, size):
    # Return the path for this shape, building it only the first time this (rounded) size is asked for.
    steps = settings.SHAPE_CACHE_STEPS
    key = (shape, round(size * steps))
    if key not in _cache:
        _cache[key] = BUILDERS[shape](key[1] / steps)
    return _cache[key]
