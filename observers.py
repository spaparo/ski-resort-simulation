import os
import matplotlib.pyplot as plt


class StatsManager:
    def __init__(self):
        self.wait_times = {
            "rental": [],
            "lift": [],
            "cafe": []
        }

        self.queue_lengths = {
            "rental": [],
            "lift": [],
            "cafe": []
        }

        self.total_runs = 0
        self.cafe_visits = 0
        self.falls = 0

        self.visitor_types = {
            "skier": 0,
            "snowboarder": 0
        }

        self.visitor_summaries = []

    def update(self, event_type, data=None):
        if event_type == "rental_wait":
            self.wait_times["rental"].append(data)

        elif event_type == "lift_wait":
            self.wait_times["lift"].append(data)

        elif event_type == "cafe_wait":
            self.wait_times["cafe"].append(data)

        elif event_type == "rental_queue":
            self.queue_lengths["rental"].append(data)

        elif event_type == "lift_queue":
            self.queue_lengths["lift"].append(data)

        elif event_type == "cafe_queue":
            self.queue_lengths["cafe"].append(data)

        elif event_type == "run":
            self.total_runs += 1

        elif event_type == "cafe":
            self.cafe_visits += 1

        elif event_type == "fall":
            self.falls += 1

        elif event_type == "visitor_type":
            self.record_visitor_type(data)

        elif event_type == "visitor_summary":
            self.visitor_summaries.append(data)

    def record_visitor_type(self, data):
        visitor_type = data

        if hasattr(data, "visitor_type"):
            visitor_type = data.visitor_type
        elif hasattr(data, "type"):
            visitor_type = data.type

        if visitor_type in self.visitor_types:
            self.visitor_types[visitor_type] += 1

    def average_wait(self, area):
        times = self.wait_times.get(area, [])

        if len(times) == 0:
            return 0

        return sum(times) / len(times)

    def max_queue(self, area):
        queues = self.queue_lengths.get(area, [])

        if len(queues) == 0:
            return 0

        return max(queues)

    def show_summary(self):
        print("\n--- SIMULATION SUMMARY ---")

        print("Average rental wait:", round(self.average_wait("rental"), 2))
        print("Average lift wait:", round(self.average_wait("lift"), 2))
        print("Average cafe wait:", round(self.average_wait("cafe"), 2))

        print("Max rental queue:", self.max_queue("rental"))
        print("Max lift queue:", self.max_queue("lift"))
        print("Max cafe queue:", self.max_queue("cafe"))

        print("Total runs:", self.total_runs)
        print("Cafe visits:", self.cafe_visits)
        print("Falls:", self.falls)
        print("Visitor types:", self.visitor_types)

    def show_graphs(self):
        os.makedirs("graphs", exist_ok=True)

        self.plot_average_wait_times()
        self.plot_max_queue_lengths()
        self.plot_activity_summary()
        self.plot_visitor_type_distribution()
        self.plot_queue_trend()
        self.plot_runs_vs_energy()
        self.plot_runs_vs_cafe_visits()

        print("\nGraphs saved in the 'graphs' folder.")

    def add_bar_labels(self, bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                str(round(height, 2)),
                ha="center",
                va="bottom",
                fontsize=10
            )

    def plot_average_wait_times(self):
        areas = ["rental", "lift", "cafe"]
        averages = [self.average_wait(area) for area in areas]

        plt.figure(figsize=(8, 5))
        bars = plt.bar(
            ["Rental", "Lift", "Cafe"],
            averages
        )

        self.add_bar_labels(bars)

        plt.title("Average Waiting Time by Resort Area", fontsize=15, fontweight="bold")
        plt.xlabel("Area")
        plt.ylabel("Average Wait Time")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig("graphs/average_wait_times.png", dpi=300)
        plt.close()

    def plot_max_queue_lengths(self):
        areas = ["rental", "lift", "cafe"]
        max_queues = [self.max_queue(area) for area in areas]

        plt.figure(figsize=(8, 5))
        bars = plt.bar(
            ["Rental", "Lift", "Cafe"],
            max_queues
        )

        self.add_bar_labels(bars)

        plt.title("Maximum Queue Length by Resort Area", fontsize=15, fontweight="bold")
        plt.xlabel("Area")
        plt.ylabel("Maximum Queue Length")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig("graphs/max_queue_length.png", dpi=300)
        plt.close()

    def plot_activity_summary(self):
        labels = ["Runs", "Cafe Visits", "Falls"]
        values = [self.total_runs, self.cafe_visits, self.falls]

        plt.figure(figsize=(8, 5))
        bars = plt.bar(labels, values)

        self.add_bar_labels(bars)

        plt.title("Simulation Activity Summary", fontsize=15, fontweight="bold")
        plt.xlabel("Activity")
        plt.ylabel("Total Count")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig("graphs/activity_summary.png", dpi=300)
        plt.close()

    def plot_visitor_type_distribution(self):
        labels = ["Skier", "Snowboarder"]
        values = [
            self.visitor_types["skier"],
            self.visitor_types["snowboarder"]
        ]

        plt.figure(figsize=(8, 5))
        bars = plt.bar(labels, values)

        self.add_bar_labels(bars)

        plt.title("Visitor Type Distribution", fontsize=15, fontweight="bold")
        plt.xlabel("Visitor Type")
        plt.ylabel("Number of Visitors")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig("graphs/visitor_type_distribution.png", dpi=300)
        plt.close()

    def plot_queue_trend(self):
        plt.figure(figsize=(10, 6))

        areas = ["rental", "lift", "cafe"]

        for area in areas:
            values = self.queue_lengths[area]

            if len(values) > 0:
                x_values = list(range(1, len(values) + 1))

                plt.plot(
                    x_values,
                    values,
                    marker="o",
                    markersize=3,
                    linewidth=2,
                    label=area.capitalize()
                )

        plt.title("Queue Length Trend During Simulation", fontsize=15, fontweight="bold")
        plt.xlabel("Observation Number")
        plt.ylabel("Queue Length")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("graphs/queue_trend.png", dpi=300)
        plt.close()

    def plot_runs_vs_energy(self):
        if len(self.visitor_summaries) == 0:
            return

        skier_runs = []
        skier_energy = []
        snowboarder_runs = []
        snowboarder_energy = []

        for visitor in self.visitor_summaries:
            visitor_type = visitor.get("type")
            runs = visitor.get("runs", 0)
            energy_left = visitor.get("energy_left", 0)

            if visitor_type == "skier":
                skier_runs.append(runs)
                skier_energy.append(energy_left)

            elif visitor_type == "snowboarder":
                snowboarder_runs.append(runs)
                snowboarder_energy.append(energy_left)

        plt.figure(figsize=(8, 5))

        plt.scatter(
            skier_runs,
            skier_energy,
            label="Skier",
            alpha=0.7
        )

        plt.scatter(
            snowboarder_runs,
            snowboarder_energy,
            label="Snowboarder",
            alpha=0.7
        )

        plt.title("Runs Completed vs Energy Left", fontsize=15, fontweight="bold")
        plt.xlabel("Runs Completed")
        plt.ylabel("Energy Left")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("graphs/runs_vs_energy.png", dpi=300)
        plt.close()

    def plot_runs_vs_cafe_visits(self):
        if len(self.visitor_summaries) == 0:
            return

        skier_runs = []
        skier_cafe = []
        snowboarder_runs = []
        snowboarder_cafe = []

        for visitor in self.visitor_summaries:
            visitor_type = visitor.get("type")
            runs = visitor.get("runs", 0)
            cafe_visits = visitor.get("cafe_visits", 0)

            if visitor_type == "skier":
                skier_runs.append(runs)
                skier_cafe.append(cafe_visits)

            elif visitor_type == "snowboarder":
                snowboarder_runs.append(runs)
                snowboarder_cafe.append(cafe_visits)

        plt.figure(figsize=(8, 5))

        plt.scatter(
            skier_runs,
            skier_cafe,
            label="Skier",
            alpha=0.7
        )

        plt.scatter(
            snowboarder_runs,
            snowboarder_cafe,
            label="Snowboarder",
            alpha=0.7
        )

        plt.title("Runs Completed vs Cafe Visits", fontsize=15, fontweight="bold")
        plt.xlabel("Runs Completed")
        plt.ylabel("Cafe Visits")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("graphs/runs_vs_cafe_visits.png", dpi=300)
        plt.close()
