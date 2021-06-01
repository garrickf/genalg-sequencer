"""
plot.py
author: garrick

Utilities for plotting. Think of this as a wrapper around matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from sklearn.neighbors import KNeighborsClassifier


def tsne_example():
    # From StackOverflow
    # (https://stackoverflow.com/questions/37718347/plotting-decision-boundary-for-high-dimension-data)
    np.random.seed(222)

    # replace the below with your data and model
    iris = load_iris()
    X, y = iris.data, iris.target
    model = LogisticRegression().fit(X, y)
    print("LogReg finished")
    y_predicted = model.predict(X)
    # replace the above with your data and model

    X_Train_embedded = TSNE(n_components=2).fit_transform(X)
    print("t-SNE shape", X_Train_embedded.shape)
    print("t-SNE finished")

    # create meshgrid
    resolution = 500  # resolution x resolution background pixels
    X2d_xmin, X2d_xmax = np.min(X_Train_embedded[:, 0]), np.max(X_Train_embedded[:, 0])
    X2d_ymin, X2d_ymax = np.min(X_Train_embedded[:, 1]), np.max(X_Train_embedded[:, 1])
    xx, yy = np.meshgrid(
        np.linspace(X2d_xmin, X2d_xmax, resolution),
        np.linspace(X2d_ymin, X2d_ymax, resolution),
    )

    # approximate Voronoi tesselation on (resolution, resolution) grid using 1-NN
    background_model = KNeighborsClassifier(n_neighbors=1).fit(
        X_Train_embedded, y_predicted
    )
    print("1-KNN train finished")

    # To make prediction, unravel the 2D resolution x resolution meshgrids and
    # concatenate them as if they were slice objects of the 1st and 2nd point
    voronoiBackground = background_model.predict(np.c_[xx.ravel(), yy.ravel()])
    print("1-KNN predict finished")
    voronoiBackground = voronoiBackground.reshape((resolution, resolution))

    # plot
    plt.contourf(xx, yy, voronoiBackground, alpha=0.3)
    plt.scatter(X_Train_embedded[:, 0], X_Train_embedded[:, 1], c=y, marker=".")
    plt.show()


def approx_voronoi_tesselation(model, X, labels, resolution=500, alpha=0.3):
    # Model should be fitted
    X_proj = TSNE(n_components=2, random_state=222).fit_transform(X)
    y_pred = model.predict(X)

    proj_xmin, proj_xmax = np.min(X_proj[:, 0]), np.max(X_proj[:, 0])
    proj_ymin, proj_ymax = np.min(X_proj[:, 1]), np.max(X_proj[:, 1])
    xx, yy = np.meshgrid(
        np.linspace(proj_xmin, proj_xmax, resolution),
        np.linspace(proj_ymin, proj_ymax, resolution),
    )

    # approximate Voronoi tesselation on (resolution, resolution) grid using 1-NN
    background_model = KNeighborsClassifier(n_neighbors=1).fit(X_proj, y_pred)
    voronoiBackground = background_model.predict(np.c_[xx.ravel(), yy.ravel()])
    voronoiBackground = voronoiBackground.reshape((resolution, resolution))

    plt.contourf(xx, yy, voronoiBackground, alpha=alpha)
    plt.scatter(X_proj[:, 0], X_proj[:, 1], c=labels, marker=".")


def tsne_scatter(X, labels):
    X_proj = TSNE(n_components=2, random_state=222).fit_transform(X)
    plt.scatter(X_proj[:, 0], X_proj[:, 1], c=labels, marker=".")
    return X_proj


def new_population_locations(
    model, X, labels, cur_population, resolution=500, alpha=0.3
):
    pop_size = len(cur_population)
    # Project both population and training data
    X_proj = TSNE(n_components=2, random_state=222).fit_transform(
        np.vstack([X, cur_population])
    )
    y_pred = model.predict(X)

    proj_xmin, proj_xmax = np.min(X_proj[:, 0]), np.max(X_proj[:, 0])
    proj_ymin, proj_ymax = np.min(X_proj[:, 1]), np.max(X_proj[:, 1])
    xx, yy = np.meshgrid(
        np.linspace(proj_xmin, proj_xmax, resolution),
        np.linspace(proj_ymin, proj_ymax, resolution),
    )

    # approximate Voronoi tesselation on (resolution, resolution) grid using 1-NN
    background_model = KNeighborsClassifier(n_neighbors=1).fit(X_proj[:-pop_size], y_pred)
    voronoiBackground = background_model.predict(np.c_[xx.ravel(), yy.ravel()])
    voronoiBackground = voronoiBackground.reshape((resolution, resolution))

    plt.contourf(xx, yy, voronoiBackground, alpha=alpha)
    plt.scatter(X_proj[:-pop_size, 0], X_proj[:-pop_size, 1], c=labels, marker=".")

    plt.show()
    plt.clf()

    plt.contourf(xx, yy, voronoiBackground, alpha=alpha)
    plt.scatter(X_proj[-pop_size:, 0], X_proj[-pop_size:, 1], marker=".")

    plt.show()
    plt.clf()


def population_histogram(all_populations):
    pass


if __name__ == "__main__":
    tsne_example()
