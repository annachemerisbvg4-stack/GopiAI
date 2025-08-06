import os
import tempfile
import unittest

import numpy as np

from txtai.vectors import Vectors, Recovery


class TestVectors(unittest.TestCase):
    """
    Vectors tests.
    """

    def testNotImplemented(self):
        vectors = Vectors(None, None, None)
        self.assertRaises(NotImplementedError, vectors.load, None)
        self.assertRaises(NotImplementedError, vectors.encode, None)

    def testNormalize(self):
        vectors = Vectors(None, None, None)
        data1 = np.random.rand(5, 5).astype(np.float32)
        data2 = data1.copy()
        original = data1.copy()
        vectors.normalize(data1)
        for x in data2:
            vectors.normalize(x)
        self.assertTrue(np.allclose(data1, data2))
        self.assertFalse(np.allclose(data1, original))

    def testRecovery(self):
        checkpoint = os.path.join(tempfile.gettempdir(), "recovery")
        os.makedirs(checkpoint, exist_ok=True)
        f = open(os.path.join(checkpoint, "id"), "w", encoding="utf-8")
        f.close()
        recovery = Recovery(checkpoint, "id")
        self.assertIsNone(recovery())

    def testNormalizeSingle(self):
        vectors = Vectors(None, None, None)
        vector = np.random.rand(5).astype(np.float32)
        original = vector.copy()
        vectors.normalize(vector)
        self.assertFalse(np.allclose(vector, original))
        self.assertTrue(np.isclose(np.linalg.norm(vector), 1.0))

    def testRecoveryNoCheckpoint(self):
        checkpoint = os.path.join(tempfile.gettempdir(), "nonexistent")
        recovery = Recovery(checkpoint, "id")
        self.assertIsNone(recovery())