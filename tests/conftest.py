import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


@pytest.fixture
def rng():
    return np.random.default_rng(12345)


@pytest.fixture
def sample_data(rng):
    return pd.DataFrame(
        {
            "x": rng.normal(size=120),
            "y": rng.normal(size=120),
            "category": np.repeat(["A", "B", "C"], 40),
        }
    )


@pytest.fixture
def three_groups(rng):
    return pd.DataFrame(
        {
            "g": np.repeat(["A", "B", "C"], 50),
            "y": np.concatenate(
                [rng.normal(0, 1, 50), rng.normal(0.6, 1, 50), rng.normal(1.5, 1, 50)]
            ),
        }
    )
