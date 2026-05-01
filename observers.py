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

    def update(self, event_type, data):
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
            if data in self.visitor_types:
                self.visitor_types[data] += 1

    def average_wait(self, area):
        times = self.wait_times[area]

        if len(times) == 0:
            return 0

        return sum(times) / len(times)

    def max_queue(self, area):
        queues = self.queue_lengths[area]

        if len(queues) == 0:
            return 0

        return max(queues)

    def show_summary(self):
        print("\n--- SIMULATION SUMMARY ---")
        print("Average rental wait:", self.average_wait("rental"))
        print("Average lift wait:", self.average_wait("lift"))
        print("Average cafe wait:", self.average_wait("cafe"))

        print("Max rental queue:", self.max_queue("rental"))
        print("Max lift queue:", self.max_queue("lift"))
        print("Max cafe queue:", self.max_queue("cafe"))

        print("Total runs:", self.total_runs)
        print("Cafe visits:", self.cafe_visits)
        print("Falls:", self.falls)
        print("Visitor types:", self.visitor_types)