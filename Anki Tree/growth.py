import math
import random
import time
from . import settings

last_run = ""    # summary of the most recent grow_tree call; canopy.py shows it in its report

def closeness(d, reach=None, steepness=None):
    if reach is None:
        reach = settings.EDGE_RANGE
    if steepness is None:
        steepness = settings.EDGE_STEEPNESS
    if d >= reach:
        return 0.0
    if d <= 0:
        return 1.0
    t = 1 - d / reach
    return (math.exp(steepness * t) - 1) / (math.exp(steepness) - 1)


def push_from_boundaries(x, y, width, height, obstacles):
    fx = 0.0
    fy = 0.0

    inset = settings.EDGE_INSET
    fx += closeness(x - inset)
    fx -= closeness(width - inset - x)
    fy += closeness(y - inset)
    fy -= closeness(height - inset - y)

    for rx, ry, rw, rh in obstacles:
        cx = min(max(x, rx), rx + rw)
        cy = min(max(y, ry), ry + rh)
        dx = x - cx
        dy = y - cy
        d = math.hypot(dx, dy)

        if d >= settings.EDGE_RANGE:
            continue

        if d > 0:
            strength = closeness(d)
            fx += strength * dx / d
            fy += strength * dy / d
        else:
            to_left = x - rx
            to_right = rx + rw - x
            to_top = y - ry
            to_bottom = ry + rh - y
            nearest = min(to_left, to_right, to_top, to_bottom)
            if nearest == to_left:
                fx -= 1.0
            elif nearest == to_right:
                fx += 1.0
            elif nearest == to_top:
                fy -= 1.0
            else:
                fy += 1.0

    return fx, fy


class Node:
    def __init__(self, x, y, parent, direction, age):
        self.x = x
        self.y = y
        self.parent = parent
        self.children = []
        self.direction = direction
        self.age = age
        self.depth = 0 if parent is None else parent.depth + 1
        self.width = settings.MIN_TWIG_WIDTH
        self.tip_distance = 0
        self.stalled = 0
        self.entered = True
        self.display_width = settings.MIN_TWIG_WIDTH
        chain = [self]
        ancestor = parent
        while ancestor is not None and len(chain) < settings.FAMILY_STEPS:
            chain.append(ancestor)
            ancestor = ancestor.parent
        self.lineage = frozenset(chain)
        if parent is not None:
            parent.children.append(self)


class Grid:
    def __init__(self):
        self.cells = {}

    def add(self, node):
        size = settings.GRID_CELL_SIZE
        key = (int(node.x // size), int(node.y // size))
        self.cells.setdefault(key, []).append(node)

    def near(self, x, y):
        size = settings.GRID_CELL_SIZE
        cx = int(x // size)
        cy = int(y // size)
        found = []
        for i in (cx - 1, cx, cx + 1):
            for j in (cy - 1, cy, cy + 1):
                found.extend(self.cells.get((i, j), []))
        return found


def pad_obstacles(rects):
    # Grow each measured rectangle by a margin; small ones get more than large ones.
    padded = []
    for x, y, w, h in rects:
        if min(w, h) < settings.OBSTACLE_SMALL_SIZE:
            pad = settings.OBSTACLE_PADDING_SMALL
        else:
            pad = settings.OBSTACLE_PADDING_LARGE
        padded.append((x - pad, y - pad, w + 2 * pad, h + 2 * pad))
    return padded


def manual_obstacles(width, height):
    # The hand-placed obstacle, as a list holding one rectangle (empty if switched off).
    if not settings.MANUAL_OBSTACLE_ENABLED:
        return []
    cx = settings.MANUAL_OBSTACLE_X * width
    cy = settings.MANUAL_OBSTACLE_Y * height
    w = settings.MANUAL_OBSTACLE_WIDTH * width
    h = settings.MANUAL_OBSTACLE_HEIGHT * height
    pad = settings.MANUAL_OBSTACLE_PADDING
    return [(cx - w / 2 - pad, cy - h / 2 - pad, w + 2 * pad, h + 2 * pad)]


def inside_playfield(x, y, width, height):
    inset = settings.EDGE_INSET
    return inset <= x <= width - inset and inset <= y <= height - inset


def is_free(x, y, width, height, obstacles):
    if not inside_playfield(x, y, width, height):
        return False
    for rx, ry, rw, rh in obstacles:
        if rx <= x <= rx + rw and ry <= y <= ry + rh:
            return False
    return True


def lookahead_turn(node, width, height, obstacles):
    a = math.radians(settings.LOOKAHEAD_ANGLE)
    d = settings.LOOKAHEAD_DISTANCE

    ax = node.x + d * math.cos(node.direction - a)
    ay = node.y + d * math.sin(node.direction - a)
    bx = node.x + d * math.cos(node.direction + a)
    by = node.y + d * math.sin(node.direction + a)

    fax, fay = push_from_boundaries(ax, ay, width, height, obstacles)
    fbx, fby = push_from_boundaries(bx, by, width, height, obstacles)
    crowd_a = math.hypot(fax, fay)
    crowd_b = math.hypot(fbx, fby)

    return settings.LOOKAHEAD_TURN * (crowd_a - crowd_b)


def grow_step(node, width, height, obstacles, rng, grid=None):
    heading = node.direction + rng.uniform(-settings.WOBBLE, settings.WOBBLE)
    steer = node.entered and node.depth >= settings.TRUNK_FREE_NODES

    if steer:
        heading += lookahead_turn(node, width, height, obstacles)

    vx = math.cos(heading)
    vy = math.sin(heading)

    if steer:
        px, py = push_from_boundaries(node.x, node.y, width, height, obstacles)
        vx += settings.PUSH_STRENGTH * px
        vy += settings.PUSH_STRENGTH * py
        if grid is not None:
            bx, by = branch_push(node, grid)
            vx += settings.BRANCH_PUSH_STRENGTH * bx
            vy += settings.BRANCH_PUSH_STRENGTH * by

    turn = math.atan2(vy, vx) - node.direction
    turn = math.atan2(math.sin(turn), math.cos(turn))
    turn = max(-settings.MAX_TURN, min(settings.MAX_TURN, turn))
    direction = node.direction + turn

    x = node.x + settings.STEP_LENGTH * math.cos(direction)
    y = node.y + settings.STEP_LENGTH * math.sin(direction)

    inside = inside_playfield(x, y, width, height)
    if node.entered or inside:
        if not is_free(x, y, width, height, obstacles):
            return None
    new = Node(x, y, node, direction, node.age + 1)
    new.entered = node.entered or inside
    return new


def update_tip_distances(nodes):
    for node in reversed(nodes):
        if not node.children:
            node.tip_distance = 0
        else:
            node.tip_distance = 1 + min(child.tip_distance for child in node.children)


def update_widths(nodes):
    k = settings.K
    for node in reversed(nodes):
        if not node.children:
            node.width = settings.MIN_TWIG_WIDTH
        elif len(node.children) == 1:
            node.width = node.children[0].width + settings.WIDTH_PER_NODE
        else:
            total = sum(child.width ** k for child in node.children)
            node.width = total ** (1 / k) + settings.WIDTH_PER_NODE


def main_child(node):
    # The child that carries the most weight; on a tie the first child wins.
    best = node.children[0]
    for child in node.children[1:]:
        if child.width > best.width:
            best = child
    return best


def update_display_widths(nodes):
    # Bottom-up: the thickest a node may be drawn, so that its branch can still taper to a point.
    limit = {}
    for node in reversed(nodes):
        if node.children:
            limit[node] = limit[main_child(node)] + settings.MAX_TAPER_PER_NODE
        else:
            limit[node] = settings.MIN_TWIG_WIDTH

    # Top-down: thin slowly from the parent, but never above the limit and never below the real width.
    for node in nodes:
        node.display_width = node.width
        parent = node.parent
        if parent is not None and main_child(parent) is node:
            wanted = min(parent.display_width - settings.MAX_TAPER_PER_NODE, limit[node])
            node.display_width = max(node.width, wanted)

    # Last: flare the base. This is a separate pass so that the extra width doesn't leak into the taper above.
    entry_depth = 0
    for node in nodes:
        if node.entered:
            entry_depth = node.depth
            break
    fork_depths = [node.depth for node in nodes if len(node.children) >= 2]
    if fork_depths:
        first_fork = min(fork_depths)
    else:
        first_fork = max(node.depth for node in nodes)
    flare_length = (first_fork - entry_depth) * settings.FLARE_LENGTH_FRACTION

    for node in nodes:
        steps = max(0, node.depth - entry_depth)
        fade = closeness(steps, flare_length, settings.FLARE_STEEPNESS)
        node.display_width *= 1 + settings.FLARE_AMOUNT * fade


def tip_weight(node):
    n = node
    for _ in range(settings.TIP_WEIGHT_STEPS):
        p = n.parent
        if p is None or (len(p.children) == 2 and p.children[1] is n):
            break
        n = p
    return n.width


def crowding(tip, grid):
    weight = settings.CROWD_WEIGHT_FLOOR + tip_weight(tip) / settings.CROWD_REF_WIDTH
    total = 0.0
    for other in grid.near(tip.x, tip.y):
        if not tip.lineage.isdisjoint(other.lineage):
            continue
        d = math.hypot(other.x - tip.x, other.y - tip.y)
        if d >= settings.CROWD_RANGE:
            continue
        pusher = (other.width / settings.CROWD_REF_WIDTH) ** settings.CROWD_WIDTH_POWER
        total += closeness(d, settings.CROWD_RANGE, settings.CROWD_STEEPNESS) * pusher * weight
    return total


def relation_fade(tip, other):
    if other in tip.lineage:
        return 0.0
    steps_apart = settings.FAMILY_STEPS - len(tip.lineage & other.lineage)
    return min(1.0, steps_apart / settings.FADE_STEPS)


def branch_push(tip, grid):
    weight = settings.CROWD_WEIGHT_FLOOR + tip_weight(tip) / settings.CROWD_REF_WIDTH
    fx = 0.0
    fy = 0.0
    for other in grid.near(tip.x, tip.y):
        fade = relation_fade(tip, other)
        if fade == 0.0:
            continue
        dx = tip.x - other.x
        dy = tip.y - other.y
        d = math.hypot(dx, dy)
        if d == 0 or d >= settings.CROWD_RANGE:
            continue
        pusher = (other.width / settings.CROWD_REF_WIDTH) ** settings.CROWD_WIDTH_POWER
        strength = closeness(d, settings.CROWD_RANGE, settings.CROWD_STEEPNESS) * pusher * weight * fade
        fx += strength * dx / d
        fy += strength * dy / d
    return fx, fy


def recent_forks(node):
    reach = settings.SPROUT_SPACING_STEPS
    falloff = settings.SPROUT_SPACING_FALLOFF
    total = 0.0

    n = node.parent
    for d in range(1, reach + 1):
        if n is None:
            break
        if len(n.children) == 2:
            total += math.exp(-d / falloff)
        n = n.parent

    n = node
    for d in range(1, reach + 1):
        if not n.children:
            break
        n = n.children[0]
        if len(n.children) == 2:
            total += math.exp(-d / falloff)

    return total


def try_sprout(node, round_number, width, height, obstacles, rng):
    angle = math.radians(rng.uniform(settings.SPROUT_ANGLE_MIN, settings.SPROUT_ANGLE_MAX))
    d = settings.LOOKAHEAD_DISTANCE
    base = node.children[0].direction if node.children else node.direction

    crowd = {}
    for side in (1, -1):
        px = node.x + d * math.cos(base + side * angle)
        py = node.y + d * math.sin(base + side * angle)
        fx, fy = push_from_boundaries(px, py, width, height, obstacles)
        crowd[side] = math.hypot(fx, fy)

    total = crowd[1] + crowd[-1]
    p_plus = 0.5 if total == 0 else crowd[-1] / total
    side = 1 if rng.random() < p_plus else -1

    direction = base + side * angle
    x = node.x + settings.STEP_LENGTH * math.cos(direction)
    y = node.y + settings.STEP_LENGTH * math.sin(direction)
    if not is_free(x, y, width, height, obstacles):
        return None
    return Node(x, y, node, direction, round_number)


def backwardness(node, home_x, home_y):
    # 0 = growing away from the trunk start or sideways; 1 = growing straight back towards it.
    dx = node.x - home_x
    dy = node.y - home_y
    if math.hypot(dx, dy) < settings.BACKWARD_MIN_DISTANCE:
        return 0.0
    outward = math.atan2(dy, dx)
    diff = node.direction - outward
    diff = abs(math.atan2(math.sin(diff), math.cos(diff)))
    free = math.radians(settings.BACKWARD_FREE_ANGLE)
    if diff <= free:
        return 0.0
    return (diff - free) / (math.pi - free)


def edge_pressure(x, y, width, height, obstacles):
    # 0 = far from every wall and obstacle; 1 = at or beyond the nearest one.
    reach = settings.EDGE_SLOWDOWN_RANGE
    steepness = settings.EDGE_SLOWDOWN_STEEPNESS
    inset = settings.EDGE_INSET
    d = min(x - inset, width - inset - x, y - inset, height - inset - y)
    strongest = closeness(d, reach, steepness)
    for rx, ry, rw, rh in obstacles:
        cx = min(max(x, rx), rx + rw)
        cy = min(max(y, ry), ry + rh)
        strongest = max(strongest, closeness(math.hypot(x - cx, y - cy), reach, steepness))
    return strongest


def grow_tree(width, height, obstacles, seed, max_nodes, enough=None):
    global last_run
    started = time.perf_counter()
    rng = random.Random(seed)
    start = Node(settings.TRUNK_START_MARGIN,
                 height - settings.TRUNK_START_MARGIN,
                 None,
                 -math.radians(settings.TRUNK_START_ANGLE),
                 0)
    grid = Grid()
    start.entered = inside_playfield(start.x, start.y, width, height)
    grid.add(start)
    nodes = [start]
    tips = [start]
    reason = "round cap"
    rounds_done = 0

    for round_number in range(1, settings.MAX_ROUNDS + 1):
        if not tips:
            reason = "all tips retired"
            break
        if len(nodes) >= max_nodes:
            reason = "node cap"
            break

        # 1. every tip tries to take one step
        new_tips = []
        for tip in tips:
            crowd = crowding(tip, grid)
            back = backwardness(tip, start.x, start.y)
            edge = 0.0    # changed
            if tip.entered and tip.depth >= settings.EDGE_SLOWDOWN_FREE_NODES:    # changed
                edge = edge_pressure(tip.x, tip.y, width, height, obstacles)    # changed
            slowdown = (settings.GROWTH_SLOWDOWN * crowd
                        + settings.BACKWARD_SLOWDOWN * back
                        + settings.EDGE_SLOWDOWN * edge)
            if rng.random() > 1 / (1 + slowdown):
                tip.stalled += 1
                if tip.stalled <= settings.MAX_STALL_ROUNDS:
                    new_tips.append(tip)
                continue
            new = grow_step(tip, width, height, obstacles, rng, grid)
            if new is not None:
                nodes.append(new)
                grid.add(new)
                new_tips.append(new)

        # 2. refresh each node's distance to its nearest tip, and the widths
        update_tip_distances(nodes)
        update_widths(nodes)

        # 3. sample random nodes and let some of them sprout
        expected = settings.BRANCHING_RATE * len(nodes)
        picks = int(expected) + (1 if rng.random() < expected - int(expected) else 0)
        for _ in range(picks):
            node = rng.choice(nodes)
            if node.depth < settings.TRUNK_BARE_NODES:
                continue
            if node.tip_distance <= settings.TIP_EXCLUDE_NODES:
                continue
            if len(node.children) >= 2:
                continue
            if node.width > settings.MAX_SPROUT_WIDTH:
                continue
            gap = node.tip_distance - settings.TIP_EXCLUDE_NODES
            if rng.random() > 1 - math.exp(-gap / settings.TIP_FALLOFF):
                continue
            recent = recent_forks(node)
            if rng.random() > 1 / (1 + settings.SPROUT_SPACING_DAMPING * recent):
                continue
            crowd = crowding(node, grid)
            if rng.random() > 1 / (1 + settings.SPROUT_CROWD_DAMPING * crowd):
                continue
            sprout = try_sprout(node, round_number, width, height, obstacles, rng)
            if sprout is not None:
                nodes.append(sprout)
                grid.add(sprout)
                new_tips.append(sprout)

        tips = new_tips
        rounds_done = round_number
        if settings.GROWTH_PAUSE > 0:
            time.sleep(settings.GROWTH_PAUSE)

        # 4. every few rounds, ask whether the tree already has enough leaf slots
        if enough is not None and round_number % settings.SLOT_CHECK_ROUNDS == 0:
            update_widths(nodes)
            if enough(nodes):
                reason = "enough slots"
                break

    update_tip_distances(nodes)
    update_widths(nodes)
    update_display_widths(nodes)
    seconds = time.perf_counter() - started
    last_run = f"stopped: {reason} after {rounds_done} rounds, {len(nodes)} nodes, {seconds:.1f} s"
    return nodes
