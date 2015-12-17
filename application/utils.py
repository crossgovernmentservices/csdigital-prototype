def a_year_from_now():
    a_year_from_now = datetime.timedelta(weeks=52)
    now = datetime.datetime.utcnow()
    return now + a_year_from_now
