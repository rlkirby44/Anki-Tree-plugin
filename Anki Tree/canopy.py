import math
from aqt import mw
from aqt.qt import QColor, QBrush, QPainterPath, QPen, Qt
from . import appearance, cards, debug_deck, growth, placement, settings, shapes

# A one-line summary of the last build, printed by dev.py.
report = ""


def current_deck():
    if settings.DEBUG_USE_FAKE_DECK:
        return debug_deck.fake_deck(settings.DEBUG_FAKE_DECK_SIZE, settings.DEBUG_SEED)
    return cards.cards


# Counts growth requests. A running growth checks it to see whether it has been replaced or cancelled.
generation = 0


def cancel():
    # Tell any running growth to stop early and to throw its result away.
    global generation
    generation += 1


def start_growth(width, height, obstacles, on_done):
    # Grow a tree in a background thread. on_done(nodes) is called on the main thread when it is ready.
    global generation
    generation += 1
    mine = generation
    target = len(current_deck())

    def enough(nodes):
        if generation != mine:
            return True
        return len(placement.find_slots(nodes)) >= target

    def job():
        nodes = growth.grow_tree(width, height, obstacles, settings.DEBUG_SEED,
                                 settings.MAX_NODES, enough)
        return nodes, growth.last_run

    def finished(future):
        nodes, summary = future.result()
        if generation != mine:
            return
        growth.last_run = summary
        on_done(nodes)

    mw.taskman.run_in_background(job, finished, uses_collection=False)


def build(nodes):
    # Match cards to slots and work out each item's minitwig and position. Returns a list of items.
    global report
    deck = current_deck()
    slots, factor = placement.fit_slots(nodes, len(deck))
    pairs = placement.assign(deck, slots)
    report = (f"{len(pairs)} of {len(deck)} cards placed ({len(slots)} slots, spacing x{factor:.2f}); "
              f"{growth.last_run}")

    sides = placement.branch_sides([node for card, node in pairs])
    length = settings.LEAF_SIZE * settings.MINITWIG_LENGTH_RATIO
    turn = math.radians(settings.MINITWIG_TURN)
    items = []
    for card, node in pairs:
        side = sides[node]
        start_dir = node.direction
        end_dir = start_dir + side * turn

        mid_x = node.x + length / 2 * math.cos(start_dir)
        mid_y = node.y + length / 2 * math.sin(start_dir)
        end_x = mid_x + length / 2 * math.cos(end_dir)
        end_y = mid_y + length / 2 * math.sin(end_dir)

        twig = QPainterPath()
        twig.moveTo(node.x, node.y)
        twig.quadTo(mid_x, mid_y, end_x, end_y)

        shape, colour, size = appearance.appearance(card)
        items.append((twig, shape, colour, size, end_x, end_y, math.degrees(end_dir)))
    return items


def paint(painter, items):
    if not settings.DEBUG_SHOW_ITEMS:
        return
    painter.save()
    painter.setBrush(Qt.BrushStyle.NoBrush)
    pen = QPen(QColor(settings.MINITWIG_COLOR))
    pen.setWidthF(settings.MINITWIG_WIDTH)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    for twig, shape, colour, size, end_x, end_y, angle in items:
        painter.drawPath(twig)

    for twig, shape, colour, size, end_x, end_y, angle in items:
        painter.save()
        painter.translate(end_x, end_y)
        painter.rotate(angle)
        painter.fillPath(shapes.cached_path(shape, size), QBrush(QColor(colour)))
        painter.restore()
    painter.restore()
