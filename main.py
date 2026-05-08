from resort import Resort


def main():
    print("Starting Full Ski Resort Simulation...")
    print("Visitors: 2500")

    resort = Resort()
    resort.start_simulation()

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()