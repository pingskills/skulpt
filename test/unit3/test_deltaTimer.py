import unittest
import deltaTimer

class FakeTimeSleep:
    def __init__(self, times):
        # times: list of timestamps to return on successive calls
        self.times = list(times)
        self.slept = []

    def time(self):
        # return next timestamp, or last if exhausted
        if self.times:
            self.last = self.times.pop(0)
        return self.last

    def sleep(self, duration):
        # record sleep durations
        self.slept.append(duration)

class TestDeltaTimer(unittest.TestCase):
    def test_update_and_enforceFps(self):
        # __init__ at 100.0, update() at 100.2, enforceFps timing at 100.25
        fake = FakeTimeSleep(times=[100.0, 100.2, 100.25])
        # monkey-patch module functions
        deltaTimer.time = fake.time
        deltaTimer.sleep = fake.sleep

        timer = deltaTimer.DeltaTimer(fps=60)
        # repr shows fps and paused flag
        self.assertEqual(repr(timer), '<DeltaTimer fps=60.0 paused=False>')

        # update returns correct dt and sets frame_start
        dt = timer.update()
        self.assertAlmostEqual(dt, 0.2)
        self.assertEqual(timer._frame_start, 100.2)

        # enforceFps: work_time = 100.25 - 100.2 = 0.05 > 1/60 => no sleep
        timer.enforceFps()
        self.assertEqual(fake.slept, [])
        self.assertIsNone(timer._frame_start)

    def test_enforceFps_without_update(self):
        fake = FakeTimeSleep(times=[0.0])
        deltaTimer.time = fake.time
        deltaTimer.sleep = fake.sleep

        timer = deltaTimer.DeltaTimer(fps=10)
        # enforceFps without update should do nothing
        timer.enforceFps()
        self.assertEqual(fake.slept, [])

    def test_enforceFps_when_paused(self):
        fake = FakeTimeSleep(times=[0.0])
        deltaTimer.time = fake.time
        deltaTimer.sleep = fake.sleep

        timer = deltaTimer.DeltaTimer(fps=5)
        timer.pause()
        # enforceFps when paused should sleep one frame duration
        timer.enforceFps()
        self.assertEqual(fake.slept, [timer.frame_target])

    def test_update_when_paused(self):
        fake = FakeTimeSleep(times=[0.0])
        deltaTimer.time = fake.time
        deltaTimer.sleep = fake.sleep

        timer = deltaTimer.DeltaTimer(fps=60)
        timer.pause()
        # update when paused returns 0.0 and clears frame_start
        dt = timer.update()
        self.assertEqual(dt, 0.0)
        self.assertIsNone(timer._frame_start)

    def test_resume_and_update(self):
        # init at 100.0, resume resets at 150.0, update at 150.1
        fake = FakeTimeSleep(times=[100.0, 150.0, 150.1])
        deltaTimer.time = fake.time
        deltaTimer.sleep = fake.sleep

        timer = deltaTimer.DeltaTimer(fps=60)
        timer.pause()
        timer.resume()
        dt = timer.update()
        self.assertAlmostEqual(dt, 0.1)
        self.assertEqual(timer._frame_start, 150.1)

    def test_repr_after_pause(self):
        fake = FakeTimeSleep(times=[0.0])
        deltaTimer.time = fake.time
        deltaTimer.sleep = fake.sleep

        timer = deltaTimer.DeltaTimer(fps=30)
        timer.pause()
        # repr reflects paused state
        self.assertEqual(repr(timer), '<DeltaTimer fps=30.0 paused=True>')

    def test_raw_fps(self):
        # With averaged=False, getFps() == 1 / last_dt
        timer = deltaTimer.DeltaTimer(fps=10, smoothing=5)
        timer._last_dt = 0.2   # simulate a 0.2s frame
        self.assertAlmostEqual(timer.getFps(averaged=False), 5.0)

    def test_average_fps_with_history(self):
        # With averaged=True, FPS == 1 / mean(dt_history)
        timer = deltaTimer.DeltaTimer(fps=60, smoothing=3)
        # push three frame‐times: 0.5s, 0.25s, 0.75s -> mean dt = 0.5
        timer._dt_history.extend([0.5, 0.25, 0.75])
        self.assertAlmostEqual(timer.getFps(averaged=True), 2.0)

    def test_average_fps_without_history(self):
        # If history is empty, averaged=True falls back to last_dt
        timer = deltaTimer.DeltaTimer(fps=30, smoothing=3)
        # initial last_dt == 1/30
        expected_fps = 30.0
        self.assertAlmostEqual(timer.getFps(averaged=True), expected_fps, places=2)

    def test_zero_dt(self):
        # dt == 0 should never divide-by-zero; getFps returns 0.0
        timer = deltaTimer.DeltaTimer(fps=60, smoothing=3)
        timer._last_dt = 0.0
        timer._dt_history.extend([0.0, 0.0, 0.0])
        self.assertEqual(timer.getFps(averaged=False), 0.0)
        self.assertEqual(timer.getFps(averaged=True), 0.0)

    def test_tick_combines_update_and_enforce_fps(self):
        # __init__ at 100.0s, update() at 100.2s, enforceFps() at 100.22s
        fake = FakeTimeSleep(times=[100.0, 100.2, 100.22])
        deltaTimer.time  = fake.time
        deltaTimer.sleep = fake.sleep

        timer = deltaTimer.DeltaTimer(fps=60)
        dt = timer.tick()

        # dt should be the delta between init and update
        self.assertAlmostEqual(dt, 0.2, places=3)

        # work_time = 0.02s, frame_target = 1/60≈0.0167, so no sleep
        self.assertEqual(fake.slept, [])

        # after a full tick, frame_start should be reset
        self.assertIsNone(timer._frame_start)

if __name__ == '__main__':
    unittest.main()
