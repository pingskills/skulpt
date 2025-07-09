from time import time

class DeltaTimer:
    def __init__(self, fps=60):
        """
        fps: target frames per second for throttling
        """
        self.frame_target = 1.0 / fps
        self._last_time   = time()
        self._frame_start = None
        self._paused      = False

    def __repr__(self):
        return f"<DeltaTimer fps={1/self.frame_target:.1f} paused={self._paused}>"

    def pause(self):
        """Pause the timer—dt will be zero until resumed."""
        self._paused = True

    def resume(self):
        """Resume without any giant dt spike."""
        self._paused    = False
        self._last_time = time()

    def update(self):
        """
        Call at the top of each frame.
        Returns: dt (raw seconds since last update), or 0.0 if paused.
        """
        if self._paused:
            # no progress while paused
            self._frame_start = None
            return 0.0

        now                 = time()
        dt                  = now - self._last_time
        self._last_time     = now
        self._frame_start   = now
        return dt

    def enforceFps(self):
        """
        Call at the end of each frame to throttle to your target FPS.
        If paused, still yields one frame's worth of time.
        """
        if self._paused:
            sleep(self.frame_target)
            return

        if self._frame_start is None:
            return  # update() wasn't called

        work_time = time() - self._frame_start
        to_sleep  = self.frame_target - work_time
        if to_sleep > 0:
            sleep(to_sleep)
        self._frame_start = None
