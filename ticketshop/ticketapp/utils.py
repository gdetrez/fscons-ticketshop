from datetime import date,datetime,timedelta
def daterange(begin, end):
    """
    Returns an iterator of all dates between begin and end (included).
    """
    if isinstance(begin, datetime):
        d = begin.date()
    elif isinstance(begin, date):
        d = begin
    else:
        assert False, "Unknown format for begin"
    if isinstance(end, datetime):
        end = end.date()
    elif isinstance(begin, date):
        pass
    else:
        assert False, "Unknown format for end"
    while d <= end:
        yield d
        d += timedelta( days = 1 )
