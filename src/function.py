"""
function.py
author: garrick

Function utility class. All functions can subclass this for consistent behavior
in the genetic algorithm optimizer.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression


class Function:
    def __init__(self) -> None:
        pass

    def eval(self, X: np.ndarray) -> np.ndarray:
        """Evaluate the function at a batch of design points x

        Args:
          X (np.ndarray): design matrix of shape (batch_size, n_dims)

        Returns:
          (np.ndarray): evaluations of objective function, shape 
          (batch_size, ).
        """
        raise NotImplementedError("Subclasses must override this function")

    def __call__(self, X: np.ndarray) -> np.ndarray:
        return self.eval(X)


# Useful for testing the genetic algorithm's correctness on a concrete objective
class RosenbrocksFunc(Function):
    def __init__(self, a: int = 1, b: int = 100) -> None:
        """Implements Rosenbrock's Banana Function (see M. Kochenderfer and T. 
        Wheeler, "Algorithms for Optimization," p. 430).

        Args:
          a (int): parameter in function. Global minimum will be at [a, a^2].
          b (int): another parameter
        """
        super().__init__()
        self.a = a
        self.b = b

    def eval(self, X: np.ndarray) -> np.ndarray:
        assert X.shape[1] == 2, f"Expected shape (batch_size, 2), got {X.shape}"
        # f(x) = (a − x1)^2 + b(x2 − x1^2)^2
        return self.b * (X[:, 1] - X[:, 0] ** 2) ** 2 + (self.a - X[:, 0]) ** 2


class BoothsFunc(Function):
    def __init__(self) -> None:
        """Implements Booths's Function (see M. Kochenderfer and T. Wheeler, 
        "Algorithms for Optimization," p. 426). Its global minimum is at [1, 3].
        """
        super().__init__()

    def eval(self, X: np.ndarray) -> np.ndarray:
        assert X.shape[1] == 2, f"Expected shape (batch_size, 2), got {X.shape}"
        # f(x) = (x1 + 2 * x2 − 7)^2 +(2 * x1 + x2 − 5)^2
        return (X[:, 0] + 2 * X[:, 1] - 7) ** 2 + (2 * X[:, 0] + X[:, 1] - 5) ** 2


# Useful for just letting the genetic algorithm explore
class UniformRandomFunc(Function):
    def __init__(self) -> None:
        super().__init__()

    def eval(self, X: np.ndarray) -> np.ndarray:
        batch_size = len(X)
        return np.random.random_sample((batch_size,))


class SurrogateFunc(Function):
    def __init__(self) -> None:
        """Superclass defining an objective/fitness function that is 
        approximated using a fit() class method.
        """
        super().__init__()

    def fit(self, X, labels, weights=None) -> None:
        """I'll put something here eventually...

        Args:
          X (np.ndarray): shape (batch_size, n_dim) array of labelled design points
          label (int): the label for the point (0 for dislike, 1 for like)
        """
        raise NotImplementedError("Subclasses must override this function")


class LogRegUserPreferenceFunc(SurrogateFunc):
    def __init__(self, random_state=222, **kwargs) -> None:
        super().__init__()
        self.model = LogisticRegression(random_state=random_state, **kwargs)
        self.is_fitted = False

    def fit(self, X, labels, weights=None) -> None:
        """NOTE weights allow for recency-based weighting of samples (earlier
        samples matter less than more recent ones).

        Also, NOTE fit will overwrite data
        """
        if 0 not in labels or 1 not in labels:  # Need one of each label
            return
        self.model.fit(X, labels, sample_weight=weights)
        self.is_fitted = True

    def eval(self, X: np.ndarray) -> np.ndarray:
        if self.is_fitted:
            # A lower objective value is better, so we use the probability that 
            # the user dislikes the design point. The lower this is, the better.
            return self.model.predict_proba(X)[:, 0]
        else:
            # Just return random values
            batch_size = len(X)
            return np.random.random_sample((batch_size,))
