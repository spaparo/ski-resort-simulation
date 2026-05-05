from threading import Thread
import time

from fontTools.misc import visitor

from states import ArrivingState
from strategies import SkierStrategy, SnowboarderStrategy

class Visitor(Thread):
    def __init__(self, visitor_id, visitor_type, resort=None):
        self.visitor_id = visitor_id
        self.visitor_type = visitor_type
        self.resort = resort
        self.energy = 100
        self.runs_completed = 0
        self.cafe_visits = 0
        self.current_state = None
        self.has_equipment = False

        if visitor_type == "skier":
            self.strategy = SkierStrategy()
        else:
            self.strategy = SnowboarderStrategy()


        self.current_state = ArrivingState()

        Thread.__init__(self, name=f"Thread-{visitor_id}", daemon=True)

    def log(self, message):
        print(f"[{self.visitor_id} | {self.visitor_type}] {message}", flush=True)

    def run(self):
        self.log("thread started.")

        try:
            while self.current_state is not None:
                next_state = self.current_state.handle(self)
                self.current_state = next_state

        except Exception as e:
            self.log(f"error occurred: {e}")

        finally:
            self.log("thread ended.")

if __name__ == "__main__":

    visitors = [
        Visitor("V-001", "skier"),       # resort is None for now
        Visitor("V-002", "snowboarder"),
        Visitor("V-003", "skier"),
    ]

    for v in visitors:
        v.start()
        time.sleep(0.1)

    for v in visitors:
        v.join()