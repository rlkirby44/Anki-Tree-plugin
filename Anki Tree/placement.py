from datetime import datetime
import math
from . import growth, settings


def find_slots(nodes, spacing_factor=1.0):
    # Pick the nodes that will carry an item, returned oldest first.
    spacing = settings.LEAF_SIZE * settings.LEAF_SPACING_RATIO * spacing_factor
    if spacing > settings.GRID_CELL_SIZE:
        raise ValueError("LEAF_SIZE * LEAF_SPACING_RATIO must not exceed GRID_CELL_SIZE")

    grid = growth.Grid()
    slots = []
    for node in reversed(nodes):
        if node.parent is None or node.width > settings.MAX_LEAF_WIDTH:
            continue
        too_close = False
        for other in grid.near(node.x, node.y):
            if math.hypot(other.x - node.x, other.y - node.y) < spacing:
                too_close = True
                break
        if too_close:
            continue
        grid.add(node)
        slots.append(node)

    slots.reverse()
    return slots


def sort_group(card):
    # 0 = not new, but no review history; 1 = has review history; 2 = new with no history at all.
    if card["first_seen"] is not None:
        return 1
    if card["kind"] != "new":
        return 0
    return 2


def sort_key(card):
    # Sorting by this puts the cards in placement order: base of the tree first, tips last.
    first_seen = card["first_seen"] or datetime.min
    return (sort_group(card), first_seen, card["card_id"])


def sort_cards(cards):
    return sorted(cards, key=sort_key)


def assign(cards, slots):
    # Pair the oldest cards with the oldest slots. Cards beyond the number of slots (the newest) are left off.
    return list(zip(sort_cards(cards), slots))


def branch_sides(slots):
    # Each slot gets the opposite side of the nearest slot below it on the same branch.
    sides = {}
    for node in slots:
        side = 1
        ancestor = node.parent
        while ancestor is not None:
            if ancestor in sides:
                side = -sides[ancestor]
                break
            ancestor = ancestor.parent
        sides[node] = side
    return sides


def fit_slots(nodes, target):
    # Find slots; if there are fewer than target, shrink the spacing step by step until there are enough or the floor is reached.
    factor = 1.0
    slots = find_slots(nodes, factor)
    while len(slots) < target:
        smaller = factor * settings.SLOT_SHRINK_STEP
        if smaller < settings.SLOT_SHRINK_FLOOR:
            break
        factor = smaller
        slots = find_slots(nodes, factor)
    return slots, factor
