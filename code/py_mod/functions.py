

def quarter_start_value(date):
    """
    Takes a date and returns the beginning-of-quarter date

    Parameters
    ----------
    date

    Returns
    -------

    """
    return date.to_period("Q").start_time.normalize()


def quarter_start(dates):
    """
    Vectorized wrapping for 'quarter_start_value'

    Parameters
    ----------
    dates: Array-like of dates

    Returns
    -------

    """
    if dates.size == 1:
        return quarter_start_value(dates)
    else:
        return dates.apply(quarter_start_value)


def quarter_end_value(date):
    """
    Takes a date and returns the beginning-of-quarter date

    Parameters
    ----------
    date

    Returns
    -------

    """
    return date.to_period("Q").end_time.normalize()


def quarter_end(dates):
    """
    Vectorized wrapping for 'quarter_end_value'

    Parameters
    ----------
    dates: Array-like of dates

    Returns
    -------

    """
    if dates.size == 1:
        return quarter_end_value(dates)
    else:
        return dates.apply(quarter_end_value)