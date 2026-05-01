from observers import StatsManager


class FakeVisitor:
    def __init__(self, visitor_id, resort):
        self.visitor_id = visitor_id
        self.resort = resort

    def start(self):
        print(f"Visitor {self.visitor_id} started")

        self.resort.stats.update("visitor_type", "skier")
        self.resort.stats.update("rental_wait", 2)
        self.resort.stats.update("rental_queue", 3)
        self.resort.stats.update("lift_wait", 5)
        self.resort.stats.update("lift_queue", 4)
        self.resort.stats.update("run", 1)
        self.resort.stats.update("cafe", 1)

    def join(self):
        print(f"Visitor {self.visitor_id} finished")


class Resort:
    def __init__(self):
        self.stats = StatsManager()
        self.visitors = []
        self.is_open = False

    def create_resources(self):
        # This will connect to Marie's resource classes later
        pass

    def create_visitors(self):
        # Using fake visitors until Sofia finishes Visitor class
        self.visitors = [FakeVisitor(i, self) for i in range(5)]

    def start_threads(self):
        for visitor in self.visitors:
            visitor.start()

    def join_threads(self):
        for visitor in self.visitors:
            visitor.join()

    def start_simulation(self):
        self.is_open = True
        self.create_resources()
        self.create_visitors()
        self.start_threads()
        self.join_threads()
        self.is_open = False
        self.stats.show_summary()