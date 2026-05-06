import random
from resort import Resort


def main():
    random.seed(42)

    print("Starting Ski Resort Simulation...\n")

    resort = Resort()
    resort.start_simulation()

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()