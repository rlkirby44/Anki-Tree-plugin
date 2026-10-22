import math
import random
from datetime import datetime, timedelta
from . import settings


def fake_deck(count, seed):
    # Make a list of fake card records, shaped exactly like the ones from cards.py.
    rng = random.Random(seed)
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    kinds = list(settings.DEBUG_FAKE_KIND_WEIGHTS)
    weights = list(settings.DEBUG_FAKE_KIND_WEIGHTS.values())
    low_due, high_due = settings.DEBUG_FAKE_DUE_RANGE

    records = []
    for card_id in range(count):
        kind = rng.choices(kinds, weights)[0]
        suspended = rng.random() < settings.DEBUG_FAKE_SUSPENDED_CHANCE
        buried = not suspended and rng.random() < settings.DEBUG_FAKE_BURIED_CHANCE
        is_leech = rng.random() < settings.DEBUG_FAKE_LEECH_CHANCE

        first_seen = None
        if kind != "new":
            days_ago = rng.uniform(0, settings.DEBUG_FAKE_HISTORY_DAYS)
            first_seen = now - timedelta(days=days_ago)

        interval_days = None
        if kind in ("learnt", "relearning"):
            interval_days = int(math.exp(rng.uniform(0, math.log(settings.DEBUG_FAKE_MAX_INTERVAL))))
        mature = interval_days is not None and interval_days >= settings.MATURE_INTERVAL

        days_until_due = None
        due_now = False
        if kind == "learnt":
            days_until_due = rng.randint(low_due, high_due)
            due_now = days_until_due <= 0 and not buried

        records.append({
            "card_id": card_id,
            "kind": kind,
            "suspended": suspended,
            "buried": buried,
            "is_leech": is_leech,
            "first_seen": first_seen,
            "interval_days": interval_days,
            "mature": mature,
            "days_until_due": days_until_due,
            "due_now": due_now,
        })
    return records
