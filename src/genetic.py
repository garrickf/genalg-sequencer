"""
genetic.py
author: garrick

Main file for genetic algorithm.
"""
import math
from collections import namedtuple

import matplotlib.pyplot as plt
import numpy as np

from function import BoothsFunc, RosenbrocksFunc, UniformRandomFunc

N_INSTRUMENTS = 8
EXPRESSION_DIM = 16
TIMING_DIM = 16
BAR_SIZE = 4
N_BARS = TIMING_DIM // BAR_SIZE
POPULATION_SIZE = 20

"""Generative music dynamics"""


def init_chromosome():
    """
    Returns:
      (np.ndarray) chromosome of shape (1 + expression_dim + timing_dim,)
    """
    instrument = np.random.choice(np.arange(N_INSTRUMENTS))
    expression = np.random.random_sample(EXPRESSION_DIM)
    timing = np.random.random_sample(TIMING_DIM) < 0.75
    return np.hstack([instrument, expression, timing])


def get_instrument(chromosome):
    return int(chromosome[0])


def get_expression(chromosome):
    """
    Returns:
      (np.ndarray): copy of the expression information
    """
    return chromosome[1 : EXPRESSION_DIM + 1].copy()


def get_timing(chromosome):
    """
    Args:
      chromosome (np.ndarray): the chromosome
    
    Returns:
      (np.ndarray): copy of the timing information, as integers
    """
    return chromosome[EXPRESSION_DIM + 1 :].copy().astype(np.int32)


def set_instrument(chromosome, instrument):
    chromosome[0] = instrument


def set_expression(chromosome, expression):
    chromosome[1 : EXPRESSION_DIM + 1] = expression


def set_timing(chromosome, timing):
    chromosome[EXPRESSION_DIM + 1 :] = timing


def roulette_wheel_selection(y):
    """Performs roulette wheel selection, also known as fitness proportionate
    selection. Each parent is chosen with a probability proportional to its 
    performance relative to the population. This process can be run multiple 
    times to select different parents.

    This approach mirrors the one described in the book (p. 151); we assign zero
    probability mass to the individual with the worst/highest objective value.

    Args:
      y (np.ndarray): Fitness function evaluations of shape (batch_size, )
    
    Returns:
      (int): Index of the selected individual. Why, congratulations, <individual>!
    """
    likelihood = np.max(y) - y  # NOTE max will have likelihood of zero
    probs = likelihood / np.sum(likelihood)
    return np.random.choice(np.arange(len(y)), p=probs)


def mutate(chromosome, m_ins_prob=0.1, m_exp_prob=0.1, m_tim_prob=0.1):
    """

    Returns:
      (np.ndarray): A new, mutated chromosome. *Does not* modify the old one.
    """
    mutated = chromosome.copy()

    if np.random.random_sample() < m_ins_prob:
        set_instrument(mutated, np.random.choice(np.arange(N_INSTRUMENTS)))

    new_expression = np.random.random_sample(EXPRESSION_DIM)

    mask = np.random.random_sample((TIMING_DIM,)) < m_exp_prob
    new_expression = get_expression(mutated)
    new_expression[mask] = np.random.random_sample(np.count_nonzero(mask))
    set_expression(mutated, new_expression)

    # Randomly flip bits according to m_tim_prob
    mask = np.random.random_sample((TIMING_DIM,)) < m_tim_prob
    new_timing = get_timing(mutated)
    new_timing[mask] = 1 - new_timing[mask]
    set_timing(mutated, new_timing)

    return mutated


def crossover(c1, c2):
    # Choose instrument from c1 or c2
    new_instrument = np.random.choice([get_instrument(c1), get_instrument(c2)])

    # Pick each expression parameter from either c1 or c2
    idxs = np.random.randint(2, size=EXPRESSION_DIM)  # Pick either from 0 or 1
    new_expression = np.vstack([get_expression(c1), get_expression(c2)]).T[
        np.arange(EXPRESSION_DIM), idxs
    ]

    # Pick bars (groups of beats) from either c1 or c2
    idxs = np.random.randint(2, size=N_BARS)
    new_timing = np.stack(
        [
            get_timing(c1).reshape(N_BARS, BAR_SIZE),
            get_timing(c2).reshape(N_BARS, BAR_SIZE),
        ],
        axis=1,
    )[np.arange(N_BARS), idxs]
    new_timing = new_timing.flatten()

    return np.hstack([new_instrument, new_expression, new_timing])


GenAlgDynamics = namedtuple(
    "GenAlgDynamics", ["init", "selection", "crossover", "mutate"]
)
music_dynamics = GenAlgDynamics(
    init=init_chromosome,
    selection=roulette_wheel_selection,
    crossover=crossover,
    mutate=mutate,
)

"""Configurable genetic algorithm"""


def genetic_algorithm_step(
    population, f, dynamics: GenAlgDynamics = music_dynamics, pop_size=POPULATION_SIZE,
):
    """
    Args:
      f (Function): An instance of a Function; the objective function to 
        evaluate.
    
    """
    selection, crossover, mutate = (
        dynamics.selection,
        dynamics.crossover,
        dynamics.mutate,
    )

    # Evaluate fitness
    y = f(population)
    # print("avg y", np.mean(y))
    # print("best y", np.min(y), population[np.argmin(y)])

    # Select parents of the next generation
    parent_idxs = [(selection(y), selection(y)) for _ in range(pop_size)]
    parents = [(population[a], population[b]) for a, b in parent_idxs]

    # Perform crossover
    proto = [crossover(c1, c2) for c1, c2 in parents]

    # Perform mutation
    new_population = np.array([mutate(c) for c in proto])

    return new_population, np.argsort(y), y


GenAlgHistory = namedtuple("GenAlgHistory", ["populations", "argsorts", "evals"])


def genetic_algorithm(
    function=UniformRandomFunc,
    dynamics: GenAlgDynamics = music_dynamics,
    max_iters=30,
    pop_size=POPULATION_SIZE,
) -> GenAlgHistory:
    """Runs genetic algorithm to optimize a given function with specified 
    evolutionary dynamics.

    NOTE n_iters generations produces a history object with n_iters + 1 entries
    (count the initial population, too)
    """
    init_chromosome = dynamics.init
    iter = 0
    population = np.array([init_chromosome() for _ in range(pop_size)])
    f = function()

    all_populations = [population]
    all_argsorts = []
    all_evals = []

    while iter < max_iters:
        # print(f"Iteration {iter}")

        # XXX: could measure differences? or cache and plot?
        population, argsort, evals = genetic_algorithm_step(
            population, f, dynamics=dynamics, pop_size=pop_size
        )
        all_populations.append(population)
        all_argsorts.append(argsort)
        all_evals.append(evals)

        iter += 1

    return GenAlgHistory(
        populations=all_populations, argsorts=all_argsorts, evals=all_evals
    )


"""Rosenbrock's Function"""


def rosenbrocks_init_chromosome():
    return np.random.random_sample(2) * 6 - 3  # 3, -3


# def rosenbrocks_crossover(c1, c2, lambd=0.5):
#     return (1 - lambd) * c1 + lambd * c2


def rosenbrocks_crossover(c1, c2):
    mask = np.random.random_sample(2) < 0.5
    new_c = c1.copy()
    new_c[mask] = c2[mask]
    return new_c


def rosenbrocks_mutation(c):
    scale = np.random.choice([1, 0.1, 0.01], p=[0.05, 0.3, 0.65])
    new_c = c + (np.random.random_sample(2) * scale - scale / 2)
    return np.clip(new_c, -3, 3)


def truncation_selection(y, sample_size=5):
    top_idxs = np.argsort(y)[:sample_size]  # Lower objective values are better
    return np.random.choice(top_idxs)


rosenbrock_problem = GenAlgDynamics(
    init=rosenbrocks_init_chromosome,
    selection=truncation_selection,
    crossover=rosenbrocks_crossover,
    mutate=rosenbrocks_mutation,
)

"""Booths's Function"""


def booths_init_chromosome():
    return np.random.random_sample(2) * 20 - 10  # -10, 10


booths_crossover = rosenbrocks_crossover


def booths_mutation(c):
    scale = np.random.choice([1, 0.1, 0.01], p=[0.05, 0.3, 0.65])
    new_c = c + (np.random.random_sample(2) * scale - scale / 2)
    return np.clip(new_c, -10, 10)


booths_problem = GenAlgDynamics(
    init=booths_init_chromosome,
    selection=truncation_selection,
    crossover=booths_crossover,
    mutate=booths_mutation,
)

"""Plotting code"""


def log_level_locator(z, n=20, base=1.5, exclude_first=10):
    """ Selects contour lines on a logarithmic scale. Useful for getting more 
    information out of relatively flat valleys, like in Rosenbrock's (Banana)
    function.
    """
    vmin, vmax = np.min(z), np.max(z)
    if vmin == 0:
        vmin = 1e-1
    lines = np.logspace(
        math.log(vmin, base), math.log(vmax, base), n, base=base
    ).tolist()

    # The first few lines are very tightly spaced, so exclude them
    return lines[exclude_first:]


def create_contours(function=RosenbrocksFunc, log=True):
    if function == BoothsFunc:
        bound = 10
    else:
        bound = 3

    x1 = np.linspace(-bound, bound, 100)
    x2 = np.linspace(-bound, bound, 100)
    X = np.meshgrid(x1, x2)  # Index 0 is all x1 coordinates, 1 is all x2; vectorizes

    eval_X = np.array([[x1, x2] for x1, x2 in zip(X[0].flatten(), X[1].flatten())])

    f = function()
    Z = f(eval_X)
    Z = np.array(Z).reshape([100, 100])

    if log:
        plt.contour(X[0], X[1], Z, levels=log_level_locator(Z), cmap="viridis_r")
    else:
        plt.contour(X[0], X[1], Z, levels=10, cmap="viridis_r")


def plot_populations(history: GenAlgHistory, function=RosenbrocksFunc):
    # Plot a generation of design points
    for generation in [0, 1, 2, 3, 4, 5, 9, 99, -501, -101, -1]:
        pop = history.populations[generation]
        create_contours(function)
        plt.scatter(pop[:, 0], pop[:, 1], zorder=2, marker=".")
        # XXX: Why do I have to change z-order?
        plt.xlabel("x1")
        plt.ylabel("x2")
        plt.title(
            f"Generation {generation + 1 if generation >= 0 else len(history.populations) + generation + 1}"
        )
        plt.show()
        # TODO: could animate sequence (and save plots)
        plt.clf()


# TODO: add argparse, allow running different trials
TRIAL = "rosenbrocks"

if __name__ == "__main__":
    np.random.seed(222)

    if TRIAL == "rosenbrocks":
        history = genetic_algorithm(RosenbrocksFunc, rosenbrock_problem, max_iters=999)

        plot_populations(history)
    elif TRIAL == "booths":
        history = genetic_algorithm(BoothsFunc, booths_problem, max_iters=999)

        plot_populations(history, BoothsFunc)
