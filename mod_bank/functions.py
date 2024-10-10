
def quarter_start(date):
    return date.to_period("Q").start_time.normalize()


def quarter_end(date):
    return date.to_period("Q").end_time.normalize()