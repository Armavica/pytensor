import pickle

import numpy as np

from tests import unittest_tools as utt
from theano import function
from theano.compile.ops import as_op
from theano.configdefaults import config
from theano.tensor.basic import Rebroadcast
from theano.tensor.type import TensorType, dmatrix, dtensor4, dvector


@as_op([dmatrix, dmatrix], dmatrix)
def mul(a, b):
    """
    This is for test_pickle, since the function still has to be
    reachable from pickle (as in it cannot be defined inline)
    """
    return a * b


class TestOpDecorator(utt.InferShapeTester):
    def test_1arg(self):
        x = dmatrix("x")

        @as_op(dmatrix, dvector)
        def cumprod(x):
            return np.cumprod(x)

        fn = function([x], cumprod(x))
        r = fn([[1.5, 5], [2, 2]])
        r0 = np.array([1.5, 7.5, 15.0, 30.0])

        assert np.allclose(r, r0), (r, r0)

    def test_2arg(self):
        x = dmatrix("x")
        x.tag.test_value = np.zeros((2, 2))
        y = dvector("y")
        y.tag.test_value = [0, 0, 0, 0]

        @as_op([dmatrix, dvector], dvector)
        def cumprod_plus(x, y):
            return np.cumprod(x) + y

        fn = function([x, y], cumprod_plus(x, y))
        r = fn([[1.5, 5], [2, 2]], [1, 100, 2, 200])
        r0 = np.array([2.5, 107.5, 17.0, 230.0])

        assert np.allclose(r, r0), (r, r0)

    def test_infer_shape(self):
        x = dmatrix("x")
        x.tag.test_value = np.zeros((2, 2))
        y = dvector("y")
        y.tag.test_value = [0, 0, 0, 0]

        def infer_shape(fgraph, node, shapes):
            x, y = shapes
            return [y]

        @as_op([dmatrix, dvector], dvector, infer_shape)
        def cumprod_plus(x, y):
            return np.cumprod(x) + y

        self._compile_and_check(
            [x, y],
            [cumprod_plus(x, y)],
            [[[1.5, 5], [2, 2]], [1, 100, 2, 200]],
            cumprod_plus.__class__,
            warn=False,
        )

    def test_pickle(self):
        x = dmatrix("x")
        y = dmatrix("y")

        m = mul(x, y)

        s = pickle.dumps(m)
        m2 = pickle.loads(s)

        assert m2.owner.op == m.owner.op


class TestRebroadcast(utt.InferShapeTester):
    def test_rebroadcast(self):
        rng = np.random.RandomState(3453)
        # Rebroadcast
        adtens4 = dtensor4()
        adict = [(0, False), (1, True), (2, False), (3, True)]
        adtens4_val = rng.rand(2, 1, 3, 1).astype(config.floatX)
        self._compile_and_check(
            [adtens4],
            [Rebroadcast(*adict)(adtens4)],
            [adtens4_val],
            Rebroadcast,
            warn=False,
        )

        adtens4_bro = TensorType("float64", (True, True, True, False))()
        bdict = [(0, True), (1, False), (2, False), (3, False)]
        adtens4_bro_val = rng.rand(1, 1, 1, 3).astype(config.floatX)
        self._compile_and_check(
            [adtens4_bro],
            [Rebroadcast(*bdict)(adtens4_bro)],
            [adtens4_bro_val],
            Rebroadcast,
        )