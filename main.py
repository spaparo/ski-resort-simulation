from resort import Resort
from config import NUM_VISITORS


def main():
    print("Starting Full Ski Resort Simulation...")
    print(f"Visitors: {NUM_VISITORS}")

    resort = Resort()
    resort.start_simulation()

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()