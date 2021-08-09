import sys, os
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import unittest 
from binary import Binary
import numpy as np


class TestSum(unittest.TestCase):
    def test_all_cmps(self):
        TESTDATA = [1, 2, 256, 255, 1024, 0]
        for x in TESTDATA:
            for y in TESTDATA:
                xx = Binary(x)
                yy = Binary(y)

                self.assertEqual(xx==yy, x==y)
                self.assertEqual(xx!=yy, x!=y)
                self.assertEqual(xx>yy, x>y)
                self.assertEqual(xx>=yy, x>=y)
                self.assertEqual(xx<yy, x<y)
                self.assertEqual(xx<=yy, x<=y)

                self.assertEqual(x==yy, x==y)
                self.assertEqual(x!=yy, x!=y)
                self.assertEqual(x>yy, x>y)
                self.assertEqual(x>=yy, x>=y)
                self.assertEqual(x<yy, x<y)
                self.assertEqual(x<=yy, x<=y)

                self.assertEqual(xx==y, x==y)
                self.assertEqual(xx!=y, x!=y)
                self.assertEqual(xx>y, x>y)
                self.assertEqual(xx>=y, x>=y)
                self.assertEqual(xx<y, x<y)
                self.assertEqual(xx<=y, x<=y)

    def test_construction(self):
        value = Binary(0)
        self.assertTrue((value._data==np.array([0], dtype=np.uint8)).all())
        self.assertEqual(value._len, 1)

        value = Binary(1)
        self.assertTrue((value._data==np.array([1], dtype=np.uint8)).all())
        self.assertEqual(value._len, 1)

        value = Binary(255)
        self.assertTrue((value._data==np.array([255], dtype=np.uint8)).all())
        self.assertEqual(value._len, 8)

        value = Binary(256)
        self.assertTrue((value._data==np.array([0, 1], dtype=np.uint8)).all())
        self.assertEqual(value._len, 9)

        value = Binary("0000")
        self.assertTrue((value._data==np.array([0], dtype=np.uint8)).all())
        self.assertEqual(value._len, 4)

        value = Binary("0   1 1 0")
        self.assertTrue((value._data==np.array([6], dtype=np.uint8)).all())
        self.assertEqual(value._len, 4)

        value = Binary("FF")
        self.assertTrue((value._data==np.array([255], dtype=np.uint8)).all())
        self.assertEqual(value._len, 8)

        value = Binary("0b1111")
        self.assertTrue((value._data==np.array([15], dtype=np.uint8)).all())
        self.assertEqual(value._len, 4)

        value = Binary([True, True, 0, 0.0])
        self.assertEqual(value, "1100")
        self.assertEqual(value._len, 4)

        value = Binary(0,bytes_lenght=2)
        self.assertEqual(value, 0)
        self.assertEqual(value._len, 16)

        with self.assertRaises(Exception):
            value = Binary(0,bytes_lenght=2, bit_lenght=1)
        
    def test_assigns(self):
        x = Binary("0000 0000")
        y = Binary("101")
        x[0] = True
        self.assertEqual(str(x), "00000001")
        x[1] = True
        self.assertEqual(str(x), "00000011")
        x[-1] = True
        self.assertEqual(str(x), "10000011")
        x[0] = False
        self.assertEqual(str(x), "10000010")

        self.assertEqual(x[0], False)
        self.assertEqual(x[1], True)
        self.assertEqual(x[2], False)
        
        self.assertEqual(x[0:3], "010")
        self.assertEqual(x[:3], "010")
        self.assertEqual(x[-3:], "100")
        
        x[:3] = y
        self.assertEqual(str(x), "10000101")

        x[4:] = 1
        self.assertEqual(str(x), "11110101")

        x[:4] = 0
        self.assertEqual(str(x), "11110000")

        x[1:4] = y
        self.assertEqual(str(x), "11111010")

        x[:] = False
        self.assertEqual(str(x), "00000000")

        x[:] = False
        self.assertEqual(str(x), "00000000")

        with self.assertRaises(Exception):
            x[0:1] = "1111 1111"
        with self.assertRaises(Exception):
            x[0:100] = "11" 
        with self.assertRaises(Exception):
            x[-100:1] = "1111 1111"

        x[[1,3,5]] = True
        self.assertEqual(str(x), "00101010")

if __name__ == '__main__':
    unittest.main()