# --- Width ---
K = 2                       # parent width = (child1^K + child2^K) ** (1/K)
MIN_TWIG_WIDTH = 1.        # px, the width of a tip
WIDTH_PER_NODE = 0.03       # px a node gains compared to the node after it

# --- Growth ---
STEP_LENGTH = 6             # px between nodes
WOBBLE = 0.25               # largest random turn per step, in radians
MAX_ROUNDS = 2000           # safety cap
MAX_NODES = 20000           # safety cap

# --- Sprouting ---
BRANCHING_RATE = 0.03       # fraction of nodes that get a sprout roll each round
MAX_SPROUT_WIDTH = 20.0     # nodes wider than this never sprout
TIP_EXCLUDE_NODES = 25       # nodes this close to a tip never sprout
TIP_FALLOFF = 6             # nodes over which sprout chance recovers
SPROUT_ANGLE_MIN = 8       # degrees away from the parent branch
SPROUT_ANGLE_MAX = 10

# --- Leaves ---
MAX_LEAF_WIDTH = 10.0        # nodes thicker than this never carry leaves
MATURE_INTERVAL = 21        # days: an interval this long or longer counts as mature

# --- Item sizes ---
LEAF_SIZE = 32              # px, length of a full-grown leaf; every other size is relative to this
FLOWER_SIZE_RATIO = 1.2     # flower size as a multiple of LEAF_SIZE
BUD_SIZE_RATIO = 0.4        # bud size as a multiple of LEAF_SIZE
NEWBORN_LEAF_RATIO = 0.6    # size of a leaf with a 1 day interval, as a multiple of LEAF_SIZE
LEAF_GROWTH_TAU = 9         # days: bigger = leaves take longer to approach full size
LEAF_WIDTH_RATIO = 0.45     # leaf width as a fraction of its length
LEAF_SPACING_RATIO = 0.25    # minimum gap between leaf slots as a multiple of LEAF_SIZE (result in px must stay <= GRID_CELL_SIZE)

# --- Veins ---
VEIN_SIZE_THRESHOLDS = (0.7, 0.8, 0.9)   # leaf sizes at which the 1st, 2nd and 3rd side vein appear
VEIN_WIDTH_RATIO = 0.03     # vein width as a fraction of leaf size
VEIN_MIN_WIDTH = 0.8        # px: veins are never drawn thinner than this

# --- Minitwigs ---
MINITWIG_WIDTH = 1.0        # px
MINITWIG_LENGTH_RATIO = 0.5   # minitwig length as a fraction of LEAF_SIZE
MINITWIG_TURN = 30          # degrees the minitwig bends away from the branch

# --- Colours ---
COLOR_NEW = "#62b0e0"
COLOR_LEARNING = "#f0913a"
COLOR_RELEARNING = "#f26b5a"
COLOR_YOUNG = "#6cc57a"
COLOR_MATURE = "#2f9e4f"
COLOR_DUE = "#f2d14b"
COLOR_SUSPENDED = "#8a8a8a"
COLOR_LEECH = "#8b5a2b"

# --- Trunk start ---
TRUNK_START_MARGIN = -5     # px in from the bottom-left corner
TRUNK_START_ANGLE = 40      # degrees above horizontal (90 = straight up)
TRUNK_FREE_NODES = 5       # first nodes ignore edge repulsion
TRUNK_BARE_NODES = 5       # first nodes can't sprout

# --- Trunk base flare ---
FLARE_AMOUNT = 0.6          # extra width at the very start of the trunk, as a fraction of its normal width; 0 turns the flare off
FLARE_LENGTH_FRACTION = 0.5 # the flare ends this fraction of the way from the trunk's entry into the window to the first fork (0.5 = halfway)
FLARE_STEEPNESS = 2.0       # same shape control as EDGE_STEEPNESS; higher = the flare drops faster at first and has a longer, flatter tail; near 0 = a straight line down

# --- Performance ---
GRID_CELL_SIZE = 60         # px, for the neighbour lookup grid

# --- Edge and obstacle repulsion ---
EDGE_RANGE = 140            # px: distance at which repulsion starts to be felt
EDGE_STEEPNESS = 6.5        # higher = force stays low longer, then shoots up near the boundary

# --- Debug ---
DEBUG_SHOW_FIELD = True     # paint the repulsion field as orange dots
DEBUG_SEED = 2             # fixed seed while tuning
DEBUG_TRUNK_NODES = 1500     # trunk length in nodes
DEBUG_USE_FAKE_DECK = False      # True = place the fake deck; False = place the real deck (run cards.refresh_cards() first)

# --- Debug overlays ---
DEBUG_SHOW_OBSTACLES = True# blue boxes over the measured page content
DEBUG_SHOW_OUTLINE = False  # red frame around the overlay

# --- Debug: hide the items ---
DEBUG_SHOW_ITEMS = True     # False = paint only the branches (no leaves, buds, flowers or minitwigs)

# --- Debug gallery ---
DEBUG_SHOW_GALLERY = False       # paint the gallery panel over the window
DEBUG_GALLERY_X = 60            # px from the left edge of the overlay to the panel
DEBUG_GALLERY_Y = 100           # px from the top of the overlay to the panel
DEBUG_GALLERY_ZOOMS = (1, 4)    # one block of rows per zoom level; 1 = real size
DEBUG_GALLERY_INTERVALS = (1, 3, 4, 8, 14, 21, 60)   # days: one leaf per interval in the first row
DEBUG_GALLERY_COLOR_INTERVAL = 30   # days: the interval used for the colour row
DEBUG_GALLERY_PADDING = 12      # px: space around the items, between rows, and the height of a label
DEBUG_GALLERY_MIN_CELL = 56     # px: narrowest cell, so that neighbouring labels don't overlap
DEBUG_GALLERY_BACKGROUND = "#2b2b2b"   # panel colour, so that the tree doesn't disturb the view

# --- Steering ---
PUSH_STRENGTH = 0.7         # how strongly the boundary push turns a tip
LOOKAHEAD_DISTANCE = 60     # px ahead where the tip probes for room
LOOKAHEAD_ANGLE = 35        # degrees either side of the heading
LOOKAHEAD_TURN = 0.4        # radians of turn per unit of difference between the two probes
MAX_TURN = 0.1              # largest turn per step, in radians (keeps branches smooth)

# --- Crowding ---
CROWD_RANGE = 45            # px: how far a node's crowding reaches (keep <= GRID_CELL_SIZE)
CROWD_STEEPNESS = 4.0       # same shape control as EDGE_STEEPNESS
CROWD_REF_WIDTH = 10.0      # px: a node this wide counts as "1" when measuring weight
CROWD_WIDTH_POWER = 3       # how steeply a neighbour's push rises with its width
CROWD_WEIGHT_FLOOR = 0.1    # even a very light tip feels heavy neighbours a little
TIP_WEIGHT_STEPS = 10       # a tip's weight is the width of the node this many steps behind it
FAMILY_STEPS = 3           # nodes within this many steps of a shared fork ignore each other

# --- Crowding effects ---
GROWTH_SLOWDOWN = 7.0       # a tip steps with chance 1 / (1 + GROWTH_SLOWDOWN * crowding)
SPROUT_CROWD_DAMPING = 3.0  # same shape, applied to sprout chance
MAX_STALL_ROUNDS = 30       # a tip that fails to grow this many rounds in a row retires

# --- Sprout spacing ---
SPROUT_SPACING_STEPS = 25     # how many nodes to look along the branch, each way
SPROUT_SPACING_FALLOFF = 16    # a fork this many steps away counts about a third as much as an adjacent one
SPROUT_SPACING_DAMPING = 25.0  # sprout chance = 1 / (1 + DAMPING * nearby forks); 0 turns the check off

# --- Branch-to-branch steering ---
BRANCH_PUSH_STRENGTH = 5.0   # how hard neighbouring branches turn a tip away; 0 turns it off
FADE_STEPS = 2               # a sprout feels its sibling at full strength after this many steps

# --- Display ---
MAX_TAPER_PER_NODE = 100   # px: fastest a continuing branch may thin per node; a huge value (100) switches the effect off

# --- Debug fake deck ---
DEBUG_FAKE_DECK_SIZE = 1000                  # how many cards fake_deck makes
DEBUG_FAKE_KIND_WEIGHTS = {"new": 15, "learning": 3, "relearning": 2, "learnt": 80}   # relative weights, not percentages
DEBUG_FAKE_SUSPENDED_CHANCE = 0.02          # chance that a card is suspended
DEBUG_FAKE_BURIED_CHANCE = 0.02             # chance that a card that is not suspended is buried
DEBUG_FAKE_LEECH_CHANCE = 0.25              # chance that a card carries the leech tag
DEBUG_FAKE_MAX_INTERVAL = 365               # days: longest interval a fake card can have
DEBUG_FAKE_HISTORY_DAYS = 400               # days: how far back a fake card's first review can lie
DEBUG_FAKE_DUE_RANGE = (-10, 160)            # days until due for learnt cards; 0 or below means due

# --- Leaf shape and shape cache ---
LEAF_CONTROL_NEAR = 0.15    # where along the leaf (0 = base, 1 = tip) the first curve handle sits; smaller = rounder base
LEAF_CONTROL_FAR = 0.5      # where the second curve handle sits; bigger = blunter tip, smaller = sharper tip
VEIN_INSET = 0.8            # veins are clipped to a copy of the leaf shrunk to this fraction; smaller = veins stop further from the edge
VEIN_LATERAL_STARTS = (0.30, 0.20, 0.50)   # where the 1st, 2nd and 3rd side vein leave the centre vein (0 = base, 1 = tip); keep as many entries as VEIN_SIZE_THRESHOLDS
VEIN_LATERAL_SIDES = (1, -1, -1)   # side of the 1st, 2nd and 3rd side vein: 1 = lower edge, -1 = upper edge (leaf pointing right); keep as many entries as VEIN_SIZE_THRESHOLDS
VEIN_LATERAL_ANGLE = 40     # degrees between a side vein and the centre vein
SHAPE_CACHE_STEPS = 40      # sizes are rounded to a multiple of 1/this before a shape is cached

# --- Bud ---
BUD_WIDTH_RATIO = 0.5       # bud width as a fraction of its length
BUD_CONTROL_NEAR = 0.05    # 0 = fully round base; bigger = pointier base (0.25 would be the oval's value)
BUD_CONTROL_FAR = 0.525     # smaller = widest part nearer the base and a longer, sharper tip (0.75 would be the oval's value)

# --- Flower ---
FLOWER_PETAL_WIDTH_RATIO = 0.5    # petal width as a fraction of petal length; bigger = fatter petals that overlap more
FLOWER_CONTROL_NEAR = 0.2          # same meaning as LEAF_CONTROL_NEAR, for one petal
FLOWER_CONTROL_FAR = 0.5           # same meaning as LEAF_CONTROL_FAR, for one petal
FLOWER_CENTER_OFFSET_RATIO = 0.45  # distance from the stem end to the flower's centre, as a fraction of petal length
FLOWER_CENTER_LINE_LENGTH = 0.3    # length of each centre line as a fraction of petal length (must stay short of where petals meet)
FLOWER_CENTER_LINE_WIDTH_RATIO = 0.04   # centre line width as a fraction of the flower's width (never thinner than VEIN_MIN_WIDTH)

# --- Placement on the tree ---
MINITWIG_COLOR = "#6e461e"      # same brown as the branches (110, 70, 30)

# --- Stopping rule ---
SLOT_CHECK_ROUNDS = 10      # the tree counts its leaf slots every this many rounds and stops once there are enough

# --- Fitting all cards ---
SLOT_SHRINK_STEP = 0.95     # each attempt multiplies the leaf spacing by this (closer to 1 = finer steps)
SLOT_SHRINK_FLOOR = 0.5     # safety stop: the spacing is never shrunk below this fraction of the normal spacing

# --- Background growth ---
GROWTH_PAUSE = 0.001        # seconds the growth thread sleeps after each round; bigger = gentler on the interface, slower tree

# --- Obstacle padding ---
OBSTACLE_SMALL_SIZE = 120       # px: a rectangle whose shorter side is below this counts as small (buttons, text lines)
OBSTACLE_PADDING_SMALL = 10     # px of extra blocked space around each small rectangle
OBSTACLE_PADDING_LARGE = 5      # px of extra blocked space around the large ones (deck table and similar)

# --- Discouraging growth towards the trunk ---
BACKWARD_SLOWDOWN = 5.0         # added to the growth slowdown at full backwardness (heading straight back at the trunk start); 0 turns the effect off
BACKWARD_FREE_ANGLE = 120        # degrees away from "straight out from the trunk start" that cost nothing; 180 = no penalty at all
BACKWARD_MIN_DISTANCE = 150     # px: tips closer to the trunk start than this are never penalised

# --- Manual obstacle ---
MANUAL_OBSTACLE_ENABLED = True
MANUAL_OBSTACLE_X = 0.5       # centre, as a fraction of the window width (0 = left edge, 1 = right edge)
MANUAL_OBSTACLE_Y = 1        # centre, as a fraction of the window height (0 = top edge, 1 = bottom edge)
MANUAL_OBSTACLE_WIDTH = 0.3    # fraction of the window width (0.13 is about 248 px in a 1900 px wide window)
MANUAL_OBSTACLE_HEIGHT = 0.02 # fraction of the window height (0.0185 is about 19 px in a 1028 px high window)
MANUAL_OBSTACLE_PADDING = 0     # px of extra blocked space on every side

EDGE_INSET = 22             # px: the wall sits this far inside the window edge on all sides; repulsion reaches its maximum here

# --- Menu bar ---
MENUBAR_BLOCK_PADDING = 12      # px of blocked space around the File/Edit/View/Tools/Help items

# --- Edge degrowth (slows tips near edges and obstacles instead of steering them) ---
EDGE_SLOWDOWN = 10.0            # added to the growth slowdown right at an edge or obstacle; a tip then steps with chance 1 / (1 + this); 0 turns it off
EDGE_SLOWDOWN_RANGE = 175        # px: distance from the wall (or obstacle) at which the slowdown starts to be felt
EDGE_SLOWDOWN_STEEPNESS = 2.0   # same shape control as EDGE_STEEPNESS; higher = stays weak longer, then rises sharply near the wall
EDGE_SLOWDOWN_FREE_NODES = 60   # nodes at or below this depth (counted from the trunk start) are never slowed by edges, so the trunk can grow clear of the corner
