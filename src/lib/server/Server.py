from .Listener import Listener
import logging
import signal


class Server:
    def __init__(self, port, host, dir):
        self.listener = Listener(port, host, dir)

    def start(self):
        signal.signal(signal.SIGTSTP, self.handler)
        self.listener.start()
        working = True
        try:
            while (working):
                print("Press 'q' to quit.")
                if (input() == "q"):
                    working = False
        except EOFError:
            logging.info("SERVER exited by CTRL + D.")
        except KeyboardInterrupt:
            logging.info("SERVER exited by CTRL + C.")
        self.quit()

    def handler(self, signum, frame):
        logging.info("SERVER exited by signal {}".format(signum))
        self.quit()
        exit(0)

    def quit(self):
        self.listener.stop()
        self.listener.join()
