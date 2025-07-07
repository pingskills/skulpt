# --- Tweening support and easing functions ---
import math

def linear_easing(t: float) -> float:
    """Linear easing function (no acceleration)."""
    return t

# --- New easing functions ---

def ease_in_quad(t: float) -> float:
    return t * t

def ease_out_quad(t: float) -> float:
    return t * (2 - t)

def ease_in_out_quad(t: float) -> float:
    return 2*t*t if t < 0.5 else -1 + (4 - 2*t)*t

def ease_in_cubic(t: float) -> float:
    return t * t * t

def ease_out_cubic(t: float) -> float:
    t1 = t - 1
    return t1 * t1 * t1 + 1

def ease_in_out_cubic(t: float) -> float:
    return 4*t*t*t if t < 0.5 else (t - 1)*(2*t - 2)*(2*t - 2) + 1

def ease_in_sine(t: float) -> float:
    return 1 - math.cos((t * math.pi) / 2)

def ease_out_sine(t: float) -> float:
    return math.sin((t * math.pi) / 2)

def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2

def ease_out_bounce(t: float) -> float:
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t2 = t - (1.5 / d1)
        return n1 * t2 * t2 + 0.75
    elif t < 2.5 / d1:
        t2 = t - (2.25 / d1)
        return n1 * t2 * t2 + 0.9375
    else:
        t2 = t - (2.625 / d1)
        return n1 * t2 * t2 + 0.984375

def ease_out_elastic(t: float) -> float:
    c4 = (2 * math.pi) / 3
    if t == 0:
        return 0
    if t == 1:
        return 1
    return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

# Mapping names to functions for convenience
EASINGS = {
    'linear': linear_easing,
    'ease_in_quad': ease_in_quad,
    'ease_out_quad': ease_out_quad,
    'ease_in_out_quad': ease_in_out_quad,
    'ease_in_cubic': ease_in_cubic,
    'ease_out_cubic': ease_out_cubic,
    'ease_in_out_cubic': ease_in_out_cubic,
    'ease_in_sine': ease_in_sine,
    'ease_out_sine': ease_out_sine,
    'ease_in_out_sine': ease_in_out_sine,
    'ease_out_bounce': ease_out_bounce,
    'ease_out_elastic': ease_out_elastic,
}

def register_easing(name: str, fn):
    """Register a custom easing function by name."""
    if callable(fn):
        EASINGS[name] = fn

class Tween:
    """Animates a single numeric property on a target over time."""
    def __init__(self, target, propertyName, endValue, duration, easing=None):
        self.target = target
        self.propertyName = propertyName
        self.startValue = getattr(target, propertyName)
        self.endValue = endValue
        self.duration = max(0.0001, duration)
        # Accept either a function or a string key
        if callable(easing):
            self.easing = easing
        else:
            # lookup by name, fallback to linear
            self.easing = EASINGS.get(easing, linear_easing)
        self.elapsed = 0.0
        self.finished = False
        self._callbacks = []

    def update(self, dt):
        if self.finished:
            return
        self.elapsed += dt
        progress = min(self.elapsed / self.duration, 1.0)
        factor = self.easing(progress)
        current = self.startValue + (self.endValue - self.startValue) * factor
        setattr(self.target, self.propertyName, current)
        if progress >= 1.0:
            self.finished = True
            for cb in self._callbacks:
                cb()

    def onComplete(self, callback):
        """Register a callback to run when tween finishes."""
        self._callbacks.append(callback)
        return self

    def cancel(self):
        """Stop the tween immediately."""
        self.finished = True
        return self

