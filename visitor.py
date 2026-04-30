from threading import Thread
import time
from states import ArrivingState
from strategies import SkierStrategy, SnowboarderStrategy

class Visitor(Thread):
    def __init__(self, visitor_id, visitor_type):
        self.visitor_id = visitor_id
        self.visitor_type = visitor_type
        self.energy = 100
        self.runs_completed = 0
        self.cafe_visits = 0
        self.current_state = None  # set later

        if visitor_type == "skier":
            self.strategy = SkierStrategy()
        else:
            self.strategy = SnowboarderStrategy()


        self.current_state = ArrivingState()

        Thread.__init__(self, name=f"Thread-{visitor_id}", daemon=True)

    def log(self, message):
        print(f"[{self.visitor_id} | {self.visitor_type}] {message}", flush=True)

    def run(self):
        while self.current_state is not None:
            next_state = self.current_state.handle(self)
            self.current_state = next_state

