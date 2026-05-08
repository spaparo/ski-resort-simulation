import random
from resort import Resort
from config import USE_RANDOM_SEED, RANDOM_SEED, RUN_MODE


def main():
    if USE_RANDOM_SEED:
        random.seed(RANDOM_SEED)

    print("Starting Full Ski Resort Simulation...")
    print(f"Run mode: {RUN_MODE}")

    resort = Resort()
    resort.start_simulation()

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()