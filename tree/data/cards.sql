-- One row per card in the selected deck and its subdecks.
-- __DECK_IDS__ is replaced by cards.py with a comma-separated list of deck ids.
-- The column order must match the unpacking in load_deck_cards.
SELECT
    c.id,
    c.type,
    c.queue,
    c.ivl,
    c.due,
    c.odue,
    c.odid,
    n.tags,
    (SELECT MIN(r.id) FROM revlog r WHERE r.cid = c.id AND r.type < 4)
FROM cards c
JOIN notes n ON n.id = c.nid
WHERE c.did IN (__DECK_IDS__) OR c.odid IN (__DECK_IDS__)
