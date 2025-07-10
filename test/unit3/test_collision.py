import unittest
from sprite import (
    RectangleSprite,
    CircleSprite,
    EllipseSprite,
    PolygonSprite
)
from collision import (
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

class CollisionGeometryTests(unittest.TestCase):
    def setUp(self):
        # Rectangles: rect1 vs rect2 (no overlap), rect1 vs rect3 (overlap)
        self.rect1 = RectangleSprite(0, 0, width=2, height=2)
        self.rect2 = RectangleSprite(3, 3, width=2, height=2)
        self.rect3 = RectangleSprite(1.5, 1.5, width=2, height=2)

        # Circles: circle1 vs circle2 (no), circle1 vs circle3 (yes)
        self.circle1 = CircleSprite(0, 0, radius=1)
        self.circle2 = CircleSprite(3, 0, radius=1)
        self.circle3 = CircleSprite(1.5, 0, radius=1)

        # Ellipses: ellipse1 vs ellipse2 (no), ellipse1 vs ellipse3 (yes)
        self.ellipse1 = EllipseSprite(0, 0, radiusX=2, radiusY=1)
        self.ellipse2 = EllipseSprite(5, 0, radiusX=2, radiusY=1)
        self.ellipse3 = EllipseSprite(1, 0, radiusX=2, radiusY=1)

        # Polygons: poly1 vs poly2 (no), poly1 vs poly3 (yes)
        self.poly1 = PolygonSprite(0, 0, numSides=4, radius=1)
        self.poly2 = PolygonSprite(5, 5, numSides=4, radius=1)
        self.poly3 = PolygonSprite(0.5, 0.5, numSides=4, radius=1)

    def test_aabbCollision(self):
        self.assertFalse(aabbCollision(self.rect1, self.rect2))
        self.assertTrue(aabbCollision(self.rect1, self.rect3))

    def test_circleCircleCollision(self):
        self.assertFalse(circleCircleCollision(self.circle1, self.circle2))
        self.assertTrue(circleCircleCollision(self.circle1, self.circle3))

    def test_circleRectCollision(self):
        self.assertFalse(circleRectCollision(self.circle1, self.rect2))
        rect_near = RectangleSprite(0.5, 0, width=1, height=1)
        self.assertTrue(circleRectCollision(self.circle1, rect_near))

    def test_ellipseEllipseCollision(self):
        self.assertFalse(ellipseEllipseCollision(self.ellipse1, self.ellipse2))
        self.assertTrue(ellipseEllipseCollision(self.ellipse1, self.ellipse3))

    def test_ellipseRectCollision(self):
        self.assertFalse(ellipseRectCollision(self.ellipse1, self.rect2))
        rect_near = RectangleSprite(1, 0, width=2, height=2)
        self.assertTrue(ellipseRectCollision(self.ellipse1, rect_near))

    def test_circleEllipseCollision(self):
        self.assertFalse(circleEllipseCollision(self.circle1, self.ellipse2))
        ellipse_near = EllipseSprite(0.5, 0, radiusX=1, radiusY=0.5)
        self.assertTrue(circleEllipseCollision(self.circle1, ellipse_near))

    def test_polygonPolygonCollision(self):
        self.assertFalse(polygonPolygonCollision(self.poly1, self.poly2))
        self.assertTrue(polygonPolygonCollision(self.poly1, self.poly3))

    def test_polygonCircleCollision(self):
        self.assertFalse(polygonCircleCollision(self.poly1, self.circle2))
        self.assertTrue(polygonCircleCollision(self.poly1, self.circle3))

    def test_polygonRectCollision(self):
        self.assertFalse(polygonRectCollision(self.poly1, self.rect2))
        rect_near = RectangleSprite(0, 0, width=2, height=2)
        self.assertTrue(polygonRectCollision(self.poly1, rect_near))

    def test_polygonEllipseCollision(self):
        self.assertFalse(polygonEllipseCollision(self.poly1, self.ellipse2))
        ellipse_near = EllipseSprite(0.2, 0.2, radiusX=1, radiusY=1)
        self.assertTrue(polygonEllipseCollision(self.poly1, ellipse_near))

class CollisionRegistryTests(unittest.TestCase):
    def setUp(self):
        # Prepare overlapping instances for functional equivalence tests
        self.shape_map = {
            'RectangleSprite': RectangleSprite(1, 1, width=2, height=2),
            'CircleSprite': CircleSprite(1, 1, radius=1),
            'EllipseSprite': EllipseSprite(1, 1, radiusX=1, radiusY=1),
            'PolygonSprite': PolygonSprite(1, 1, numSides=4, radius=1)
        }
        # Expected direct functions mapping
        self.expected = {
            ('RectangleSprite','RectangleSprite'): aabbCollision,
            ('CircleSprite','CircleSprite'): circleCircleCollision,
            ('CircleSprite','RectangleSprite'): circleRectCollision,
            ('EllipseSprite','EllipseSprite'): ellipseEllipseCollision,
            ('EllipseSprite','RectangleSprite'): ellipseRectCollision,
            ('CircleSprite','EllipseSprite'): circleEllipseCollision,
            ('PolygonSprite','PolygonSprite'): polygonPolygonCollision,
            ('PolygonSprite','RectangleSprite'): polygonRectCollision,
            ('PolygonSprite','CircleSprite'): polygonCircleCollision,
            ('PolygonSprite','EllipseSprite'): polygonEllipseCollision
        }

    def test_registry_entries_and_symmetry(self):
        for (a,b), func in self.expected.items():
            # handler exist and callable
            self.assertIn((a,b), COLLISION_HANDLERS)
            handler = COLLISION_HANDLERS[(a,b)]
            self.assertTrue(callable(handler))
            # functional equivalence for overlapping shapes
            s1 = self.shape_map[a]
            s2 = self.shape_map[b]
            self.assertTrue(handler(s1, s2))
            # symmetry: same handler behavior when swapped
            handler_swapped = COLLISION_HANDLERS[(b,a)]
            self.assertTrue(callable(handler_swapped))
            self.assertTrue(handler_swapped(s2, s1))

class SpriteCollisionTests(unittest.TestCase):
    def test_overlaps_delegates_to_handler(self):
        rectA = RectangleSprite(0,0,2,2)
        rectB = RectangleSprite(3,3,2,2)
        self.assertEqual(rectA.overlaps(rectB), aabbCollision(rectA, rectB))

        circle = CircleSprite(0,0,1)
        rect_near = RectangleSprite(0.5,0,1,1)
        self.assertEqual(circle.overlaps(rect_near), circleRectCollision(circle, rect_near))

        polygon = PolygonSprite(0,0,3,1)
        circle_far = CircleSprite(5,5,1)
        self.assertEqual(polygon.overlaps(circle_far), polygonCircleCollision(polygon, circle_far))

    def test_collision_differs_by_drawMode(self):
        # two rectangles that just touch in one mode but not in the other
        r1 = RectangleSprite(100, 100, width=4, height=4)
        r2 = RectangleSprite(103, 103, width=4, height=4)
        # CORNER: they touch edges → collision
        r1.setDrawMode(CORNER)
        r2.setDrawMode(CORNER)
        self.assertTrue(r1.overlaps(r2))
        r1.setDrawMode(CENTER)
        r2.setDrawMode(CORNER)
        self.assertFalse(r1.overlaps(r2))
        r1.setDrawMode(CENTER)
        r2.setDrawMode(CENTER)
        self.assertTrue(r1.overlaps(r2))
        r1.setDrawMode(CORNER)
        r2.setDrawMode(CENTER)
        self.assertTrue(r1.overlaps(r2))

class EdgeCaseCollisionTests(unittest.TestCase):
    def test_touching_edges_count_as_collision(self):
        c1 = CircleSprite(0,0,1)
        c2 = CircleSprite(2,0,1)
        self.assertTrue(circleCircleCollision(c1, c2))
        r1 = RectangleSprite(0,0,2,2)
        r2 = RectangleSprite(2,0,2,2)
        self.assertTrue(aabbCollision(r1, r2))

    def test_zero_size_shapes(self):
        # zero-size vs non-zero at same location: collision
        rect_zero = RectangleSprite(0,0,0,0)
        rect = RectangleSprite(0,0,1,1)
        self.assertTrue(aabbCollision(rect_zero, rect))
        # zero-size vs non-zero far apart: no collision
        rect_far = RectangleSprite(5,5,1,1)
        self.assertFalse(aabbCollision(rect_zero, rect_far))

        circle_zero = CircleSprite(0,0,0)
        circle = CircleSprite(0,0,1)
        self.assertTrue(circleCircleCollision(circle_zero, circle))
        circle_far = CircleSprite(5,5,1)
        self.assertFalse(circleCircleCollision(circle_zero, circle_far))

class MixedDrawModeCollisionTests(unittest.TestCase):
    def test_circle_rect_collision_center_vs_corner(self):
        # Circle at (5,5), r=2 → spans [3→7]
        # Rectangle at (7,3), w=4,h=4 in CORNER → spans [7→11]×[3→7]
        c = CircleSprite(5, 5, radius=2)
        r = RectangleSprite(7, 3, width=4, height=4)
        c.setDrawMode(CENTER)
        r.setDrawMode(CORNER)
        # They touch along the vertical edge at x=7 → should count as collision
        self.assertTrue(circleRectCollision(c, r))
        self.assertTrue(c.overlaps(r))

    def test_ellipse_polygon_collision_corner_vs_center(self):
        # Ellipse center (10,10) → radiusX=3,radiusY=1 corners [10→16]×[10→12] if CORNER
        e = EllipseSprite(10, 10, radiusX=3, radiusY=1)
        p = PolygonSprite(15, 11, numSides=6, radius=2)
        e.setDrawMode(CORNER)
        p.setDrawMode(CENTER)
        # Their boxes overlap: [10,16]×[10,12] vs [13→17]×[9→13]
        self.assertTrue(polygonEllipseCollision(p, e))
        self.assertTrue(p.overlaps(e))

    def test_circle_ellipse_no_collision_mixed_modes(self):
        c = CircleSprite(0, 0, radius=1)
        e = EllipseSprite(3, 3, radiusX=1, radiusY=2)
        c.setDrawMode(CENTER)
        e.setDrawMode(CORNER)
        # Circle spans [-1→1], ellipse spans [3→5]×[3→5] → no overlap
        self.assertFalse(circleEllipseCollision(c, e))
        self.assertFalse(e.overlaps(c))


class ContainsPointTests(unittest.TestCase):
    def test_rectangle_contains_corner_and_center(self):
        r = RectangleSprite(0, 0, width=4, height=6)
        # CORNER: spans [0→4]×[0→6]
        r.setDrawMode(CORNER)
        self.assertTrue(r.contains(Point(2, 3)))
        self.assertFalse(r.contains(Point(5, 3)))
        # CENTER: center at (0,0) spans [-2→2]×[-3→3]
        r.setDrawMode(CENTER)
        self.assertTrue(r.contains(Point(1, -2)))
        self.assertFalse(r.contains(Point(3, 0)))

    def test_circle_contains_corner_and_center(self):
        c = CircleSprite(5, 5, radius=3)
        # CENTER (default): contains (5,5) and (8,5), excludes (9,5)
        self.assertTrue(c.contains(Point(5, 5)))
        self.assertTrue(c.contains(Point(8, 5)))
        self.assertFalse(c.contains(Point(9, 5)))
        # now treat x/y as corner: spans [5→11]×[5→11]
        c.setDrawMode(CORNER)
        self.assertTrue(c.contains(Point(6, 6)))
        self.assertFalse(c.contains(Point(4, 4)))


class TouchingEdgeBehaviorTests(unittest.TestCase):
    def test_edge_touching_rectangle_polygon(self):
        # Two polygons that just touch at one vertex
        p1 = PolygonSprite(200, 200, numSides=4, radius=20)
        p2 = PolygonSprite(240, 200, numSides=4, radius=20)
        p1.setDrawMode(CENTER)   # spans [-2→2], p2 spans [2→6]
        p2.setDrawMode(CENTER)
        # They share the line x=240 → should be True if you treat boundaries as collisions
        self.assertTrue(polygonPolygonCollision(p1, p2))

if __name__ == '__main__':
    unittest.main()

