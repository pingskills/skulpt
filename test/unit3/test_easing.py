import math
import unittest

from easing import (
    linear_easing,
    ease_in_quad, ease_out_quad, ease_in_out_quad,
    ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
    ease_in_sine, ease_out_sine, ease_in_out_sine,
    ease_out_bounce, ease_out_elastic,
    EASINGS, register_easing, Tween
)

__author__ = "pyangelo"

# Unit tests for easing.py
# Ensure file is named test_easing.py to be auto-discovered

class EasingFunctionTests(unittest.TestCase):
    def test_linear_easing(self):
        self.assertEqual(linear_easing(0.0), 0.0)
        self.assertEqual(linear_easing(0.5), 0.5)
        self.assertEqual(linear_easing(1.0), 1.0)

    def test_quad_easings(self):
        # ease_in_quad
        self.assertEqual(ease_in_quad(0.0), 0.0)
        self.assertAlmostEqual(ease_in_quad(1.0), 1.0)
        self.assertAlmostEqual(ease_in_quad(0.3), 0.3*0.3)
        # ease_out_quad
        self.assertEqual(ease_out_quad(0.0), 0.0)
        self.assertAlmostEqual(ease_out_quad(1.0), 1.0)
        self.assertAlmostEqual(ease_out_quad(0.4), 0.4*(2-0.4))
        # ease_in_out_quad
        self.assertEqual(ease_in_out_quad(0.0), 0.0)
        self.assertAlmostEqual(ease_in_out_quad(1.0), 1.0)
        # midpoint behavior
        mid = 0.25
        if mid < 0.5:
            expected = 2*mid*mid
        else:
            expected = -1 + (4-2*mid)*mid
        self.assertAlmostEqual(ease_in_out_quad(mid), expected)

    def test_cubic_easings(self):
        # ease_in_cubic
        self.assertEqual(ease_in_cubic(0.0), 0.0)
        self.assertAlmostEqual(ease_in_cubic(1.0), 1.0)
        self.assertAlmostEqual(ease_in_cubic(0.2), 0.2**3)
        # ease_out_cubic
        self.assertEqual(ease_out_cubic(0.0), 0.0)
        self.assertAlmostEqual(ease_out_cubic(1.0), 1.0)
        self.assertAlmostEqual(ease_out_cubic(0.5), (0.5-1)**3 + 1)
        # ease_in_out_cubic
        self.assertEqual(ease_in_out_cubic(0.0), 0.0)
        self.assertAlmostEqual(ease_in_out_cubic(1.0), 1.0)

    def test_sine_easings(self):
        # ease_in_sine
        self.assertEqual(ease_in_sine(0.0), 0.0)
        self.assertAlmostEqual(ease_in_sine(1.0), 1.0)
        self.assertAlmostEqual(ease_in_sine(0.5), 1 - math.cos((0.5*math.pi)/2))
        # ease_out_sine
        self.assertEqual(ease_out_sine(0.0), 0.0)
        self.assertAlmostEqual(ease_out_sine(1.0), 1.0)
        self.assertAlmostEqual(ease_out_sine(0.5), math.sin((0.5*math.pi)/2))
        # ease_in_out_sine
        self.assertEqual(ease_in_out_sine(0.0), 0.0)
        self.assertAlmostEqual(ease_in_out_sine(1.0), 1.0)

    def test_bounce_and_elastic_edges(self):
        # bounce
        self.assertEqual(ease_out_bounce(0.0), 0.0)
        self.assertAlmostEqual(ease_out_bounce(1.0), 1.0)
        # elastic
        self.assertEqual(ease_out_elastic(0.0), 0.0)
        self.assertAlmostEqual(ease_out_elastic(1.0), 1.0)

    def test_easings_registry(self):
        # ensure named functions in EASINGS map
        for name, func in [
            ('linear', linear_easing),
            ('ease_in_quad', ease_in_quad),
            ('ease_out_quad', ease_out_quad),
            ('ease_in_out_quad', ease_in_out_quad),
            ('ease_in_cubic', ease_in_cubic),
            ('ease_out_cubic', ease_out_cubic),
            ('ease_in_out_cubic', ease_in_out_cubic),
            ('ease_in_sine', ease_in_sine),
            ('ease_out_sine', ease_out_sine),
            ('ease_in_out_sine', ease_in_out_sine),
            ('ease_out_bounce', ease_out_bounce),
            ('ease_out_elastic', ease_out_elastic),
        ]:
            self.assertIn(name, EASINGS)
            self.assertIs(EASINGS[name], func)

    def test_register_easing(self):
        def custom_ease(t):
            return t * 0.5
        register_easing('custom', custom_ease)
        self.assertIn('custom', EASINGS)
        self.assertIs(EASINGS['custom'], custom_ease)
        # cleanup
        EASINGS.pop('custom', None)


class TweenTests(unittest.TestCase):
    class Dummy:
        def __init__(self):
            self.value = 0

    def test_tween_progress_and_completion(self):
        obj = self.Dummy()
        tween = Tween(obj, 'value', endValue=10, duration=2.0, easing='linear')
        tween.update(1.0)
        self.assertAlmostEqual(obj.value, 5.0)
        self.assertFalse(tween.finished)
        tween.update(1.0)
        self.assertAlmostEqual(obj.value, 10.0)
        self.assertTrue(tween.finished)

    def test_oncomplete_called_once(self):
        obj = self.Dummy()
        tween = Tween(obj, 'value', endValue=4, duration=1.0)
        calls = []
        tween.onComplete(lambda: calls.append('x'))
        tween.update(1.0)
        self.assertEqual(calls, ['x'])
        tween.update(0.5)
        self.assertEqual(calls, ['x'])

    def test_cancel(self):
        obj = self.Dummy()
        tween = Tween(obj, 'value', endValue=8, duration=1.0)
        tween.update(0.5)
        mid = obj.value
        tween.cancel()
        tween.update(1.0)
        self.assertAlmostEqual(obj.value, mid)
        self.assertTrue(tween.finished)

    def test_custom_easing_function(self):
        def half(t): return 0.5
        obj = self.Dummy()
        tween = Tween(obj, 'value', endValue=6, duration=3.0, easing=half)
        tween.update(1.0)
        # always half progression
        self.assertAlmostEqual(obj.value, 3.0)


if __name__ == '__main__':
    unittest.main()
