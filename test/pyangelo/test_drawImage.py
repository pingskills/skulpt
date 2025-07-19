import unittest

class DrawImageTestCase(unittest.TestCase):

    def test_drawImage(self):
        img = Image("https://www.pyangelo.com/images/logos/pyangelo-logo.png")
        self.assertEqual(74, img.width)
        self.assertEqual(55, img.height)
        self.assertEqual("https://www.pyangelo.com/images/logos/pyangelo-logo.png", img.file)

        setCanvasSize(200, 200, CARTESIAN)
        background()
        drawImage(img, 0, 0)
        img.draw(100, 100, 10, 10)

    def test_drawImageIOError(self):
        with self.assertRaises(IOError):
           img = Image("https://www.pyangelo.com/no-such-image.png")

    def test_drawImageParameterTypes(self):
        with self.assertRaises(TypeError):
            drawImage()
        with self.assertRaises(TypeError):
            drawImage(1, 2)
        with self.assertRaises(TypeError):
            drawImage("file", "not a number", "not a number")

    def test_subImage_init(self):
        # Valid initialization
        sub = SubImage(10, 20, 30, 40)
        self.assertEqual(10, sub.x)
        self.assertEqual(20, sub.y)
        self.assertEqual(30, sub.width)
        self.assertEqual(40, sub.height)
        self.assertEqual("SubImage(10, 20, 30, 40)", repr(sub))

    def test_subImage_invalid_args(self):
        # Wrong types
        with self.assertRaises(TypeError):
            SubImage("a", 0, 10, 10)
        with self.assertRaises(TypeError):
            SubImage(0, "b", 10, 10)
        with self.assertRaises(TypeError):
            SubImage(0, 0, "c", 10)
        with self.assertRaises(TypeError):
            SubImage(0, 0, 10, "d")
        # Negative dimensions
        with self.assertRaises(ValueError):
            SubImage(0, 0, -10, 10)
        with self.assertRaises(ValueError):
            SubImage(0, 0, 10, -10)

    def test_drawSubImage_basic(self):
        img = Image("https://www.pyangelo.com/images/logos/pyangelo-logo.png")
        sub = SubImage(0, 0, img.width, img.height)
        setCanvasSize(200, 200, CARTESIAN)
        background()
        # draw at natural size (no scaling)
        img.drawSubImage(sub, 50, 50)
        # draw scaled to half size
        img.drawSubImage(sub, 100, 100, img.width // 2, img.height // 2)
        # If no exceptions are raised, test passes

    def test_drawSubImage_invalid_args(self):
        img = Image("https://www.pyangelo.com/images/logos/pyangelo-logo.png")
        sub = SubImage(0, 0, 10, 10)
        # Missing required args
        with self.assertRaises(TypeError):
            img.drawSubImage()
        with self.assertRaises(TypeError):
            img.drawSubImage(1, 2)
        # Wrong types for positions
        with self.assertRaises(TypeError):
            img.drawSubImage(sub, "x", "y")
        # Invalid subImage type
        with self.assertRaises(TypeError):
            img.drawSubImage("not a subimage", 0, 0)
        # Negative dimensions in SubImage
        bad_sub = SubImage(0, 0, 5, 5)
        # Manually tamper to invalid
        with self.assertRaises(ValueError):
            bad_sub.width = -5

if __name__ == "__main__":
    unittest.main()
