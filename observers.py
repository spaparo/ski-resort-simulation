import os
import matplotlib.pyplot as plt
import threading


class StatsManager:
    def __init__(self):
        self.lock = threading.Lock()

        self.wait_times = {
            "rental": [],
            "lift": [],
            "cafe": [],
            "restaurant": [],
            "apres_ski": [],
            "first_aid": [],
            "ski_school": [],
            "equipment_return": []
        }

        self.queue_lengths = {
            "rental": [],
            "lift": [],
            "cafe": [],
            "restaurant": [],
            "apres_ski": [],
            "first_aid": [],
            "ski_school": [],
            "equipment_return": [],
            "slope": []
        }

        self.total_runs = 0
        self.cafe_visits = 0
        self.restaurant_visits = 0
        self.apres_ski_visits = 0
        self.falls = 0
        self.serious_falls = 0
        self.first_aid_visits = 0
        self.ski_school_visitors = 0
        self.closing_affected_visitors = 0

        self.visitor_types = {
            "skier": 0,
            "snowboarder": 0
        }

        self.weather_counts = {
            "sunny": 0,
            "snowy": 0,
            "windy": 0,
            "foggy": 0
        }

        self.current_weather = None

        self.falls_by_weather = {
            "sunny": 0,
            "snowy": 0,
            "windy": 0,
            "foggy": 0
        }

        self.serious_falls_by_weather = {
            "sunny": 0,
            "snowy": 0,
            "windy": 0,
            "foggy": 0
        }

        self.first_aid_by_weather = {
            "sunny": 0,
            "snowy": 0,
            "windy": 0,
            "foggy": 0
        }

        self.age_groups = {
            "child": 0,
            "adult": 0,
            "senior": 0
        }

        self.skill_levels = {
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0
        }

        self.equipment_status = {
            "own_equipment": 0,
            "rental_equipment": 0
        }

        self.slope_usage = {
            "Green": 0,
            "Blue": 0,
            "Red": 0,
            "Black": 0,
            "Orange": 0
        }

        self.slope_closures = 0
        self.closed_slopes = {}

        self.equipment_return_queues = []
        self.visitor_summaries = []

    def update(self, event_type, data=None):
        # Critical region: statistics are updated by multiple visitor threads
        with self.lock:
            if event_type == "rental_wait":
                self.wait_times["rental"].append(data)

            elif event_type == "lift_wait":
                self.wait_times["lift"].append(data)

            elif event_type == "cafe_wait":
                self.wait_times["cafe"].append(data)

            elif event_type == "restaurant_wait":
                self.wait_times["restaurant"].append(data)

            elif event_type == "apres_wait":
                self.wait_times["apres_ski"].append(data)

            elif event_type == "first_aid_wait":
                self.wait_times["first_aid"].append(data)

            elif event_type == "instructor_wait":
                self.wait_times["ski_school"].append(data)

            elif event_type == "return_wait":
                self.wait_times["equipment_return"].append(data)

            elif event_type == "rental_queue":
                self.queue_lengths["rental"].append(data)

            elif event_type == "lift_queue":
                self.queue_lengths["lift"].append(data)

            elif event_type == "cafe_queue":
                self.queue_lengths["cafe"].append(data)

            elif event_type == "restaurant_queue":
                self.queue_lengths["restaurant"].append(data)

            elif event_type == "apres_queue":
                self.queue_lengths["apres_ski"].append(data)

            elif event_type == "first_aid_queue":
                self.queue_lengths["first_aid"].append(data)

            elif event_type == "first_aid_priority_queue":
                self.queue_lengths["first_aid"].append(data)

            elif event_type == "instructor_queue":
                self.queue_lengths["ski_school"].append(data)

            elif event_type == "return_queue":
                self.queue_lengths["equipment_return"].append(data)
                self.equipment_return_queues.append(data)

            elif event_type == "slope_queue":
                self.queue_lengths["slope"].append(data)

            elif event_type == "run":
                self.total_runs += 1

            elif event_type == "slope_used":
                if data not in self.slope_usage:
                    self.slope_usage[data] = 0
                self.slope_usage[data] += 1

            elif event_type == "cafe":
                self.cafe_visits += 1

            elif event_type == "restaurant":
                self.restaurant_visits += 1

            elif event_type == "apres_ski":
                self.apres_ski_visits += 1

            elif event_type == "fall":
                self.falls += 1
                self._record_weather_event(self.falls_by_weather)

            elif event_type == "serious_fall":
                self.serious_falls += 1
                self._record_weather_event(self.serious_falls_by_weather)

            elif event_type == "first_aid":
                self.first_aid_visits += 1
                self._record_weather_event(self.first_aid_by_weather)

            elif event_type == "visitor_type":
                self.record_visitor_type(data)

            elif event_type == "visitor_summary":
                self.visitor_summaries.append(data)

            elif event_type == "weather":
                self.current_weather = data
                if data in self.weather_counts:
                    self.weather_counts[data] += 1

            elif event_type == "age_group":
                if data in self.age_groups:
                    self.age_groups[data] += 1

            elif event_type == "skill_level":
                if data in self.skill_levels:
                    self.skill_levels[data] += 1

            elif event_type == "own_equipment":
                self.equipment_status["own_equipment"] += 1

            elif event_type == "rental_equipment":
                self.equipment_status["rental_equipment"] += 1

            elif event_type == "ski_school":
                self.ski_school_visitors += 1

            elif event_type == "closing_affected":
                self.closing_affected_visitors += 1

            elif event_type == "slope_closed":
                self.slope_closures += 1
                if data not in self.closed_slopes:
                    self.closed_slopes[data] = 0
                self.closed_slopes[data] += 1

    def _record_weather_event(self, target_dict):
        weather = self.current_weather or "sunny"
        if weather in target_dict:
            target_dict[weather] += 1

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
        print("Average restaurant wait:", round(self.average_wait("restaurant"), 2))
        print("Average après-ski wait:", round(self.average_wait("apres_ski"), 2))
        print("Average first-aid wait:", round(self.average_wait("first_aid"), 2))
        print("Average ski school wait:", round(self.average_wait("ski_school"), 2))
        print("Average equipment return wait:", round(self.average_wait("equipment_return"), 2))

        print("Max rental queue:", self.max_queue("rental"))
        print("Max lift queue:", self.max_queue("lift"))
        print("Max cafe queue:", self.max_queue("cafe"))
        print("Max restaurant queue:", self.max_queue("restaurant"))
        print("Max après-ski queue:", self.max_queue("apres_ski"))
        print("Max first-aid queue:", self.max_queue("first_aid"))
        print("Max ski school queue:", self.max_queue("ski_school"))
        print("Max equipment return queue:", self.max_queue("equipment_return"))
        print("Max slope queue:", self.max_queue("slope"))

        print("Total runs:", self.total_runs)
        print("Cafe visits:", self.cafe_visits)
        print("Restaurant visits:", self.restaurant_visits)
        print("Après-ski visits:", self.apres_ski_visits)
        print("Falls:", self.falls)
        print("Serious falls:", self.serious_falls)
        print("First-aid visits:", self.first_aid_visits)
        print("Ski school visitors:", self.ski_school_visitors)
        print("Visitors affected by closing:", self.closing_affected_visitors)

        print("Visitor types:", self.visitor_types)
        print("Weather:", self.weather_counts)
        print("Age groups:", self.age_groups)
        print("Skill levels:", self.skill_levels)
        print("Equipment status:", self.equipment_status)
        print("Slope usage:", self.slope_usage)
        print("Slope closures:", self.slope_closures)
        print("Closed slope events:", self.closed_slopes)

    def show_graphs(self):
        os.makedirs("graphs", exist_ok=True)

        self.plot_main_bottleneck()
        self.plot_queue_trend()
        self.plot_visitor_profiles()
        self.plot_slope_usage()
        self.plot_activity_breakdown()
        self.plot_risk_by_weather()

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

    def add_caption(self, text):
        plt.figtext(
            0.5,
            -0.02,
            text,
            ha="center",
            fontsize=10,
            wrap=True
        )

    def save_graph(self, filename):
        plt.tight_layout()
        plt.savefig(f"graphs/{filename}", dpi=300, bbox_inches="tight")
        plt.close()

    def plot_main_bottleneck(self):
        areas = [
            "Rental",
            "Lift",
            "Cafe",
            "Restaurant",
            "Après-ski",
            "First Aid",
            "Ski School",
            "Return",
            "Slope"
        ]

        keys = [
            "rental",
            "lift",
            "cafe",
            "restaurant",
            "apres_ski",
            "first_aid",
            "ski_school",
            "equipment_return",
            "slope"
        ]

        max_queues = [self.max_queue(area) for area in keys]

        plt.figure(figsize=(12, 6))
        bars = plt.bar(areas, max_queues)
        self.add_bar_labels(bars)

        plt.title("Main Bottleneck: Maximum Queue Length by Resort Area", fontsize=15)
        plt.xlabel("Resort Area")
        plt.ylabel("Maximum Queue Length")
        plt.xticks(rotation=25)
        plt.grid(axis="y", alpha=0.3)

        self.add_caption(
            "Interpretation: This graph identifies which shared resource produced the largest queue and therefore acted as the main bottleneck."
        )

        self.save_graph("01_main_bottleneck_queue.png")

    def plot_queue_trend(self):
        areas = [
            "rental",
            "lift",
            "cafe",
            "restaurant",
            "first_aid",
            "equipment_return",
            "apres_ski",
            "ski_school",
            "slope"
        ]

        plt.figure(figsize=(12, 6))

        for area in areas:
            values = self.queue_lengths.get(area, [])

            if len(values) > 0:
                x_values = list(range(1, len(values) + 1))
                label = area.replace("_", " ").title()

                plt.plot(
                    x_values,
                    values,
                    linewidth=2,
                    label=label
                )

        plt.title("Queue Length Trend During the Simulation", fontsize=15)
        plt.xlabel("Queue Observation Number")
        plt.ylabel("Queue Length")
        plt.legend()
        plt.grid(True, alpha=0.3)

        self.add_caption(
            "Interpretation: This line graph shows when congestion builds up and whether queues clear or remain high during the simulation."
        )

        self.save_graph("02_queue_growth_trend.png")

    def plot_visitor_profiles(self):
        age_labels = ["child", "adult", "senior"]
        visitor_labels = ["skier", "snowboarder"]

        profile_counts = {
            "skier": {"child": 0, "adult": 0, "senior": 0},
            "snowboarder": {"child": 0, "adult": 0, "senior": 0}
        }

        for visitor in self.visitor_summaries:
            visitor_type = visitor.get("type")
            age_group = visitor.get("age_group")

            if visitor_type in profile_counts and age_group in profile_counts[visitor_type]:
                profile_counts[visitor_type][age_group] += 1

        skier_values = [profile_counts["skier"][age] for age in age_labels]
        snowboarder_values = [profile_counts["snowboarder"][age] for age in age_labels]

        x_positions = list(range(len(age_labels)))
        width = 0.35

        plt.figure(figsize=(10, 6))

        bars1 = plt.bar(
            [x - width / 2 for x in x_positions],
            skier_values,
            width,
            label="Skier"
        )

        bars2 = plt.bar(
            [x + width / 2 for x in x_positions],
            snowboarder_values,
            width,
            label="Snowboarder"
        )

        self.add_bar_labels(bars1)
        self.add_bar_labels(bars2)

        plt.title("Visitor Profiles by Type and Age Group", fontsize=15)
        plt.xlabel("Age Group")
        plt.ylabel("Number of Visitors")
        plt.xticks(x_positions, [age.title() for age in age_labels])
        plt.legend()
        plt.grid(axis="y", alpha=0.3)

        self.add_caption(
            "Interpretation: This graph shows the visitor mix by age and type, which matters because age affects energy, fall risk, and break behavior."
        )

        self.save_graph("03_visitor_profiles.png")

    def plot_slope_usage(self):
        labels = list(self.slope_usage.keys())
        values = [self.slope_usage[label] for label in labels]

        if sum(values) == 0:
            labels = ["Green", "Blue", "Red", "Black", "Orange"]
            values = [0, 0, 0, 0, 0]

        plt.figure(figsize=(10, 6))
        bars = plt.barh(labels, values)

        for bar in bars:
            width = bar.get_width()
            plt.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                str(round(width, 2)),
                va="center",
                fontsize=10
            )

        plt.title("Slope Usage by Difficulty", fontsize=15)
        plt.xlabel("Number of Completed Runs")
        plt.ylabel("Slope")
        plt.grid(axis="x", alpha=0.3)

        self.add_caption(
            "Interpretation: This graph shows which slopes were used most. It helps evaluate whether demand concentrates on easier, advanced, or extreme ungroomed slopes."
        )

        self.save_graph("04_slope_usage_by_difficulty.png")

    def plot_activity_breakdown(self):
        labels = [
            "Slope Runs",
            "Cafe",
            "Restaurant",
            "Après-ski",
            "First Aid"
        ]

        values = [
            self.total_runs,
            self.cafe_visits,
            self.restaurant_visits,
            self.apres_ski_visits,
            self.first_aid_visits
        ]

        plt.figure(figsize=(8, 8))

        if sum(values) == 0:
            values = [1]
            labels = ["No activity recorded"]

        wedges, texts, autotexts = plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"width": 0.45}
        )

        plt.title("Visitor Activity Breakdown", fontsize=15)

        self.add_caption(
            "Interpretation: This donut chart summarizes how visitor activity was divided across skiing, recovery, food, social stops, and emergency care."
        )

        self.save_graph("05_activity_breakdown.png")

    def plot_risk_by_weather(self):
        weather_labels = ["sunny", "snowy", "windy", "foggy"]

        normal_falls = [
            max(0, self.falls_by_weather[w] - self.serious_falls_by_weather[w])
            for w in weather_labels
        ]

        serious_falls = [
            self.serious_falls_by_weather[w]
            for w in weather_labels
        ]

        first_aid = [
            self.first_aid_by_weather[w]
            for w in weather_labels
        ]

        x_positions = list(range(len(weather_labels)))

        plt.figure(figsize=(10, 6))

        plt.bar(
            x_positions,
            normal_falls,
            label="Minor Falls"
        )

        plt.bar(
            x_positions,
            serious_falls,
            bottom=normal_falls,
            label="Serious Falls"
        )

        combined_bottom = [
            normal_falls[i] + serious_falls[i]
            for i in range(len(weather_labels))
        ]

        plt.bar(
            x_positions,
            first_aid,
            bottom=combined_bottom,
            label="First Aid Visits"
        )

        plt.title("Falls and First-Aid Outcomes by Weather", fontsize=15)
        plt.xlabel("Weather")
        plt.ylabel("Number of Events")
        plt.xticks(x_positions, [w.title() for w in weather_labels])
        plt.legend()
        plt.grid(axis="y", alpha=0.3)

        self.add_caption(
            "Interpretation: This stacked chart connects weather conditions to risk. Foggy, snowy, or windy weather should place more pressure on first aid and slope safety."
        )

        self.save_graph("06_risk_and_first_aid_by_weather.png")