# Sprite.py
# Unified Sprite library

from easing import EASINGS, register_easing, Tween
from collision import (
    aabbCollision, circleCircleCollision, circleRectCollision,
    ellipseEllipseCollision, ellipseRectCollision, circleEllipseCollision,
    polygonPolygonCollision, polygonRectCollision, polygonCircleCollision,
    polygonEllipseCollision, COLLISION_HANDLERS
)
import math

# --- Utility functions ---
def clamp(val, minval, maxval):
    return max(minval, min(maxval, val))

# --- Base class for all transformable objects ---
class Transformable:
    def __init__(self, x=0, y=0, angle=0.0, anchorX=0.5, anchorY=0.5):
        self._x = x; self._y = y; self._angle = angle
        self._anchorX = clamp(anchorX, 0, 1)
        self._anchorY = clamp(anchorY, 0, 1)
        self._tweens = []
        self._hitTest = None; self._overlapTest = None

    # Tween API
    def tweenTo(self, propertyName, endValue, duration, easing=None):
        tw = Tween(self, propertyName, endValue, duration, easing)
        self._tweens.append(tw)
        return tw
    def update(self, dt):
        for tw in self._tweens[:]:
            tw.update(dt)
            if tw.finished:
                self._tweens.remove(tw)

    # Hit/Test overrides
    def setHitTest(self, fn): self._hitTest = fn
    def setOverlapTest(self, fn): self._overlapTest = fn

    def contains(self, point):
        if self._hitTest:
            return self._hitTest(self, point)
        return (point.x >= self.left and point.x <= self.right
                and point.y >= self.bottom and point.y <= self.top)

    def overlaps(self, other):
        if self._overlapTest:
            return self._overlapTest(self, other)
        key = (type(self).__name__, type(other).__name__)
        handler = COLLISION_HANDLERS.get(key)
        if handler:
            return handler(self, other)
        return aabbCollision(self, other)

    # Transform properties
    @property
    def x(self): return self._x
    @x.setter
    def x(self, v): self._x = v
    @property
    def y(self): return self._y
    @y.setter
    def y(self, v): self._y = v
    @property
    def angle(self): return self._angle
    @angle.setter
    def angle(self, v): self._angle = v

    # Anchor
    @property
    def anchorX(self): return self._anchorX
    @anchorX.setter
    def anchorX(self, v): self._anchorX = clamp(v, 0, 1)
    @property
    def anchorY(self): return self._anchorY
    @anchorY.setter
    def anchorY(self, v): self._anchorY = clamp(v, 0, 1)
    def setAnchor(self, ax, ay): self.anchorX, self.anchorY = ax, ay

    # Movement
    def moveBy(self, dx, dy): self.x += dx; self.y += dy
    def moveTo(self, x, y): self.x = x; self.y = y
    def rotateTo(self, angle): self.angle = angle
    def rotateBy(self, d): self.angle += d

    # Boundaries
    @property
    def left(self): return self.x
    @property
    def right(self): return self.x + self.width
    @property
    def bottom(self): return self.y
    @property
    def top(self): return self.y + self.height

    # Drawing (render only)
    def draw(self):
        saveState()
        if self.angle != 0.0:
            px = getattr(self, 'width', 0) * self.anchorX
            py = getattr(self, 'height',0) * self.anchorY
            translate(self.x + px, self.y + py)
            rotate(self.angle)
            translate(-px, -py)
        else:
            translate(self.x, self.y)
        self._render()
        restoreState()

# --- Image sprite ---
class Sprite(Transformable):
    """Image-based sprite (alias for backwards compatibility)"""
    def __init__(self, imageSource, x=0, y=0, width=None, height=None):
        super().__init__(x, y)
        self._imageFile = None
        self._image = None
        # Accept either a filename (str) or an already-loaded image object
        if isinstance(imageSource, str):
            self.imageFile = imageSource
            img = self._image
        else:
            img = imageSource
            self._image = img
            # try to preserve original file name if available
            self._imageFile = getattr(img, 'file', None)
        # Set dimensions
        self.width = width if width is not None else getattr(img, 'width', 0)
        self.height = height if height is not None else getattr(img, 'height', 0)
        self._opacity = None; self.opacity = 1
        self.hitboxScale = 1.0

    @property
    def imageFile(self):
        return self._imageFile

    @imageFile.setter
    def imageFile(self, f):
        self._imageFile = f
        self._image = Image(f)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, img):
        """Allow assigning a loaded image directly."""
        self._image = img
        # update size defaults if available
        try:
            self.width = img.width
            self.height = img.height
        except AttributeError:
            pass

    @property
    def left(self):
        full_w = self.width
        shrunk_w = full_w * self.hitboxScale
        # shift inwards by half the lost width to keep centered
        return self.x + (full_w - shrunk_w) / 2

    @property
    def right(self):
        full_w = self.width
        shrunk_w = full_w * self.hitboxScale
        return self.x + (full_w - shrunk_w) / 2 + shrunk_w

    @property
    def bottom(self):
        full_h = self.height
        shrunk_h = full_h * self.hitboxScale
        return self.y + (full_h - shrunk_h) / 2

    @property
    def top(self):
        full_h = self.height
        shrunk_h = full_h * self.hitboxScale
        return self.y + (full_h - shrunk_h) / 2 + shrunk_h

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, v):
        self._width = max(0, v)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, v):
        self._height = max(0, v)

    @property
    def opacity(self): return self._opacity
    @opacity.setter
    def opacity(self, v): self._opacity = max(0.0, min(1.0, v))

    def setHitboxScale(self, scale: float):
        """Scale hit-box between 0.0 (none) and 1.0 (full image)."""
        self.hitboxScale = clamp(scale, 0.0, 1.0)

    def _render(self):
        drawImage(self._image, 0, 0, self.width, self.height, opacity=self.opacity)

    def __repr__(self):
        return (f"Sprite(imageFile='{self.imageFile}', x={self.x}, y={self.y}, "
                f"width={self.width}, height={self.height}, opacity={self.opacity}, "
                f"angle={self.angle}, anchor=({self.anchorX},{self.anchorY}))")

# --- Text sprite ---
class TextSprite(Transformable):
    """Text-based sprite"""
    def __init__(self, textContent, x=0, y=0, fontSize=20, fontName="Arial"):
        super().__init__(x, y)
        self._textContent = textContent
        self._fontSize = fontSize
        self._fontName = fontName
        self.fillColour = Colour(255)
        self._strokeEnabled = False
        self.strokeColour = Colour(0)
        self._strokeWeight = 1
        self._recalculate_metrics()

    def _recalculate_metrics(self):
        metrics = measureText(self._textContent, self._fontSize, self._fontName)
        self.width = metrics["actualBoundingBoxLeft"] + metrics["actualBoundingBoxRight"]
        self.height = metrics["actualBoundingBoxAscent"] + metrics["actualBoundingBoxDescent"]

    @property
    def textContent(self): return self._textContent

    @textContent.setter
    def textContent(self, v):
        self._textContent = v
        self._recalculate_metrics()

    @property
    def fontSize(self): return self._fontSize

    @fontSize.setter
    def fontSize(self, v):
        self._fontSize = v
        self._recalculate_metrics()

    @property
    def fontName(self): return self._fontName

    @fontName.setter
    def fontName(self, v):
        self._fontName = v
        self._recalculate_metrics()

    def setColour(self, *args):
        """Set fill colour"""
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.fillColour = args[0] if isinstance(args[0], Colour) else Colour(*args)

    def setStroke(self, *args):
        """Set stroke colour"""
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.strokeColour = args[0] if isinstance(args[0], Colour) else Colour(*args)
        self._strokeEnabled = True

    def strokeWeight(self, w): self._strokeWeight = max(0, w)
    def noStroke(self): self._strokeEnabled = False

    def _render(self):
        fill(self.fillColour)
        if self._strokeEnabled:
            stroke(self.strokeColour)
            strokeWeight(self._strokeWeight)
        else:
            noStroke()
        text(self._textContent, 0, 0, self._fontSize, self._fontName)

    def __repr__(self):
        return (f"TextSprite(text='{self._textContent}', x={self.x}, y={self.y}, "
                f"fontSize={self._fontSize}, fontName='{self._fontName}', "
                f"fill=({self._fillR},{self._fillG},{self._fillB},{self.opacity}))")

    def __str__(self):
        return (f"TextSprite - '{self._textContent}' at ({self.x},{self.y}), "
                f"size=({self.width},{self.height}), font={self.fontName} {self.fontSize}, "
                f"fill=({self._fillR},{self._fillG},{self._fillB},{self.opacity})")

# --- Base for fillable and stroking shapes ---
class ShapeSprite(Transformable):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)
        self.fillColour = Colour(255)
        self._strokeEnabled = False
        self.strokeColour = Colour(0)
        self._strokeWeight = 1

    def setColour(self, *args):
        """Set fill colour"""
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.fillColour = args[0] if isinstance(args[0], Colour) else Colour(*args)

    def setStroke(self, *args):
        """Set stroke colour"""
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.strokeColour = args[0] if isinstance(args[0], Colour) else Colour(*args)
        self._strokeEnabled = True

    def strokeWeight(self, w): self._strokeWeight = max(0, w)
    def noStroke(self): self._strokeEnabled = False

    def _render(self):
        fill(self.fillColour)
        if self._strokeEnabled:
            stroke(self.strokeColour)
            strokeWeight(self._strokeWeight)
        else:
            noStroke()
        self._renderShape()

# --- Specific shape classes ---
class RectangleSprite(ShapeSprite):
    def __init__(self, x=0, y=0, width=0, height=0):
        super().__init__(x, y)
        self.width, self.height = width, height
    def _renderShape(self): rect(0, 0, self.width, self.height)
    def __repr__(self): return f"RectangleSprite(x={self.x},y={self.y},w={self.width},h={self.height})"

class CircleSprite(ShapeSprite):
    def __init__(self, x=0, y=0, radius=0):
        super().__init__(x, y)
        self.radius = radius
    @property
    def left(self): return self.x - self.radius
    @property
    def right(self): return self.x + self.radius
    @property
    def bottom(self): return self.y - self.radius
    @property
    def top(self): return self.y + self.radius
    def _renderShape(self): circle(0, 0, self.radius)
    def __repr__(self): return f"CircleSprite(x={self.x},y={self.y},r={self.radius})"

class EllipseSprite(ShapeSprite):
    def __init__(self, x=0, y=0, radiusX=0, radiusY=0):
        super().__init__(x, y)
        self.radiusX, self.radiusY = radiusX, radiusY
    @property
    def left(self): return self.x - self.radiusX
    @property
    def right(self): return self.x + self.radiusX
    @property
    def bottom(self): return self.y - self.radiusY
    @property
    def top(self): return self.y + self.radiusY
    def _renderShape(self): ellipse(0, 0, self.radiusX, self.radiusY)
    def __repr__(self): return f"EllipseSprite(x={self.x},y={self.y},rx={self.radiusX},ry={self.radiusY})"

class PolygonSprite(ShapeSprite):
    """Convex polygon sprite defined by number of sides and radius."""
    def __init__(self, x=0, y=0, numSides=3, radius=0):
        super().__init__(x, y)
        self.numSides = max(3, int(numSides))
        self.radius = max(0, radius)
    def _renderShape(self):
        beginShape()
        for i in range(self.numSides):
            ang = 2*math.pi*i/self.numSides
            vertex(self.radius*math.cos(ang), self.radius*math.sin(ang))
        endShape()
    def getVertices(self):
        verts=[]
        for i in range(self.numSides):
            ang = 2*math.pi*i/self.numSides + self.angle
            verts.append((self.x+ self.radius*math.cos(ang), self.y+ self.radius*math.sin(ang)))
        return verts
    def getAxes(self):
        verts = self.getVertices()
        axes=[]
        for i in range(len(verts)):
            x1,y1=verts[i]; x2,y2=verts[(i+1)%len(verts)]
            dx,dy=x2-x1,y2-y1; nx,ny= -dy,dx
            mag=math.hypot(nx,ny)
            axes.append((nx/mag,ny/mag))
        return axes
    def project(self, axis):
        projs=[v[0]*axis[0]+v[1]*axis[1] for v in self.getVertices()]
        return (min(projs), max(projs))
    def __repr__(self):
        return f"PolygonSprite(x={self.x},y={self.y},sides={self.numSides},r={self.radius})"
    def __str__(self):
        return f"PolygonSprite - sides:{self.numSides}, radius:{self.radius}, pos:({self.x},{self.y}), angle:{self.angle}"
