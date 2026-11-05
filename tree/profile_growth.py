import cProfile
import importlib
import pstats

from . import overlay, settings
from .drawing import canopy
from .simulation import growth, placement

# The functions that get their own line in the second table.
WATCH = ("update_tip_distances", "update_widths", "crowding", "branch_push",
         "edge_pressure", "push_from_boundaries", "is_free", "find_slots")


def run(top=12):
    # Grow one tree on the real page layout, once plainly and once with the profiler, then print where the time went.
    w = overlay.overlay
    if w is None or not w.isVisible():
        print("Open the deck list first.")
        return
    if w.growing:
        print("The tree is still growing. Wait until it appears, then run this again.")
        return

    # Pick up any edits to these files, the same way dev.regrow() does.
    for module in (settings, growth, placement):
        importlib.reload(module)

    width, height = w.width(), w.height()
    obstacles = w.obstacles
    target = len(canopy.current_deck())
    print(f"window {width} x {height}, {len(obstacles)} obstacles, {target} cards")

    def enough(nodes):
        # The same stopping test that canopy.start_growth uses.
        return len(placement.find_slots(nodes)) >= target

    def grow():
        return growth.grow_tree(width, height, obstacles, settings.DEBUG_SEED,
                                settings.MAX_NODES, enough)

    print("Run 1 of 2: plain timing. Anki freezes until it finishes.")
    grow()
    print(growth.last_run)

    print("Run 2 of 2: with the profiler. This one is slower.")
    profiler = cProfile.Profile()
    profiler.runcall(grow)

    # One row per function: (name, number of calls, own time, time including everything it calls).
    stats = pstats.Stats(profiler)
    rows = []
    for (filename, line, name), (primitive, calls, own, total, callers) in stats.stats.items():
        rows.append((name, calls, own, total))

    # Every second of the run is some function's own time, so the sum of the own times is the whole profiled run.
    all_own = sum(row[2] for row in rows)

    rows.sort(key=lambda row: row[2], reverse=True)
    print()
    print(f"The profiled run took about {all_own:.1f} s in total (slower than run 1, because of the profiler)")
    print(f"Top {top} functions by their own time")
    print(f"{'function':<30}{'calls':>12}{'own s':>9}{'own %':>8}")
    for name, calls, own, total in rows[:top]:
        print(f"{name[:29]:<30}{calls:>12}{own:>9.2f}{100 * own / all_own:>7.1f}%")

    watched = [row for row in rows if row[0] in WATCH or "sleep" in row[0]]
    watched.sort(key=lambda row: row[3], reverse=True)
    print()
    print("Time including everything each function calls (these overlap, so do not add them up)")
    print(f"{'function':<30}{'calls':>12}{'total s':>9}{'of run':>9}")
    for name, calls, own, total in watched:
        print(f"{name[:29]:<30}{calls:>12}{total:>9.2f}{100 * total / all_own:>8.1f}%")

    both = sum(row[3] for row in rows if row[0] in ("update_tip_distances", "update_widths"))
    print()
    print(f"update_tip_distances + update_widths together: "
          f"{both:.2f} s, {100 * both / all_own:.0f}% of the profiled run")
