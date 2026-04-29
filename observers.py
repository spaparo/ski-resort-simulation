class StatsManager:
    def __init__(self):
        self.wait_times = {
            "lift": [],
            "rental": [],
            "cafe": []
        }
        self.runs = 0
        self.cafe_visits = 0

    def update(self, event_type, data):
        if event_type == "lift_wait":
            self.wait_times["lift"].append(data)

        elif event_type == "rental_wait":
            self.wait_times["rental"].append(data)

        elif event_type == "cafe_wait":
            self.wait_times["cafe"].append(data)

        elif event_type == "run":
            self.runs += 1

        elif event_type == "cafe":
            self.cafe_visits += 1