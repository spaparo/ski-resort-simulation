# SKI RESORT SIMULATION CONFIG
# Based on Val Thorens, France

# RUN MODE

RUN_MODE = "normal"

NORMAL_VISITORS = 250
STRESS_VISITORS = 2500

# Keep NUM_VISITORS for compatibility with older code
NUM_VISITORS = NORMAL_VISITORS if RUN_MODE == "normal" else STRESS_VISITORS

USE_RANDOM_SEED = False
RANDOM_SEED = 42


# ARRIVAL PATTERN

ARRIVAL_INTERVAL_MIN = 0.05
ARRIVAL_INTERVAL_MAX = 0.16


# RENTAL SHOP

NUM_SKIS = 140
NUM_SNOWBOARDS = 120
RENTAL_STAFF = 10
RENTAL_TIME_MIN = 0.8
RENTAL_TIME_MAX = 1.6


# LIFT SYSTEM

NUM_LIFTS = 5
LIFT_CAPACITY = 8
LIFT_RIDE_TIME_MIN = 0.9
LIFT_RIDE_TIME_MAX = 1.7


# SLOPES

SLOPE_CONFIGS = [
    {
        "name": "Green",
        "difficulty": "beginner",
        "capacity": 65,
        "time_min": 1.0,
        "time_max": 1.8,
        "fall_modifier": 0.7
    },
    {
        "name": "Blue",
        "difficulty": "intermediate",
        "capacity": 55,
        "time_min": 1.2,
        "time_max": 2.1,
        "fall_modifier": 1.0
    },
    {
        "name": "Red",
        "difficulty": "advanced",
        "capacity": 45,
        "time_min": 1.5,
        "time_max": 2.5,
        "fall_modifier": 1.3
    },
    {
        "name": "Black",
        "difficulty": "expert",
        "capacity": 30,
        "time_min": 1.8,
        "time_max": 3.0,
        "fall_modifier": 1.7
    },
    {
        "name": "Orange",
        "difficulty": "snow_park",
        "capacity": 35,
        "time_min": 1.4,
        "time_max": 2.6,
        "fall_modifier": 1.5
    }
]

# Keep old slope constants for compatibility with older code
NUM_SLOPES = len(SLOPE_CONFIGS)
SLOPE_CAPACITY = 50
SLOPE_TIME_MIN = 1.2
SLOPE_TIME_MAX = 2.3

FALL_CHANCE = 0.05
FALL_DELAY = 0.6


# VISITOR TYPES

VISITOR_TYPES = ["skier", "snowboarder"]


# VISITOR BEHAVIOR

MIN_RUNS_PER_VISITOR = 2
MAX_RUNS_PER_VISITOR = 4

STARTING_ENERGY = 100
ENERGY_LOSS_PER_RUN_SKIER = 14
ENERGY_LOSS_PER_RUN_SNOWBOARDER = 17
ENERGY_GAIN_CAFE = 25
LEAVE_ENERGY_THRESHOLD = 35


# AGE GROUPS

AGE_GROUPS = ["child", "adult", "senior"]

AGE_GROUP_PROBABILITIES = {
    "child": 0.20,
    "adult": 0.65,
    "senior": 0.15
}


# SKILL LEVELS

SKILL_LEVELS = ["beginner", "intermediate", "advanced"]

SKILL_LEVEL_PROBABILITIES = {
    "beginner": 0.35,
    "intermediate": 0.45,
    "advanced": 0.20
}


# EQUIPMENT

OWN_EQUIPMENT_CHANCE = 0.35


# WEATHER

WEATHER_OPTIONS = ["sunny", "snowy", "windy", "stormy"]

WEATHER_EFFECTS = {
    "sunny": {
        "lift_multiplier": 1.0,
        "slope_multiplier": 1.0,
        "fall_multiplier": 1.0,
        "break_multiplier": 1.0
    },
    "snowy": {
        "lift_multiplier": 1.15,
        "slope_multiplier": 1.2,
        "fall_multiplier": 1.3,
        "break_multiplier": 1.1
    },
    "windy": {
        "lift_multiplier": 1.3,
        "slope_multiplier": 1.1,
        "fall_multiplier": 1.2,
        "break_multiplier": 1.05
    },
    "stormy": {
        "lift_multiplier": 1.6,
        "slope_multiplier": 1.4,
        "fall_multiplier": 1.8,
        "break_multiplier": 1.3
    }
}


# PEAK ARRIVAL PERIOD

PEAK_START_VISITOR = 70
PEAK_END_VISITOR = 160

PEAK_ARRIVAL_INTERVAL_MIN = 0.04
PEAK_ARRIVAL_INTERVAL_MAX = 0.10

PEAK_SERVICE_SLOWDOWN_FACTOR = 1.08


# DAY PHASES

LUNCH_START_VISITOR = 90
LUNCH_END_VISITOR = 170

LAST_LIFT_VISITOR = 220
RESORT_CLOSE_VISITOR = 250


# CAFE / LODGE

CAFE_SEATS = 42
CAFE_STAFF = 8
CAFE_VISIT_CHANCE = 0.24
CAFE_TIME_MIN = 0.6
CAFE_TIME_MAX = 1.2


# RESTAURANT

RESTAURANT_SEATS = 55
RESTAURANT_STAFF = 10
RESTAURANT_VISIT_CHANCE = 0.18
RESTAURANT_TIME_MIN = 1.2
RESTAURANT_TIME_MAX = 2.3


# APRES-SKI

APRES_SKI_CAPACITY = 80
APRES_SKI_VISIT_CHANCE = 0.15
APRES_SKI_TIME_MIN = 0.8
APRES_SKI_TIME_MAX = 1.5


# SKI SCHOOL

SKI_SCHOOL_CHANCE = 0.15
CHILD_SKI_SCHOOL_CHANCE = 0.35
NUM_INSTRUCTORS = 6
SKI_SCHOOL_GROUP_SIZE = 8


# FIRST AID

PARAMEDICS = 3
SERIOUS_FALL_CHANCE = 0.20
FIRST_AID_TIME_MIN = 1.0
FIRST_AID_TIME_MAX = 2.0


# OUTPUTS TO TRACK

TRACK_WAIT_TIMES = True
TRACK_QUEUE_LENGTHS = True
TRACK_SLOPE_RUNS = True
TRACK_CAFE_VISITS = True
TRACK_FALLS = True
TRACK_RESTAURANT_VISITS = True
TRACK_APRES_SKI_VISITS = True
TRACK_FIRST_AID = True
TRACK_WEATHER = True
TRACK_AGE_GROUPS = True
TRACK_SKILL_LEVELS = True
TRACK_EQUIPMENT_STATUS = True