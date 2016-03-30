__author__ = 'Riley Flynn (nint8835)'


def days_to_hours(days):
    return days * 24


def hours_to_minutes(hours):
    return hours * 60


def minutes_to_seconds(minutes):
    return minutes * 60


def days_to_minutes(days):
    return hours_to_minutes(days_to_hours(days))


def days_to_seconds(days):
    return minutes_to_seconds(days_to_minutes(days))


def hours_to_seconds(hours):
    return minutes_to_seconds(hours_to_minutes(hours))
