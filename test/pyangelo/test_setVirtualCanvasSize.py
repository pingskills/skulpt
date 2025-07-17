import unittest
import document

class SetVirtualCanvasSizeTestCase(unittest.TestCase):

    def test_setVirtualCanvasSize_defaultYAxis(self):
        cw, ch, vw, vh = 800, 600, 400, 300
        # default yAxisMode should be CARTESIAN
        setVirtualCanvasSize(cw, ch, vw, vh)
        self.assertEqual(width, cw)
        self.assertEqual(height, ch)
        canvas = document.getElementById('canvas')
        self.assertEqual(canvas.style.display, "block")
        self.assertEqual(int(canvas.getAttribute("width")), cw)
        self.assertEqual(int(canvas.getAttribute("height")), ch)

    def test_setVirtualCanvasSize_explicitYAxis(self):
        cw, ch, vw, vh = 640, 480, 320, 240
        # explicit JAVASCRIPT mode should also work
        setVirtualCanvasSize(cw, ch, vw, vh, JAVASCRIPT)
        self.assertEqual(width, cw)
        self.assertEqual(height, ch)
        # we don’t inspect transforms here—just that no error is thrown

    def test_argumentCounts(self):
        # too few arguments
        with self.assertRaises(TypeError):
            setVirtualCanvasSize(1, 2, 3)
        # too many arguments
        with self.assertRaises(TypeError):
            setVirtualCanvasSize(1, 2, 3, 4, 5, 6)

    def test_argumentTypes(self):
        # non-int for canvasWidth
        with self.assertRaises(TypeError):
            setVirtualCanvasSize("a", 1, 1, 1)
        # non-int for canvasHeight
        with self.assertRaises(TypeError):
            setVirtualCanvasSize(1, "a", 1, 1)
        # non-int for virtualWidth
        with self.assertRaises(TypeError):
            setVirtualCanvasSize(1, 1, "a", 1)
        # non-int for virtualHeight
        with self.assertRaises(TypeError):
            setVirtualCanvasSize(1, 1, 1, "a")
        # non-int for yAxisMode
        with self.assertRaises(TypeError):
            setVirtualCanvasSize(1, 1, 1, 1, "a")

if __name__ == "__main__":
    unittest.main()
