# --- Collision handler implementations ---
import math

# --- Utility functions ---
def clamp(val, minval, maxval):
    return max(minval, min(maxval, val))

def aabbCollision(a, b):
    return (a.left <= b.right and a.right >= b.left
            and a.top >= b.bottom and a.bottom <= b.top)

def circleCircleCollision(c1, c2):
    dx = c1.centerX - c2.centerX; dy = c1.centerY - c2.centerY
    return dx*dx + dy*dy <= (c1.radius + c2.radius)**2

def circleRectCollision(circle, rect):
    cx = clamp(circle.centerX, rect.left, rect.right)
    cy = clamp(circle.centerY, rect.bottom, rect.top)
    dx = circle.centerX - cx; dy = circle.centerY - cy
    return dx*dx + dy*dy <= circle.radius**2

# --- Ellipse collision handlers ---

def ellipseEllipseCollision(e1, e2):
    dx = e1.centerX - e2.centerX; dy = e1.centerY - e2.centerY
    rx = e1.radiusX + e2.radiusX; ry = e1.radiusY + e2.radiusY
    return (dx*dx)/(rx*rx) + (dy*dy)/(ry*ry) <= 1

def ellipseRectCollision(ellipse, rect):
    cx = clamp(ellipse.centerX, rect.left, rect.right)
    cy = clamp(ellipse.centerY, rect.bottom, rect.top)
    dx = ellipse.centerX - cx; dy = ellipse.centerY - cy
    return (dx*dx)/(ellipse.radiusX**2) + (dy*dy)/(ellipse.radiusY**2) <= 1

def circleEllipseCollision(circle, ellipse):
    dx = circle.centerX - ellipse.centerX; dy = circle.centerY - ellipse.centerY
    rx = ellipse.radiusX + circle.radius; ry = ellipse.radiusY + circle.radius
    return (dx*dx)/(rx*rx) + (dy*dy)/(ry*ry) <= 1

# --- Polygon collision handlers (SAT) ---

def polygonPolygonCollision(p1, p2):
    axes = p1.getAxes() + p2.getAxes()
    for ax, ay in axes:
        min1, max1 = p1.project((ax, ay))
        min2, max2 = p2.project((ax, ay))
        if max1 < min2 or max2 < min1:
            return False
    return True

def polygonRectCollision(poly, rect):
    rect_pts = [(rect.left, rect.bottom), (rect.right, rect.bottom),
                (rect.right, rect.top), (rect.left, rect.top)]
    axes = poly.getAxes() + [(1, 0), (0, 1)]
    for ax, ay in axes:
        min1, max1 = poly.project((ax, ay))
        projs = [x*ax + y*ay for x, y in rect_pts]
        min2, max2 = min(projs), max(projs)
        if max1 < min2 or max2 < min1:
            return False
    return True

def polygonCircleCollision(poly, circle):
    axes = poly.getAxes()
    verts = poly.getVertices()
    cx, cy = circle.centerX, circle.centerY
    closest = min(verts, key=lambda v: (v[0]-cx)**2 + (v[1]-cy)**2)
    dx = closest[0] - cx; dy = closest[1] - cy
    length = math.hypot(dx, dy)
    if length > 0:
        axes.append((dx/length, dy/length))
    for ax, ay in axes:
        min1, max1 = poly.project((ax, ay))
        center_proj = cx*ax + cy*ay
        min2, max2 = center_proj - circle.radius, center_proj + circle.radius
        if max1 < min2 or max2 < min1:
            return False
    return True

def polygonEllipseCollision(poly, ellipse):
    axes = poly.getAxes()
    # Add the ellipse’s axes (its local X and Y, rotated by ellipse.angle)
    θ = math.radians(ellipse.angle)
    cos_t, sin_t = math.cos(θ), math.sin(θ)
    # local X-axis
    axes.append(( cos_t, sin_t))
    # local Y-axis
    axes.append((-sin_t, cos_t))

    # 3. For each axis, project both shapes and look for a gap
    for ax, ay in axes:
        # polygon projection
        min1, max1 = poly.project((ax, ay))
        # ellipse projection: centre ± radius along this axis
        center_proj = ellipse.centerX*ax + ellipse.centerY*ay
        # effective radius on this axis = rx*|ax| + ry*|ay|
        r = ellipse.radiusX*abs(ax) + ellipse.radiusY*abs(ay)
        min2, max2 = center_proj - r, center_proj + r

        if max1 < min2 or max2 < min1:
            return False

    return True

# --- Collision registry ---
COLLISION_HANDLERS = {
    ('RectangleSprite','RectangleSprite'): aabbCollision,
    ('CircleSprite','CircleSprite'):   circleCircleCollision,
    ('CircleSprite','RectangleSprite'): circleRectCollision,
    ('RectangleSprite','CircleSprite'): lambda r, c: circleRectCollision(c, r),
    ('EllipseSprite','EllipseSprite'): ellipseEllipseCollision,
    ('EllipseSprite','RectangleSprite'): ellipseRectCollision,
    ('RectangleSprite','EllipseSprite'): lambda r, e: ellipseRectCollision(e, r),
    ('CircleSprite','EllipseSprite'): circleEllipseCollision,
    ('EllipseSprite','CircleSprite'): lambda e, c: circleEllipseCollision(c, e),
    ('PolygonSprite','PolygonSprite'): polygonPolygonCollision,
    ('PolygonSprite','RectangleSprite'): polygonRectCollision,
    ('RectangleSprite','PolygonSprite'): lambda r, p: polygonRectCollision(p, r),
    ('PolygonSprite','CircleSprite'): polygonCircleCollision,
    ('CircleSprite','PolygonSprite'): lambda c, p: polygonCircleCollision(p, c),
    ('PolygonSprite','EllipseSprite'): polygonEllipseCollision,
    ('EllipseSprite','PolygonSprite'): lambda e, p: polygonEllipseCollision(p, e),
    ('CircleSprite','Sprite'): circleRectCollision,
    ('Sprite','CircleSprite'): lambda s, c: circleRectCollision(c, s),
    ('EllipseSprite','Sprite'): ellipseRectCollision,
    ('Sprite','EllipseSprite'): lambda s, e: ellipseRectCollision(e, s),
}

