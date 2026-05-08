# Ski Resort Simulation

This project is a Python-based simulation of a busy ski resort. It models how skiers and snowboarders move through different resort areas while competing for shared resources such as rentals, lifts, slopes, cafe spaces, restaurant service, and après-ski areas.

The main goal of the project is to analyze visitor flow, congestion, waiting times, and bottlenecks when many visitors are active at the same time.

## Project Overview

The simulation represents a busy ski resort day where visitors enter the resort, move through different areas, repeat activities, lose and recover energy, and eventually leave.

Each visitor is implemented as an independent thread. This allows many visitors to act at the same time, making the simulation closer to a real resort environment where people do not move one by one.

The general visitor flow is:

**Arrive → Rent Equipment → Use Lift → Ski/Snowboard on Slope → Visit Cafe / Restaurant / Après-Ski → Repeat or Exit**

Visitors can repeat slope runs, return to the lift multiple times, recover energy in rest areas, and experience random events such as falls.

## Main Features

- Visitor simulation using Python threads
- Skiers and snowboarders with different behavior
- Rental shop resource
- Lift station resource
- Slope resource
- Cafe resource
- Restaurant and après-ski areas
- Queues for limited-capacity resources
- Shared resource management
- Locks to prevent race conditions
- Visitor energy system
- Repeated slope runs
- Random fall events
- Midday peak arrival period
- Event tracking through StatsManager
- SQLite event logging
- Final statistics summary
- Graph generation using matplotlib

## Operating Systems Concepts

This project applies several Operating Systems concepts.

### Threads

Each visitor runs as an independent thread. This means multiple visitors can move through the simulation at the same time instead of waiting for one visitor to finish before the next one starts.

### Shared Resources

Many visitors compete for the same limited resort resources. These include:

- Rental equipment and staff
- Lift capacity
- Slope capacity
- Cafe capacity
- Restaurant capacity
- Après-ski capacity

### Critical Regions

Some parts of the simulation are critical regions because multiple threads can access and modify the same data at the same time.

Examples include:

- Queue sizes
- Capacity counters
- Visitor statistics
- Event logs
- Database writes

### Locks

Locks are used to protect shared data and prevent race conditions. This makes sure that two visitors cannot incorrectly update the same resource at the same time.

## Design Patterns Used

The project uses three main design patterns: State, Strategy, and Observer.

### State Pattern

The State pattern controls the visitor journey through the resort.

Instead of putting all visitor behavior into one large method, the visitor moves through different states, such as:

- Arriving
- Renting equipment
- Waiting for the lift
- Using the lift
- Going down the slope
- Visiting the cafe
- Visiting the restaurant
- Visiting après-ski
- Exiting the resort

This makes the simulation easier to organize, understand, and extend.

### Strategy Pattern

The Strategy pattern separates the behavior of skiers and snowboarders.

Skiers and snowboarders follow the same general resort flow, but they can behave differently in areas such as:

- Energy loss
- Probability of visiting rest areas
- Decision to continue or leave
- Slope behavior
- Activity patterns

This avoids placing too many if/else statements inside the main visitor logic.

### Observer Pattern

The Observer pattern is used to track simulation events.

When something important happens, such as a queue change, waiting time, completed run, cafe visit, restaurant visit, après-ski visit, or fall, the event is sent to StatsManager.

This keeps the simulation logic separate from the statistics and reporting logic.

## Metrics Tracked

The simulation tracks several metrics to understand congestion and visitor behavior.

### Queue Metrics

- Maximum rental queue
- Maximum lift queue
- Maximum cafe queue
- Maximum restaurant queue
- Maximum après-ski queue
- Maximum slope queue

### Waiting Metrics

- Average rental wait time
- Average lift wait time
- Average cafe wait time
- Average restaurant wait time
- Average après-ski wait time

### Activity Metrics

- Total slope runs
- Total cafe visits
- Total restaurant visits
- Total après-ski visits
- Total fall events

### Visitor Metrics

- Number of skiers
- Number of snowboarders
- Runs completed per visitor
- Energy left after the simulation
- Visitor activity patterns

## Graphs and Output

The simulation generates visual outputs using matplotlib. These graphs help explain the final results and show where congestion happened.

Possible graphs include:

- Main bottleneck queue graph
- Queue length trend graph
- Visitor activity summary
- Visitor type distribution
- Average recorded wait time
- Runs completed vs energy left
- Runs completed vs cafe visits
- Runs completed by visitor type

These graphs support the final analysis by showing how visitors moved through the resort and which resources became the most congested.

## Main Findings

The simulation showed that congestion happens mainly when many visitors need the same limited resource at the same time.

The biggest bottlenecks are usually found in areas that every visitor must use or that visitors return to multiple times, such as:

- Rental shop
- Lift station

Other areas, such as the cafe, restaurant, après-ski, and slopes, depend on capacity settings and visitor behavior. If their capacity is high enough, they may not create serious queues. If capacity is reduced, they can also become bottlenecks.

## Main Conclusion

This simulation demonstrates how concurrency and shared resources can create congestion in a ski resort.

By using threads, locks, design patterns, event tracking, and graphs, the project shows how visitor behavior affects the overall flow of the resort. The results help identify which resources need more capacity or better management to reduce waiting times and improve visitor experience.

## How to Run

First, install the required package:

```bash
pip install -r requirements.txt
