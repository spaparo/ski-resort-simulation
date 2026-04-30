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