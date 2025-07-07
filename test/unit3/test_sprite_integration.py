import unittest

from sprite import RectangleSprite, CircleSprite, EllipseSprite

class IntegrationSmokeTests(unittest.TestCase):
    def test_rectangle_tween_collision(self):
        # Moving rectangle should collide with static rectangle at the right time
        mover = RectangleSprite(0, 0, width=1, height=1)
        static = RectangleSprite(5, 0, width=1, height=1)
        # Tween x from 0 to 5 over 5s (linear)
        mover.tweenTo('x', 5, duration=5.0, easing='linear')
        # step in 1s increments until collision detected
        collision_time = None
        total_time = 0.0
        dt = 1.0
        while collision_time is None and total_time <= 5.0:
            mover.update(dt)
            total_time += dt
            if mover.overlaps(static):
                collision_time = total_time
        # collision expected at t=4.0 (when mover.right == static.left)
        self.assertAlmostEqual(collision_time, 4.0)
        # after collision but before full duration, tween should still be active
        self.assertTrue(mover._tweens, "Tween should still be active after initial collision")
        # complete the tween
        while mover._tweens:
            mover.update(dt)
        # tween should be removed after completion
        self.assertEqual(len(mover._tweens), 0, "Tween should be removed after completion")

    def test_circle_to_ellipse_collision(self):
        # Circle moves into ellipse region by end of tween
        circle = CircleSprite(0, 0, radius=1)
        ellipse = EllipseSprite(5, 0, radiusX=1, radiusY=2)
        circle.tweenTo('x', 5, duration=5.0)
        for _ in range(5):
            circle.update(1.0)
        # At t=5, x==5, should overlap
        self.assertTrue(circle.overlaps(ellipse))

    def test_tween_on_complete_callback(self):
        # Ensure onComplete callback fires and tween is cleared
        rect = RectangleSprite(0, 0, width=1, height=1)
        calls = []
        def cb():
            calls.append('done')
        t = rect.tweenTo('x', 2, duration=1.0)
        t.onComplete(cb)
        rect.update(1.0)
        self.assertEqual(calls, ['done'], "Expected onComplete callback to be invoked once")
        # Further updates should not add more calls
        rect.update(1.0)
        self.assertEqual(calls, ['done'])
        # Tween list should be empty
        self.assertEqual(len(rect._tweens), 0)

if __name__ == '__main__':
    unittest.main()
