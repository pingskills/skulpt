import math
import unittest
import sprite
from sprite import (
    clamp,
    Transformable,
    RectangleSprite,
    CircleSprite,
    EllipseSprite,
    PolygonSprite,
    Sprite,
    TextSprite,
    aabbCollision,
    circleCircleCollision,
    circleRectCollision,
    ellipseEllipseCollision,
    ellipseRectCollision,
    circleEllipseCollision,
    polygonPolygonCollision,
    polygonRectCollision,
    polygonCircleCollision,
    polygonEllipseCollision,
    COLLISION_HANDLERS
)

__author__ = "pyangelo"

class ClampTests(unittest.TestCase):
    def test_clamp_within_bounds(self):
        self.assertEqual(clamp(5, 0, 10), 5)
    def test_clamp_below_min(self):
        self.assertEqual(clamp(-1, 0, 10), 0)
    def test_clamp_above_max(self):
        self.assertEqual(clamp(11, 0, 10), 10)

class TransformableTests(unittest.TestCase):
    class DummyPoint:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    def setUp(self):
        self.t = Transformable(2, 3, angle=10, anchorX=0.2, anchorY=0.8)

    def test_position_and_rotation(self):
        self.t.moveBy(1, -1)
        self.assertEqual((self.t.x, self.t.y), (3, 2))
        self.t.moveTo(0, 0)
        self.assertEqual((self.t.x, self.t.y), (0, 0))
        self.t.rotateBy(15)
        self.assertEqual(self.t.angle, 25)
        self.t.rotateTo(5)
        self.assertEqual(self.t.angle, 5)

    def test_anchor_clamping(self):
        self.t.setAnchor(-1, 2)
        # anchorX clamps to 0, anchorY clamps to 1
        self.assertEqual((self.t.anchorX, self.t.anchorY), (0, 1))

    def test_contains_default_hit(self):
        rect = RectangleSprite(0, 0, 10, 5)
        inside = self.DummyPoint(5, 2)
        outside = self.DummyPoint(11, 2)
        self.assertTrue(rect.contains(inside))
        self.assertFalse(rect.contains(outside))

    def test_contains_custom_hit(self):
        rect = RectangleSprite(0, 0, 10, 5)
        # custom hit always False
        rect.setHitTest(lambda self_, pt: False)
        pt = self.DummyPoint(1,1)
        self.assertFalse(rect.contains(pt))

    def test_overlaps_default_and_custom(self):
        r1 = RectangleSprite(0,0,4,4)
        r2 = RectangleSprite(2,2,4,4)
        self.assertTrue(r1.overlaps(r2))
        # custom overlap always False
        r1.setOverlapTest(lambda self_, other: False)
        self.assertFalse(r1.overlaps(r2))

    def test_tweenTo_and_update(self):
        self.t.x = 0
        tw = self.t.tweenTo('x', 10, duration=2.0, easing='linear')
        # simulate halfway
        self.t.update(1.0)
        self.assertAlmostEqual(self.t.x, 5)
        # complete
        self.t.update(1.0)
        self.assertAlmostEqual(self.t.x, 10)
        # tween removed
        self.assertEqual(len(self.t._tweens), 0)

class RectangleSpriteTests(unittest.TestCase):
    def test_bounds_and_repr(self):
        r = RectangleSprite(1, 2, width=3, height=4)
        self.assertEqual((r.left, r.right, r.bottom, r.top), (1, 4, 2, 6))
        self.assertEqual(repr(r), "RectangleSprite(x=1,y=2,w=3,h=4)")

class CircleSpriteTests(unittest.TestCase):
    def test_bounds_and_repr_and_collision(self):
        c = CircleSprite(5, 5, radius=2)
        self.assertEqual((c.left, c.right, c.bottom, c.top), (3, 7, 3, 7))
        self.assertEqual(repr(c), "CircleSprite(x=5,y=5,r=2)")
        # circle-circle collision
        c2 = CircleSprite(7,5, radius=2)
        self.assertTrue(circleCircleCollision(c, c2))
        # overlaps via method
        self.assertTrue(c.overlaps(c2))

class EllipseSpriteTests(unittest.TestCase):
    def test_bounds_and_collision(self):
        e1 = EllipseSprite(0,0, radiusX=3, radiusY=1)
        e2 = EllipseSprite(4,0, radiusX=3, radiusY=1)
        self.assertEqual((e1.left, e1.right, e1.bottom, e1.top), (-3,3,-1,1))
        self.assertTrue(ellipseEllipseCollision(e1, e2))
        # rectangle collision
        r = RectangleSprite(0,0, width=2, height=2)
        self.assertTrue(ellipseRectCollision(e1, r))

class PolygonSpriteTests(unittest.TestCase):
    def test_vertices_axes_and_projection(self):
        # equilateral triangle centered at (0,0)
        tri = PolygonSprite(0,0, numSides=3, radius=1)
        verts = tri.getVertices()
        self.assertEqual(len(verts), 3)
        axes = tri.getAxes()
        self.assertEqual(len(axes), 3)
        # project on x-axis
        minp, maxp = tri.project((1,0))
        # vertices x-coordinates are within [-1,1]
        self.assertTrue(-1 <= minp <= maxp <= 1)

class SpriteTests(unittest.TestCase):
    class DummyImg:
        def __init__(self, width, height, file=None):
            self.width = width
            self.height = height
            self.file = file
    def setUp(self):
        # monkey-patch Image and drawImage
        sprite.Image = lambda f: self.DummyImg(5,7, file=f)
        sprite.drawImage = lambda img, x,y,w,h,opacity=None: None
    def test_imagefile_and_dimensions(self):
        img = self.DummyImg(5,7)
        s = Sprite(img, x=1, y=2)
        self.assertEqual(s.image, img)
        self.assertEqual((s.width, s.height), (5,7))
        # test setter from file
        s2 = Sprite("path/to.png")
        self.assertEqual(s2.imageFile, "path/to.png")
        self.assertIsInstance(s2.image, self.DummyImg)
        # hitboxScale and bounds
        s2.width, s2.height = 10, 20
        s2.setHitboxScale(0.5)
        self.assertAlmostEqual(s2.left, s2.x + 2.5)
        self.assertAlmostEqual(s2.right, s2.x + 7.5)
        self.assertAlmostEqual(s2.bottom, s2.y + 5)
        self.assertAlmostEqual(s2.top, s2.y + 15)
        # opacity clamping
        s2.opacity = 2.0
        self.assertEqual(s2.opacity, 1.0)
        s2.opacity = -1.0
        self.assertEqual(s2.opacity, 0.0)

class TextSpriteTests(unittest.TestCase):
    def setUp(self):
        # monkey-patch measureText, fill, text
        sprite.measureText = lambda txt, size, name: {
            'actualBoundingBoxLeft': 1,
            'actualBoundingBoxRight': 3,
            'actualBoundingBoxAscent': 2,
            'actualBoundingBoxDescent': 4
        }
        sprite.fill = lambda colour: None
        sprite.text = lambda txt, x,y, size, name: None
    def test_metrics_and_setters(self):
        t = TextSprite("hello", x=0, y=0, fontSize=10, fontName="TestFont")
        # width = 1+3=4, height=2+4=6
        self.assertEqual((t.width, t.height), (4,6))
        # changing textContent recalculates
        t.textContent = "world"
        self.assertEqual((t.width, t.height), (4,6))
        # fontSize setter
        t.fontSize = 12
        self.assertEqual((t.width, t.height), (4,6))
        # fontName setter
        t.fontName = "Other"
        self.assertEqual((t.width, t.height), (4,6))

class RectangleDrawModeTests(unittest.TestCase):
    def test_rectangle_bounds_corner(self):
        r = RectangleSprite(10, 20, width=4, height=6)
        r.setDrawMode(CORNER)
        # x→left, y→bottom
        self.assertEqual((r.left, r.right, r.bottom, r.top), (10,14,20,26))

    def test_rectangle_bounds_center(self):
        r = RectangleSprite(10, 20, width=4, height=6)
        r.setDrawMode(CENTER)
        # centre (10,20) with half-sizes 2,3
        self.assertEqual((r.left, r.right, r.bottom, r.top), (8,12,17,23))

    def test_center_coordinates(self):
        r = RectangleSprite(3, 7, width=4, height=6)
        r.setDrawMode(CORNER)
        self.assertEqual((r.centerX, r.centerY), (3+2, 7+3))

        r.setDrawMode(CENTER)
        self.assertEqual((r.centerX, r.centerY), (3, 7))

class CircleDrawModeTests(unittest.TestCase):
    def test_circle_bounds_center(self):
        c = CircleSprite(5, 5, radius=3)
        # default is CENTER → left=2,right=8,bottom=2,top=8
        self.assertEqual((c.left, c.right, c.bottom, c.top), (2,8,2,8))

    def test_circle_bounds_corner(self):
        c = CircleSprite(5, 5, radius=3)
        c.setDrawMode(CORNER)
        # now x,y is lower-left of 6×6 box
        self.assertEqual((c.left, c.right, c.bottom, c.top), (5,11,5,11))

    def test_center_coordinates(self):
        r = CircleSprite(10, 20, radius=4)
        r.setDrawMode(CORNER)
        self.assertEqual((r.centerX, r.centerY), (10+4, 20+4))

        r.setDrawMode(CENTER)
        self.assertEqual((r.centerX, r.centerY), (10, 20))


class EllipseDrawModeTests(unittest.TestCase):
    def test_ellipse_bounds_center(self):
        e = EllipseSprite(0, 0, radiusX=2, radiusY=1)
        # default CENTER
        self.assertEqual((e.left,e.right,e.bottom,e.top),(-2,2,-1,1))

    def test_ellipse_bounds_corner(self):
        e = EllipseSprite(0, 0, radiusX=2, radiusY=1)
        e.setDrawMode(CORNER)
        # box from (0,0) → (4,2)
        self.assertEqual((e.left,e.right,e.bottom,e.top),(0,4,0,2))

    def test_center_coordinates(self):
        r = EllipseSprite(10, 20, radiusX=4, radiusY=6)
        r.setDrawMode(CORNER)
        self.assertEqual((r.centerX, r.centerY), (10+4, 20+6))

        r.setDrawMode(CENTER)
        self.assertEqual((r.centerX, r.centerY), (10, 20))


class PolygonDrawModeTests(unittest.TestCase):
    def test_polygon_bounds_center(self):
        p = PolygonSprite(10, 10, numSides=5, radius=4)
        # default CENTER
        self.assertEqual((p.left,p.right,p.bottom,p.top), (6,14,6,14))

    def test_polygon_bounds_corner(self):
        p = PolygonSprite(10, 10, numSides=5, radius=4)
        p.setDrawMode(CORNER)
        # box from (10,10) → (18,18)
        self.assertEqual((p.left,p.right,p.bottom,p.top), (10,18,10,18))

    def test_center_coordinates(self):
        r = PolygonSprite(10, 20, 5, radius=7)
        r.setDrawMode(CORNER)
        self.assertEqual((r.centerX, r.centerY), (10+7, 20+7))

        r.setDrawMode(CENTER)
        self.assertEqual((r.centerX, r.centerY), (10, 20))

if __name__ == '__main__':
    unittest.main()
