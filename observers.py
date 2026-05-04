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
        import matplotlib.pyplot as plt
        import os

        os.makedirs("graphs", exist_ok=True)

        areas = ["rental", "lift", "cafe"]
        max_queues = [self.max_queue(area) for area in areas]

        # 1. Max queue length bar chart
        plt.figure()
        plt.bar(areas, max_queues)
        plt.title("Maximum Queue Length by Area")
        plt.xlabel("Area")
        plt.ylabel("Max Queue Length")
        plt.savefig("graphs/max_queue_length.png")
        plt.show()

        # 2. Activity summary bar chart
        plt.figure()
        plt.bar(
            ["Runs", "Cafe Visits", "Falls"],
            [self.total_runs, self.cafe_visits, self.falls]
        )
        plt.title("Simulation Activity Summary")
        plt.ylabel("Count")
        plt.savefig("graphs/activity_summary.png")
        plt.show()

        # 3. Visitor type distribution bar chart
        plt.figure()
        plt.bar(
            list(self.visitor_types.keys()),
            list(self.visitor_types.values())
        )
        plt.title("Visitor Type Distribution")
        plt.xlabel("Visitor Type")
        plt.ylabel("Number of Visitors")
        plt.savefig("graphs/visitor_types.png")
        plt.show()

        # 4. Line graph: queue length trend
        plt.figure()
        for area in areas:
            values = self.queue_lengths[area]
            if len(values) > 0:
                x = list(range(1, len(values) + 1))
                plt.plot(x, values, marker="o", label=area)

        plt.title("Queue Length Trend During Simulation")
        plt.xlabel("Observation Number")
        plt.ylabel("Queue Length")
        plt.legend()
        plt.savefig("graphs/queue_trend.png")
        plt.show()

        # 5. Scatter plot: runs completed vs energy left
        if len(self.visitor_summaries) > 0:
            skier_runs = []
            skier_energy = []
            snowboarder_runs = []
            snowboarder_energy = []

            for visitor in self.visitor_summaries:
                if visitor["type"] == "skier":
                    skier_runs.append(visitor["runs"])
                    skier_energy.append(visitor["energy_left"])
                else:
                    snowboarder_runs.append(visitor["runs"])
                    snowboarder_energy.append(visitor["energy_left"])

            plt.figure()
            plt.scatter(skier_runs, skier_energy, label="Skier")
            plt.scatter(snowboarder_runs, snowboarder_energy, label="Snowboarder")
            plt.title("Runs Completed vs Energy Left")
            plt.xlabel("Runs Completed")
            plt.ylabel("Energy Left")
            plt.legend()
            plt.savefig("graphs/runs_vs_energy.png")
            plt.show()

        # 6. Scatter plot: runs completed vs cafe visits
        if len(self.visitor_summaries) > 0:
            skier_runs = []
            skier_cafe = []
            snowboarder_runs = []
            snowboarder_cafe = []

            for visitor in self.visitor_summaries:
                if visitor["type"] == "skier":
                    skier_runs.append(visitor["runs"])
                    skier_cafe.append(visitor["cafe_visits"])
                else:
                    snowboarder_runs.append(visitor["runs"])
                    snowboarder_cafe.append(visitor["cafe_visits"])

            plt.figure()
            plt.scatter(skier_runs, skier_cafe, label="Skier")
            plt.scatter(snowboarder_runs, snowboarder_cafe, label="Snowboarder")
            plt.title("Runs Completed vs Cafe Visits")
            plt.xlabel("Runs Completed")
            plt.ylabel("Cafe Visits")
            plt.legend()
            plt.savefig("graphs/runs_vs_cafe.png")
            plt.show()
