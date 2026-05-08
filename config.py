# SKI RESORT SIMULATION CONFIG
# Based on Val Thorens, France

# SIMULATION SIZE

NUM_VISITORS = 2500


# ARRIVAL PATTERN

ARRIVAL_INTERVAL_MIN = 0.01
ARRIVAL_INTERVAL_MAX = 0.04


# RENTAL SHOP

NUM_SKIS = 1300
NUM_SNOWBOARDS = 1200
RENTAL_STAFF = 45
RENTAL_TIME_MIN = 0.25
RENTAL_TIME_MAX = 0.7


# LIFT SYSTEM

NUM_LIFTS = 12
LIFT_CAPACITY = 12
LIFT_RIDE_TIME_MIN = 0.25
LIFT_RIDE_TIME_MAX = 0.7


# SLOPES

SLOPE_CONFIGS = [
    {
        "name": "Green",
        "difficulty": "beginner",
        "capacity": 320,
        "time_min": 0.4,
        "time_max": 0.9,
        "fall_modifier": 0.7
    },
    {
        "name": "Blue",
        "difficulty": "intermediate",
        "capacity": 420,
        "time_min": 0.5,
        "time_max": 1.0,
        "fall_modifier": 1.0
    },
    {
        "name": "Red",
        "difficulty": "advanced",
        "capacity": 360,
        "time_min": 0.6,
        "time_max": 1.2,
        "fall_modifier": 1.3
    },
    {
        "name": "Black",
        "difficulty": "expert",
        "capacity": 220,
        "time_min": 0.7,
        "time_max": 1.4,
        "fall_modifier": 1.7
    },
    {
        "name": "Orange",
        "difficulty": "snow_park",
        "capacity": 260,
        "time_min": 0.6,
        "time_max": 1.3,
        "fall_modifier": 1.5
    }
]

NUM_SLOPES = len(SLOPE_CONFIGS)
SLOPE_CAPACITY = 250
SLOPE_TIME_MIN = 0.5
SLOPE_TIME_MAX = 1.2

FALL_CHANCE = 0.05
FALL_DELAY = 0.25


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

PEAK_START_VISITOR = 700
PEAK_END_VISITOR = 1600

PEAK_ARRIVAL_INTERVAL_MIN = 0.005
PEAK_ARRIVAL_INTERVAL_MAX = 0.02

PEAK_SERVICE_SLOWDOWN_FACTOR = 1.08


# DAY PHASES

LUNCH_START_VISITOR = 900
LUNCH_END_VISITOR = 1700

LAST_LIFT_VISITOR = 2200
RESORT_CLOSE_VISITOR = 2500


# CAFE / LODGE

CAFE_SEATS = 320
CAFE_STAFF = 35
CAFE_VISIT_CHANCE = 0.24
CAFE_TIME_MIN = 0.25
CAFE_TIME_MAX = 0.6


# RESTAURANT

RESTAURANT_SEATS = 450
RESTAURANT_STAFF = 45
RESTAURANT_VISIT_CHANCE = 0.18
RESTAURANT_TIME_MIN = 0.5
RESTAURANT_TIME_MAX = 1.1


# APRES-SKI

APRES_SKI_CAPACITY = 600
APRES_SKI_VISIT_CHANCE = 0.15
APRES_SKI_TIME_MIN = 0.35
APRES_SKI_TIME_MAX = 0.8


# SKI SCHOOL

SKI_SCHOOL_CHANCE = 0.15
CHILD_SKI_SCHOOL_CHANCE = 0.35
NUM_INSTRUCTORS = 35
SKI_SCHOOL_GROUP_SIZE = 8


# FIRST AID

PARAMEDICS = 12
SERIOUS_FALL_CHANCE = 0.20
FIRST_AID_TIME_MIN = 0.4
FIRST_AID_TIME_MAX = 0.9


# EQUIPMENT RETURN

RETURN_STAFF = 35
RETURN_TIME_MIN = 0.2
RETURN_TIME_MAX = 0.5


# STAFF FATIGUE / STAFF SHIFTS

STAFF_FATIGUE_MULTIPLIER = 1.12
LUNCH_SERVICE_SLOWDOWN_FACTOR = 1.15
CLOSING_SERVICE_SLOWDOWN_FACTOR = 1.20


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