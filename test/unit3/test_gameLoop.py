import unittest
import gameLoop

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
    def test_init_invalid_args(self):
        with self.assertRaises(ValueError):
            gameLoop.DeltaTimer(fps=0, smoothing=5)
        with self.assertRaises(ValueError):
            gameLoop.DeltaTimer(fps=30, smoothing=0)
        with self.assertRaises(ValueError):
            gameLoop.DeltaTimer(fps=-10, smoothing=-1)
        with self.assertRaises(ValueError):
            gameLoop.DeltaTimer(fps=10, smoothing=5, max_dt_multiplier=0.5)

    def test_update_and_enforceFps(self):
        fake = FakeTimeSleep(times=[100.0, 100.2, 100.25])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.DeltaTimer(fps=60)
        dt = timer.update()
        # dt is clamped to max_dt
        self.assertAlmostEqual(dt, timer.max_dt)
        self.assertEqual(timer._frame_start, 100.2)

        timer.enforceFps()
        self.assertEqual(fake.slept, [])
        self.assertIsNone(timer._frame_start)

    def test_enforceFps_without_update(self):
        fake = FakeTimeSleep(times=[0.0])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.DeltaTimer(fps=10)
        timer.enforceFps()
        self.assertEqual(fake.slept, [])

    def test_enforceFps_when_paused(self):
        fake = FakeTimeSleep(times=[0.0])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.DeltaTimer(fps=5)
        timer.pause()
        timer.enforceFps()
        self.assertEqual(fake.slept, [timer.frame_target])

    def test_update_when_paused(self):
        fake = FakeTimeSleep(times=[0.0])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.DeltaTimer(fps=60)
        timer.pause()
        dt = timer.update()
        self.assertEqual(dt, 0.0)
        self.assertIsNone(timer._frame_start)

    def test_resume_and_update(self):
        fake = FakeTimeSleep(times=[100.0, 150.0, 150.1])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.DeltaTimer(fps=60)
        timer.pause()
        timer.resume()
        dt = timer.update()
        # raw dt 0.1 > max_dt, so clamped
        self.assertAlmostEqual(dt, timer.max_dt)
        self.assertEqual(timer._frame_start, 150.1)

    def test_repr(self):
        timer = gameLoop.DeltaTimer(fps=30)
        self.assertIn('fps=30.0', repr(timer))
        self.assertIn('paused=False', repr(timer))
        timer.pause()
        self.assertIn('paused=True', repr(timer))

    def test_raw_fps(self):
        timer = gameLoop.DeltaTimer(fps=10, smoothing=5)
        timer._last_dt = 0.2
        self.assertAlmostEqual(timer.getFps(averaged=False), 5.0)

    def test_average_fps_with_history(self):
        timer = gameLoop.DeltaTimer(fps=60, smoothing=3)
        timer._dt_history.extend([0.5, 0.25, 0.75])
        self.assertAlmostEqual(timer.getFps(averaged=True), 2.0)

    def test_average_fps_without_history(self):
        timer = gameLoop.DeltaTimer(fps=30, smoothing=3)
        expected = 30.0
        self.assertAlmostEqual(timer.getFps(averaged=True), expected, places=2)

    def test_zero_dt(self):
        timer = gameLoop.DeltaTimer(fps=60, smoothing=3)
        timer._last_dt = 0.0
        timer._dt_history.extend([0.0, 0.0])
        self.assertEqual(timer.getFps(averaged=False), 0.0)
        self.assertEqual(timer.getFps(averaged=True), 0.0)

    def test_tick_combines_update_and_enforce_fps(self):
        fake = FakeTimeSleep(times=[100.0, 100.2, 100.22])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.DeltaTimer(fps=60)
        dt = timer.tick()
        # dt is clamped
        self.assertAlmostEqual(dt, timer.max_dt, places=3)
        self.assertEqual(fake.slept, [])
        self.assertEqual(timer._frame_start, 100.2)

    def test_dt_history_property(self):
        timer = gameLoop.DeltaTimer(fps=10, smoothing=3)
        self.assertEqual(timer.dt_history, [])
        timer._dt_history.extend([0.1, 0.2])
        hist = timer.dt_history
        self.assertEqual(hist, [0.1, 0.2])
        hist.append(0.3)
        self.assertEqual(timer.dt_history, [0.1, 0.2])

    def test_last_dt_and_fps_properties(self):
        timer = gameLoop.DeltaTimer(fps=20, smoothing=5)
        timer._last_dt = 0.05
        self.assertAlmostEqual(timer.last_dt, 0.05)
        self.assertAlmostEqual(timer.fps, 20.0)
        timer._dt_history.extend([0.1, 0.2, 0.1])
        avg = 1.0 / ((0.1 + 0.2 + 0.1) / 3)
        self.assertAlmostEqual(timer.fps, avg, places=5)

    def test_reset_clears_history_and_last_dt_and_frame_start(self):
        fake = FakeTimeSleep(times=[0.0, 0.1])
        gameLoop.time = fake.time
        timer = gameLoop.DeltaTimer(fps=10, smoothing=5)
        timer.update()
        self.assertTrue(timer.dt_history)
        self.assertIsNotNone(timer._frame_start)
        timer.reset()
        self.assertEqual(timer.dt_history, [])
        self.assertEqual(timer.last_dt, timer.frame_target)
        self.assertIsNone(timer._frame_start)

    def test_setFps_updates_frame_target_and_max_dt(self):
        timer = gameLoop.DeltaTimer(fps=20, smoothing=3, max_dt_multiplier=3)
        self.assertAlmostEqual(timer.frame_target, 1.0 / 20)
        self.assertAlmostEqual(timer.max_dt, (1.0 / 20) * 3)
        timer.setFps(40)
        self.assertAlmostEqual(timer.frame_target, 1.0 / 40)
        self.assertAlmostEqual(timer.max_dt, (1.0 / 40) * 3)
        timer.setFps(10, max_dt_multiplier=2)
        self.assertAlmostEqual(timer.frame_target, 1.0 / 10)
        self.assertAlmostEqual(timer.max_dt, (1.0 / 10) * 2)

    def test_setFps_invalid_raises(self):
        timer = gameLoop.DeltaTimer()
        with self.assertRaises(ValueError):
            timer.setFps(0)
        with self.assertRaises(ValueError):
            timer.setFps(-5)

    def test_dt_clamping(self):
        fake = FakeTimeSleep(times=[0.0, 1.0])
        gameLoop.time = fake.time
        timer = gameLoop.DeltaTimer(fps=60, smoothing=5, max_dt_multiplier=4)
        dt = timer.update()
        self.assertAlmostEqual(dt, timer.max_dt)

class TestSimpleTimer(unittest.TestCase):
    def test_init_invalid_fps(self):
        with self.assertRaises(ValueError):
            gameLoop.SimpleTimer(fps=0)
        with self.assertRaises(ValueError):
            gameLoop.SimpleTimer(fps=-10)

    def test_update_sets_last_time(self):
        fake = FakeTimeSleep(times=[100.0])
        gameLoop.time = fake.time

        timer = gameLoop.SimpleTimer(fps=60)
        timer.update()
        self.assertEqual(timer._last_time, 100.0)

    def test_enforceFps_sleeps_correct_time(self):
        # Use predictable math: start at 100.0, next time is 100.01
        fake = FakeTimeSleep(times=[100.0, 100.0, 100.01])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.SimpleTimer(fps=60)  # frame target ≈ 0.0166667
        timer.update()
        timer.enforceFps()
        self.assertEqual(len(fake.slept), 1)
        self.assertAlmostEqual(fake.slept[0], 0.0066667, places=4)

    def test_enforceFps_skips_sleep_if_too_late(self):
        # Force it to run late: 100.0 → 100.05 = 50ms elapsed (too slow)
        fake = FakeTimeSleep(times=[100.0, 100.0, 100.05])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.SimpleTimer(fps=60)  # frame target ≈ 0.0167
        timer.update()
        timer.enforceFps()
        self.assertEqual(fake.slept, [])  # Should skip sleeping

    def test_tick_calls_update_and_enforceFps(self):
        fake = FakeTimeSleep(times=[100.0, 100.0, 100.01])
        gameLoop.time = fake.time
        gameLoop.sleep = fake.sleep

        timer = gameLoop.SimpleTimer(fps=30)  # target = 1/30 = ~0.0333
        timer.tick()
        self.assertEqual(len(fake.slept), 1)
        self.assertAlmostEqual(fake.slept[0], 0.0233, places=4)

    def test_reset_sets_last_time(self):
        fake = FakeTimeSleep(times=[100.0, 200.0])
        gameLoop.time = fake.time

        timer = gameLoop.SimpleTimer(fps=60)
        self.assertEqual(timer._last_time, 100.0)

        timer.reset()
        self.assertEqual(timer._last_time, 200.0)

if __name__ == "__main__":
    unittest.main()
