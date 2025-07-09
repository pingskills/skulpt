import unittest

class TextTestCase(unittest.TestCase):

    def test_text(self):
        setCanvasSize(400, 400, CARTESIAN)
        background(255, 255, 255)
        fill(0, 0, 0)
        text("Hello", 0, 0, 100)
        bgColour = getPixelColour(12, 12)
        self.assertEqual(bgColour.red, 0)
        self.assertEqual(bgColour.green, 0)
        self.assertEqual(bgColour.blue, 0)

        setCanvasSize(400, 400, JAVASCRIPT)
        background(255, 255, 255)
        fill(0, 0, 0)
        text("Hello", 0, 0, 100)
        bgColour = getPixelColour(12, 12)
        self.assertEqual(bgColour.red, 0)
        self.assertEqual(bgColour.green, 0)
        self.assertEqual(bgColour.blue, 0)

    def test_textStroke(self):
        setCanvasSize(200, 200, CARTESIAN)
        background(255, 255, 255)
        fill(0, 0, 0)
        stroke(255, 0, 0)        # red outline
        strokeWeight(4)
        text("X", 0, 0, 80)
        # pick a pixel just outside the fill area, where the red stroke should sit
        edgeColour = getPixelColour(3, 7)
        self.assertEqual(edgeColour.red, 255)
        self.assertEqual(edgeColour.green, 0)
        self.assertEqual(edgeColour.blue, 0)

    def test_noStroke(self):
        setCanvasSize(200, 200, JAVASCRIPT)
        background(255, 255, 255)
        fill(0, 255, 0)
        stroke(0, 0, 255)
        strokeWeight(4)
        noStroke()               # disable outline
        text("Y", 0, 0, 80)
        # even though stroke() was called, noStroke() should suppress it
        edgeColour = getPixelColour(3, 6)
        self.assertEqual(edgeColour.red, 255)
        self.assertEqual(edgeColour.green, 255)
        self.assertEqual(edgeColour.blue, 255)

    def test_textParameterTypes(self):
        with self.assertRaises(TypeError):
            text("Hello", "not a number", 100, 32)
        with self.assertRaises(TypeError):
            text("Hello", 100.5, "not a number", 32)
        with self.assertRaises(TypeError):
            text("Hello", 100, 100, "not an int")
        with self.assertRaises(TypeError):
            text("Hello", 100, 100, 100.5)
        with self.assertRaises(TypeError):
            text("Hello", 100, 100, "not an int")

if __name__ == "__main__":
    unittest.main()
