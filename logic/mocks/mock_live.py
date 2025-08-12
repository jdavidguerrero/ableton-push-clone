import random, threading, time

class MockLive:
    def __init__(self, state): self.state = state
    def start(self):
        self.state.init_project(8, 12)  # 8 tracks x 12 scenes (como tu demo)
        threading.Thread(target=self._animate, daemon=True).start()
    def _animate(self):
        while True:
            t = random.randrange(8)
            s = random.randrange(12)
            st = random.choice(["empty","playing","queued","recording"])
            self.state.set_clip_status(t, s, st)
            time.sleep(0.6)