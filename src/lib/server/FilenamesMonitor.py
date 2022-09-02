import os
from threading import Lock


class FilenamesMonitor:
    def __init__(self):
        self.blocked_names = []
        self.lock = Lock()

    def lock_file(self, filename):
        with self.lock:
            path, extension = os.path.splitext(filename)
            i = 1

            while os.path.exists(filename) or filename in self.blocked_names:
                filename = path+"("+str(i)+")"+extension
                i += 1

            self.blocked_names.append(filename)
            return filename

    def unlock_file(self, filename):
        with self.lock:
            self.blocked_names.remove(filename)

    def is_locked(self, filename):
        with self.lock:
            return filename in self.blocked_names
