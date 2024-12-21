

def quarter_start_value(date):
    return date.to_period("Q").start_time.normalize()


def quarter_start(dates):
    if dates.size == 1:
        return quarter_start_value(dates)
    else:
        return dates.apply(quarter_start_value)


def quarter_end_value(date):
    return date.to_period("Q").end_time.normalize()


def quarter_end(dates):
    if dates.size == 1:
        return quarter_end_value(dates)
    else:
        return dates.apply(quarter_end_value)