"""
Helpers for predicting how many ``adapt_object_mesh`` smoothing iterations to use.

https://github.com/FNNDSC/voxelation-error-datalad/blob/90fd86aa2e1a280cbda6a210c802236e34b76457/5_notebook/taubin_vs_mean_smtherr.ipynb
"""

# TODO RERUN THE MODEL USING A TIGHTER STARTING SURFACE
# modeled MAX_SMTHERR is much smaller than actuals

A = 3.63462484
H = -9.62391412
K = 0.05865665


def predict_aom(current: float, target: float, max_iters: int = 200) -> int:
    # already smooth enough
    if current <= target or current <= MIN_SMTHERR:
        return 0
    # error is beyond our model's domain
    if current > MAX_SMTHERR:
        target -= current
        current = MAX_SMTHERR
    if target < MIN_SMTHERR:
        target = MIN_SMTHERR

    n_smooth_current = predictor_n_smooth(current, max_iters)
    n_smooth_target = predictor_n_smooth(target, max_iters)
    prediction = n_smooth_target - n_smooth_current
    return min(int(prediction), max_iters)


def predictor_smtherr(n_smooth: float, max_smtherr: float) -> float:
    """
    Predicts how smooth a surface will be after the given number of smoothing iterations.
    """
    b = n_smooth - H
    if b == 0:
        return max_smtherr
    return A / b + K


MAX_SMTHERR = predictor_smtherr(0, 10000)
MIN_SMTHERR = K


def predictor_n_smooth(mean_smtherr: float, max_iters: float) -> float:
    """
    Inverse function of ``predictor_smtherr``
    """
    b = mean_smtherr - K
    if b == 0:
        return max_iters
    return A / b + H
