# utils.py
from datetime import datetime

def get_timestamp(years_to_add=0, end_of_year=False):
    """
    Returns the current timestamp in ISO 8601 format in UTC.
    Optionally adds a number of years to the current timestamp.
    If end_of_year is True, sets the time to the end of that year.

    :param years_to_add: Optional number of years to add to the current date. Defaults to 0.
    :param end_of_year: If True, return the last moment of the current or future year. Defaults to False.
    :return: A string representing the timestamp in ISO 8601 format.
    """
    # Current time in UTC
    current_time = datetime.utcnow()

    # Add the specified number of years
    future_time = current_time.replace(year=current_time.year + years_to_add)

    # Set to the last moment of that year if end_of_year is True
    if end_of_year:
        future_time = future_time.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

    return future_time.isoformat() + "Z"
