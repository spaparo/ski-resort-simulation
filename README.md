# Ski Resort Simulation

This project simulates a busy ski resort using Python threads. The goal is to model how skiers and snowboarders move through shared resort resources and identify where congestion happens when many visitors are active at the same time.

## Project Overview

The simulation represents one busy ski day with 250 visitors. Each visitor acts as an independent thread and moves through the resort flow:

Arrive → Rent → Lift → Slope → Cafe / Repeat → Exit

Visitors can repeat slope runs, lose energy, recover at the cafe, and experience random falls. A midday peak arrival period is also included to create more realistic congestion.

## Main Features

- 250 visitor threads
- Skiers and snowboarders
- Rental shop, lift station, slope, and cafe resources
- Queues and limited capacity for shared resources
- Locks to protect shared data and prevent race conditions
- Midday peak arrival period
- Energy loss after slope runs
- Cafe recovery
- Random fall events
- SQLite event logging
- StatsManager for tracking results
- Graph generation using matplotlib

## Operating Systems Concepts

The main Operating Systems concepts used in this project are:

- **Threads:** each visitor is an independent thread.
- **Shared resources:** visitors compete for rental equipment, lift capacity, cafe space, and slope access.
- **Critical regions:** queues, capacity counts, database writes, and statistics updates must be protected.
- **Locks:** locks control access to shared data and prevent race conditions.

## Design Patterns Used

### State Pattern

The State pattern controls the visitor journey. Each visitor moves through different stages such as arriving, renting, waiting for the lift, riding the lift, going down the slope, visiting the cafe, and exiting.

### Strategy Pattern

The Strategy pattern separates skier and snowboarder behavior. Skiers and snowboarders follow the same general resort flow, but they can differ in energy use, cafe probability, and leaving decisions.

### Observer Pattern

The Observer pattern is used for tracking simulation events. When something important happens, such as a queue change, waiting time, completed slope run, cafe visit, or fall, the StatsManager records it for the final results and graphs.

## Final Run Results

The final simulation run used:

- Visitors: 250
- Slope runs: 756
- Cafe visits: 181
- Falls: 42
- Skiers: 129
- Snowboarders: 121
- Max rental queue: 66
- Max lift queue: 53
- Max cafe queue: 4
- Max slope queue: 0
- Average rental wait: 4.21 seconds
- Average lift wait: 1.04 seconds
- Average cafe wait: 0.02 seconds

## Main Conclusion

The rental shop and lift station were the main congestion points.

The rental shop was the strongest bottleneck because every visitor needs equipment before entering the rest of the resort. The lift was the second bottleneck because visitors reuse it after each slope run. The cafe and slope had enough capacity in this simulation run.

## How to Run

First, install the required package:

```bash
pip install -r requirements.txt
