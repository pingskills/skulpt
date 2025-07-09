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

if __name__ == '__main__':
    unittest.main()
