from datetime import datetime
from aqt import mw
from . import settings

# The plugin's snapshot of the selected deck. Rebuilt by refresh_cards().
cards = []

# Anki stores a card's type as a number; this turns it into a word.
KIND_NAMES = {0: "new", 1: "learning", 2: "learnt", 3: "relearning"}


def load_deck_cards(deck_id):
    # Read every card in the deck (and its subdecks) in one SQL query.
    col = mw.col
    deck_ids = ", ".join(str(d) for d in col.decks.deck_and_child_ids(deck_id))
    today = col.sched.today  # current day number, same scale as card.due for review cards

    rows = col.db.all(f"""
        SELECT c.id, c.type, c.queue, c.ivl, c.due, c.odue, c.odid, n.tags,
            (SELECT MIN(r.id) FROM revlog r WHERE r.cid = c.id AND r.type < 4)
        FROM cards c
        JOIN notes n ON n.id = c.nid
        WHERE c.did IN ({deck_ids}) OR c.odid IN ({deck_ids})
    """)

    card_records = []
    for cid, ctype, queue, ivl, due, odue, odid, tags, first_review_ms in rows:
        kind = KIND_NAMES[ctype]
        suspended = queue == -1
        buried = queue in (-2, -3)
        is_leech = "leech" in tags.lower().split()

        first_seen = None
        if first_review_ms is not None:
            first_seen = datetime.fromtimestamp(first_review_ms / 1000)

        interval_days = ivl if ivl > 0 else None
        mature = interval_days is not None and interval_days >= settings.MATURE_INTERVAL

        days_until_due = None
        due_now = False
        if kind == "learnt":
            real_due = odue if odid else due     # cards in a filtered deck keep their real due in odue
            days_until_due = real_due - today    # negative means overdue
            due_now = days_until_due <= 0 and not buried

        card_records.append({
            "card_id": cid,
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
    return card_records


def refresh_cards():
    # Rebuild the snapshot for the deck currently selected in Anki.
    global cards
    cards = load_deck_cards(mw.col.decks.get_current_id())
