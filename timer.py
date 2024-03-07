import asyncio
class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.timer_task = None
        self.expired = False

    def start(self):
        self.expired = False
        self.timer_task = asyncio.create_task(self._timer())

    async def _timer(self):
        await asyncio.sleep(self.duration)
        self.expired = True

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        if self.timer_task:
            self.timer_task.cancel()
            self.expired = False

    def has_expired(self):
        return self.expired
