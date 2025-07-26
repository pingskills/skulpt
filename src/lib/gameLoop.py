from collections import deque
from time import time

class DeltaTimer:
    def __init__(self, fps=60, smoothing=30, max_dt_multiplier=4):
        """
        fps: target frames per second for throttling
        smoothing: number of frames to keep for fps calculation
        max_dt_multiplier: limits maximum value of dt
        """
        if fps <= 0:
            raise ValueError("fps must be > 0")
        if smoothing <= 0:
            raise ValueError("smoothing must be > 0")
        if max_dt_multiplier < 1:
            raise ValueError("max_dt_multiplier must be at least 1")

        self.frame_target = 1.0 / fps
        self.max_dt_multiplier = max_dt_multiplier
        self.max_dt = self.frame_target * self.max_dt_multiplier
        self._last_time   = time()
        self._frame_start = None
        self._paused      = False
        self._dt_history = deque(maxlen=smoothing)
        self._last_dt    = self.frame_target

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
            self._last_dt = 0
            return 0.0

        now = time()
        dt  = min(now - self._last_time, self.max_dt)
        self._last_time = now
        self._frame_start = now
        self._dt_history.append(dt)
        self._last_dt = dt
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

    def setFps(self, fps, max_dt_multiplier=None):
        if fps <= 0:
            raise ValueError("fps must be > 0")
        # update multiplier if provided
        if max_dt_multiplier is not None:
            self.max_dt_multiplier = max_dt_multiplier

        # recompute targets
        self.frame_target = 1.0 / fps
        self.max_dt       = self.frame_target * self.max_dt_multiplier

    def getFps(self, averaged=True):
        """
        If averaged=True, returns 1 / (mean dt over history).
        Otherwise, returns instantaneous 1 / last_dt.
        """
        if averaged and self._dt_history:
            mean_dt = sum(self._dt_history) / len(self._dt_history)
        else:
            mean_dt = self._last_dt

        return 1.0 / mean_dt if mean_dt > 0 else 0.0

    def tick(self):
        """
        Combines enforceFps() and update(),
        returning the raw dt in seconds.
        """
        self.enforceFps()
        dt = self.update()
        return dt

    def reset(self):
        self._dt_history.clear()
        self._last_dt    = self.frame_target
        self._last_time  = time()
        self._frame_start = None

    @property
    def dt_history(self):
        return list(self._dt_history)

    @property
    def fps(self):
        return self.getFps()

    @property
    def last_dt(self):
        return self._last_dt

class SimpleTimer:
    def __init__(self, fps=60):
        """
        Simple frame capping timer.
        Sleeps only the required amount to maintain the target frame rate.
        Does not compute dt — suitable for fixed-step logic only.
        """
        if fps <= 0:
            raise ValueError("fps must be > 0")

        self.frame_target = 1.0 / fps
        self._last_time   = time()

    def update(self):
        """
        Call at the top of each frame to mark the start time.
        """
        self._last_time = time()

    def enforceFps(self):
        """
        Call at the end of the frame to sleep any remaining time.
        If the frame took longer than the target, does not sleep.
        """
        sleep_time = self._last_time + self.frame_target - time()
        if sleep_time > 0:
            sleep(sleep_time)

    def tick(self):
        """
        Run a full frame cycle: marks the start and enforces the frame cap.

        This combines update() and enforceFps(), assuming fixed timestep logic.
        It does not return dt — use this only when your game logic runs at a constant rate.
        """
        self.update()
        self.enforceFps()

    def reset(self):
        self._last_time  = time()
