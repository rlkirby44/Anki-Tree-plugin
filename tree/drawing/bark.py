from aqt.qt import QColor
from .. import settings

# Finished colours, so each distinct width is worked out only once.
_cache = {}


def bark_color(width):
    # Colour of a branch segment drawn at this width: light for twigs, dark for thick wood.
    key = round(width * 4)
    if key not in _cache:
        low = settings.BARK_WIDTH_THIN
        high = settings.BARK_WIDTH_THICK
        t = min(1.0, max(0.0, (key / 4 - low) / (high - low))) ** settings.BARK_COLOR_CURVE
        thin = QColor(settings.BARK_COLOR_THIN)
        thick = QColor(settings.BARK_COLOR_THICK)
        r = thin.red() + t * (thick.red() - thin.red())
        g = thin.green() + t * (thick.green() - thin.green())
        b = thin.blue() + t * (thick.blue() - thin.blue())
        _cache[key] = QColor(int(r + 0.5), int(g + 0.5), int(b + 0.5))
    return _cache[key]
