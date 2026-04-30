import threading
from collections import deque

class RentalShop:
    def __init__(self):
        self.skis_available = 45
        self.snowboards_available = 30
        self.staff_available = 4

        self.queue = deque()
        self.lock = threading.Lock()

    def rent_equipment(self, visitor):
        with self.lock:
            if visitor.type == "skier" and self.skis_available > 0  and self.staff_available > 0:
                self.skis_available -= 1
                self.staff_available -= 1
                return True
            elif visitor.type == "snowboarder" and self.snowboards_available > 0 and self.staff_available > 0:
                self.snowboards_available -= 1
                self.staff_available -= 1
                return True
            else:
                self.queue.append(visitor)
                return False

    class LiftStation:
        def __init__(self):
            self.capacity = 18
            self.current = 0
            self.queue = deque()
            self.lock = threading.Lock()

        def use_lift(self, visitor):
            with self.lock:
                if self.current < self.capacity:
                    self.current += 1
                    return True
                else:
                    self.queue.append(visitor)
                    return False