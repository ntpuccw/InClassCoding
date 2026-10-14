
import numpy as np
from scipy.stats import norm, t, chi2, uniform, skewnorm,skew, kurtosis



distributions = {
    'Normal': lambda size: norm.rvs(size=size),
    'T(10)': lambda size: t.rvs(df=10, size=size),
    'Uniform': lambda size: uniform.rvs(loc=-3, scale=6, size=size),
    'Chi_2(20)': lambda size: chi2.rvs(df=20, size=size),
    'skewed Normal(2)': lambda size: skewnorm.rvs(a=2, loc=0, scale=1, size=size),
    'skewed Normal(-4)': lambda size: skewnorm.rvs(a=-4, loc=0, scale=1, size=size)
}

def generate_data(distribution, size, N=10000, seed=42):
    """
    Generates sample data for a certain distribution.

    Input Args:
        distribution: The type of distribution to generate data for.
        size: The number of samples to generate.
        N: number of Monte Carlo samples to generate for each sample.
        seed: The random seed to use for reproducibility.

    Returns:
        sample data
    """
    size_MC = (N, size) # (number of MC samples, number of samples)
    sample_data = distributions[distribution](size=size_MC)
    return sample_data


def JB_statistic(sample_data):
    """
    Computes the JB statistic by formula for the given data.

    Args:
        sample_data: The data to compute the statistic for.
    
    Returns:
        JB_stat: The computed JB statistic.
        JB_p_value: The p-value associated with the JB statistic.
    """
    n_val = sample_data.shape[1]
    samples = sample_data
    g1_val = np.sqrt(n_val / 6) * skew(samples, axis=1, bias=False)
        # compute G2
    g2_val = kurtosis(samples, axis=1, fisher=True, bias=False)
    g2_val = np.sqrt(n_val / 24) * g2_val
    JB_stat = g1_val**2 + g2_val**2
    
    JB_p_value = 1 - chi2.cdf(JB_stat, df=2)
    return {'statistic': JB_stat, 'p_value': JB_p_value}

# def normality_test(sample_data, test, alpha=0.05):
#     """
#     Performs a normality test on the given data.

#     Args:
#         sample_data: The data to test for normality.
#         test: The type of normality test to perform.
#         alpha: The significance level for the test.

#     Returns:
#         A dictionary containing the test statistic and p-value.
#     """
#     from scipy import stats

#     if test == 'JB':
#         stat, p_value = JB_statistic(sample_data)
#     elif test == 'shapiro':
#         stat, p_value = stats.shapiro(sample_data)
#     # elif test == 'jarque_bera':
#     #     stat, p_value = stats.jarque_bera(sample_data)
#     else:
#         raise ValueError("Invalid test type.")
#     return {'statistic': stat, 'p_value': p_value}
