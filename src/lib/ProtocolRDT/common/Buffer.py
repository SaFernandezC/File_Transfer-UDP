from ..utils import MAX_BUFFER_SIZE
from threading import Lock
from bisect import insort


class OrderedBuffer:
    def __init__(self, max_size=MAX_BUFFER_SIZE):
        self.max_size = max_size
        self.buffer = []
        self.lock = Lock()

    def push(self, element, next_expected):
        with self.lock:
            if ((element in self.buffer) or (
                (len(self.buffer) - 1 >= self.max_size) and (
                    next_expected != element[0]))):
                return False
            insort(self.buffer, element)
            return True

    def len(self):
        with self.lock:
            return len(self.buffer)

    def first_element(self):
        with self.lock:
            if(len(self.buffer) > 0):
                return self.buffer[0][0]
            else:
                return None

    def get_first(self):
        with self.lock:
            return self.buffer.pop(0)
