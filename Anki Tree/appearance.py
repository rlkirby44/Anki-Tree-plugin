import math
from . import settings


def leaf_size(interval_days):
    # Size of a leaf as a multiple of LEAF_SIZE: 1.0 would be a full-grown leaf.
    days = max(1, interval_days or 1)
    newborn = settings.NEWBORN_LEAF_RATIO
    return 1 - (1 - newborn) * math.exp(-(days - 1) / settings.LEAF_GROWTH_TAU)


def appearance(card):
    # Turn one card record into (shape, colour, size). The first matching rule wins.
    kind = card["kind"]

    if card["suspended"] and card["is_leech"]:
        return "leaf", settings.COLOR_LEECH, leaf_size(card["interval_days"])

    if card["suspended"]:
        if kind == "learnt":
            return "leaf", settings.COLOR_SUSPENDED, leaf_size(card["interval_days"])
        return "bud", settings.COLOR_SUSPENDED, settings.BUD_SIZE_RATIO

    if kind == "relearning":
        return "flower", settings.COLOR_RELEARNING, settings.FLOWER_SIZE_RATIO
    if kind == "learning":
        return "flower", settings.COLOR_LEARNING, settings.FLOWER_SIZE_RATIO
    if kind == "new":
        return "bud", settings.COLOR_NEW, settings.BUD_SIZE_RATIO

    size = leaf_size(card["interval_days"])
    if card["due_now"]:
        return "leaf", settings.COLOR_DUE, size
    if card["mature"]:
        return "leaf", settings.COLOR_MATURE, size
    return "leaf", settings.COLOR_YOUNG, size
