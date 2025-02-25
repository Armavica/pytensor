import numpy as np
import pytest
from scipy.special import log_softmax as scipy_log_softmax
from scipy.special import softmax as scipy_softmax

from pytensor.compile.function import function
from pytensor.configdefaults import config
from pytensor.tensor.special import (
    LogSoftmax,
    Softmax,
    SoftmaxGrad,
    log_softmax,
    softmax,
)
from pytensor.tensor.type import matrix, tensor3, tensor4, vector
from tests import unittest_tools as utt


class TestSoftmax(utt.InferShapeTester):
    @pytest.mark.parametrize("axis", [None, 0, 1, 2, 3, -1, -2])
    def test_perform(self, axis):
        x = tensor4("x")
        rng = np.random.default_rng(utt.fetch_seed())
        xv = rng.standard_normal((2, 3, 4, 5)).astype(config.floatX)

        f = function([x], softmax(x, axis=axis))
        assert np.allclose(f(xv), scipy_softmax(xv, axis=axis))

    @pytest.mark.parametrize("column", [0, 1, 2, 3])
    @pytest.mark.parametrize("axis", [None, 0, 1])
    def test_grad(self, axis, column):
        def f(a):
            return softmax(a, axis=axis)[:, column]

        rng = np.random.default_rng(utt.fetch_seed())
        utt.verify_grad(f, [rng.random((3, 4, 2))])

    def test_infer_shape(self):
        admat = matrix()
        rng = np.random.default_rng(utt.fetch_seed())
        admat_val = rng.random((3, 4)).astype(config.floatX)
        self._compile_and_check(
            [admat], [Softmax(axis=-1)(admat)], [admat_val], Softmax
        )

    def test_vector_perform(self):
        x = vector()
        f = function([x], softmax(x, axis=None))

        rng = np.random.default_rng(utt.fetch_seed())
        xv = rng.standard_normal((6,)).astype(config.floatX)
        assert np.allclose(f(xv), scipy_softmax(xv))

    def test_vector_grad(self):
        def f(a):
            return softmax(a, axis=None)

        rng = np.random.default_rng(utt.fetch_seed())
        utt.verify_grad(f, [rng.random(4)])

    def test_valid_axis(self):
        with pytest.raises(TypeError):
            Softmax(1.5)

        x = [tensor3()] * LogSoftmax.nin
        Softmax(2)(*x)
        Softmax(-3)(*x)

        with pytest.raises(ValueError):
            Softmax(3)(*x)

        with pytest.raises(ValueError):
            Softmax(-4)(*x)


class TestLogSoftmax(utt.InferShapeTester):
    @pytest.mark.parametrize("column", [0, 1, 2, 3])
    @pytest.mark.parametrize("axis", [None, 0, 1])
    def test_matrix_grad(self, axis, column):
        def f(a):
            return log_softmax(a, axis=axis)[:, column]

        rng = np.random.default_rng(utt.fetch_seed())
        utt.verify_grad(f, [rng.random((3, 4))])

    def test_vector_perform(self):
        x = vector()
        f = function([x], log_softmax(x, axis=None))

        rng = np.random.default_rng(utt.fetch_seed())
        xv = rng.standard_normal((6,)).astype(config.floatX)
        assert np.allclose(f(xv), scipy_log_softmax(xv))

    def test_vector_grad(self):
        def f(a):
            return log_softmax(a, axis=None)

        rng = np.random.default_rng(utt.fetch_seed())
        utt.verify_grad(f, [rng.random((4,))])

    def test_valid_axis(self):
        with pytest.raises(TypeError):
            LogSoftmax(1.5)

        x = [tensor3()] * LogSoftmax.nin
        LogSoftmax(2)(*x)
        LogSoftmax(-3)(*x)

        with pytest.raises(ValueError):
            LogSoftmax(3)(*x)

        with pytest.raises(ValueError):
            LogSoftmax(-4)(*x)


class TestSoftmaxGrad(utt.InferShapeTester):
    def test_infer_shape(self):
        admat = matrix()
        bdmat = matrix()
        rng = np.random.default_rng(utt.fetch_seed())
        admat_val = rng.random((3, 4)).astype(config.floatX)
        bdmat_val = rng.random((3, 4)).astype(config.floatX)
        self._compile_and_check(
            [admat, bdmat],
            [SoftmaxGrad(axis=-1)(admat, bdmat)],
            [admat_val, bdmat_val],
            SoftmaxGrad,
        )

    def test_valid_axis(self):
        with pytest.raises(TypeError):
            SoftmaxGrad(1.5)

        x = [tensor3()] * SoftmaxGrad.nin
        SoftmaxGrad(2)(*x)
        SoftmaxGrad(-3)(*x)

        with pytest.raises(ValueError):
            SoftmaxGrad(3)(*x)

        with pytest.raises(ValueError):
            SoftmaxGrad(-4)(*x)
