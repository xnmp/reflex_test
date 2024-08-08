
def maybe_sample(series, nmax=None):
    if nmax < len(series):
        series = series.sample(nmax)
    return series
