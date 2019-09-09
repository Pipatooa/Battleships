import threading


class ThreadedTask(threading.Thread):
    def __init__(self, task, *args, **kwargs):
        # Construct thread
        threading.Thread.__init__(self)
        self.daemon = True

        # Store task and arguments
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Starts running task on created thread"""

        self.task(*self.args, **self.kwargs)
