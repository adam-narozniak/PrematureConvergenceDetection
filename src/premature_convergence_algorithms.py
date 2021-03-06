"""This is our project assignment."""
import logging
import numpy as np

logger = logging.getLogger("PrematureConvergenceDetection")


def naive_stop(data_collector, iteration):
    """
    Naive looking 25 iterations back

    Args:
        data_collector: instance of DataCollector to get collected data from.
        iteration: number of previous iteration
    """
    back_by = 25
    if iteration > back_by and data_collector.best_scores[iteration - back_by] / data_collector.best_scores[
        iteration] < 1.1:
        logger.info("algorithm stuck in local optimum")
        return True
    return False


def naive_stop_cmp(data_collector, variants, iteration):
    """
    Take many variants into account.

    Args:
        data_collector:
        variants: possibilities to check (row look by, column ratio)
    """
    for ratio in variants.columns.values:
        for look_back_by in variants.index.values:
            if variants.loc[look_back_by, ratio] != 0:
                continue
            if iteration > look_back_by and data_collector.best_scores[iteration - look_back_by] / \
                    data_collector.best_scores[iteration] < ratio:
                logger.info(f"algorithm stuck based on criteria ratio: {ratio} and look_back_by{look_back_by}")
                variants.loc[look_back_by, ratio] = iteration


def individual_outside_std(population, data_collector, factor, iteration):
    """
    Classify as futile when there are no individuals outside factor * std. Answers question if we should stop algorithm.
    Args:
        population:
        data_collector:
        factor:
        iteration: number of previous iteration
    Returns:
        True when stuck in optimum
        False when still exploring
    """
    means = data_collector.means[iteration]
    upper_bound = means + factor * data_collector.stds[iteration]
    lower_bound = means - factor * data_collector.stds[iteration]
    greater_than_upper = np.array(upper_bound < population.max(axis=0)).any()
    smaller_than_lower = np.array(lower_bound > population.min(axis=0)).any()
    # check if there are any individuals greater or smaller than factor * std
    if greater_than_upper or smaller_than_lower:
        return False  # there are still exploring individuals
    else:
        logger.info("algorithm stuck in local optimum")
        return True


def stds_below_threshold(population, data_collector, threshold, iteration):
    """When all stds for all features among population are smaller than threshold classify as futile.

    Args:
        iteration(int): current iteration
        threshold(float): value to compare stds with

    """
    current_population_stds = data_collector.stds[iteration]
    if (current_population_stds < threshold).all():
        # alg stuck
        logger.info("algorithm stuck in local optimum")
        return True
    else:
        return False


def stds_cmp(data_collector, variants, iteration):
    """
    Take many variants into account.

    Args:
        data_collector:
        variants: possibilities to check different thresholds
    """
    for th in variants.index.values:
        if variants.loc[th] != 0:
            continue
        if (data_collector.stds[iteration] < th).all():
            logger.info(f"algorithm stuck based on criteria threshold: {th}")
            variants.loc[th] = iteration
