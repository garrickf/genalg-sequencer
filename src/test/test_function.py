# Test functions.py
from function import *
import pytest


def test_function():
    f = Function()
    with pytest.raises(NotImplementedError):
        f(np.array([]))


def test_random_function():
    f = UniformRandomFunc()
    for batch_size in [1, 5, 10]:
        X = np.ones((batch_size, 10))
        y = f(X)
        assert y.shape == (batch_size,)


def test_rosenbrocks_function():
    f = RosenbrocksFunc(1, 5)
    for batch_size in [1, 5, 10]:
        X = np.ones((batch_size, 2))
        y = f(X)
        assert y.shape == (batch_size,)
        assert y[0] == 0  # minimum is at (1, 1)

    # Default: a = 1, b = 100
    f = RosenbrocksFunc()
    X = np.array([[1, 2]])
    y = f(X)
    assert y[0] == (1 - 1) ** 2 + 100 * (2 - 1 ** 2) ** 2
