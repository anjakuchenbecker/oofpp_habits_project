from itertools import groupby
from datetime import datetime
from functools import reduce


def __convert_dates_to_proleptic_gregorian_ordinal(dates):
    """Convert given dates to proleptic gregorian ordinal values.

    Parameters
    ----------
    dates : list of datetime
        List of datetime objects.

    Returns
    -------
    list(int)
        List of integers representing dates as proleptic gregorian ordinal values
    """
    return [datetime.strptime(d, "%Y-%m-%d").toordinal() for d in dates]


def __check_for_consecutive_dates(ordinal_dates):
    """Check if given ordinal dates are consecutive.

    Create tuples (x, y): (x: ith ordinal date, y:ith ordinal date + 1) through all given ordinal
    dates and subtract y from x.

    * Consecutive dates are indicated by a result equal to 1 (*e.g. 737761 - 737760 = 1*)

    * Non-consecutive dates are indicated by a result greater than 1 (*e.g. 737765 - 737760 = 5*)

    Parameters
    ----------
    ordinal_dates : list of int
        List of integer values.

   Returns
    -------
    list of integers
        List of integer values indicating consecutive dates (1) or non-consecutive dates (>1).
    """
    # Sort dates (ascending)
    sorted_ordinal_dates = sorted(ordinal_dates)
    return [y - x for x, y in zip(sorted_ordinal_dates, sorted_ordinal_dates[1:])]


def __sum_consecutive_dates(consecutive_dates_list):
    """Sum up all consecutive dates (indicated by 1) "in a row".

    Example
    Given is list *[1, 1, 1, 1, 2, 1, 3, 1, 1, 1]*.

    First bunch of dates "in a row" are items 1-4:
    sum is 4, but as five dates are initially involved to create this sequence of ones we add 1 --> 5.

    Second bunch of dates "in a row" is item 6:
    sum is 1, but as two dates are initially involved to create this sequence of ones we add 1 --> 2.

    Third bunch of dates "in a row" are items 8-10:
    sum is 3, but as four dates are initially involved to create this sequence of ones we add 1 --> 4.

    Returned is *[5, 2, 4]*

    Parameters
    ----------
    consecutive_dates_list : list of int
        List of integer values, where consecutive dates must indicated by 1.

    Returns
    -------
    list of integers
        List of integer values
    """
    return [(sum(1 for x in group) + 1) for x, group in groupby(consecutive_dates_list) if x == 1]


def __get_max_value(value_list):
    """Determine the largest of the input values.

    Parameters
    ----------
    value_list : list of int
        List of integer values.

    Returns
    -------
    int
        Max value.
    """
    return reduce(lambda a, b: a if a > b else b, value_list, 0)


def __calculate_longest_streak(timestamps):
    """Calculate the longest streak of given timestamps.

    Parameters
    ----------
    timestamps : list of datetime
        List of datetime objects.

    Returns
    -------
    int
        Longest streak value.
    """
    if any(timestamps):
        # Step 1 - Convert given dates to proleptic gregorian ordinal values
        result = list(map(__convert_dates_to_proleptic_gregorian_ordinal, timestamps))
        # Step 2 - Check if given ordinal dates are consecutive
        result = list(map(__check_for_consecutive_dates, result))
        # Step 3 - Sum up all consecutive dates (indicated by 1) "in a row"
        result = list(map(__sum_consecutive_dates, result))
        if any(result):
            # Step 5 - return max value for each list
            result = list(map(__get_max_value, result))
            # Step 6 - return max value
            return __get_max_value(result)
        return 1  # no consecutive timestamps, so longest streak is 1
    return 0  # no checkoff timestamps have been found, so longest streak is 0


def list_habits(habits):
    """Return all habits (1:1, no filtering).

    Parameters
    ----------
    habits : list of Habit
        List of habits.

    Returns
    -------
    list
        List of habits (1:1).
    """
    return list(filter(lambda habit: True, habits))


def list_habits_by_periodicity(habits, periodicity):
    """Return filtered habit list according to given periodicity.

    Parameters
    ----------
    habits : list of Habit
        List of habits.
    periodicity : Periodicity
        Periodicity of the habit.

    Returns
    -------
    list
        List containing habits according to given periodicity or
        empty list in case of no matches.
    """
    return list(filter(lambda habit: habit[1].periodicity.name == periodicity, habits))


def get_longest_streak(habits):
    """Determine the longest run streak from list of habits.

    Parameters
    ----------
    habits : list of (habit_id, Habit)
        List of habits.

    Returns
    -------
    int
        Longest streak value.
    """
    # Determine all checkoff timestamps from given habits
    checkoff_timestamps = [[(checkoff.timestamp.strftime("%Y-%m-%d")) for checkoff in habit[1].checkoffs]
                           for habit in habits]

    return __calculate_longest_streak(checkoff_timestamps)


def get_longest_streak_for_habit(habits, habit_id):
    """Determine the longest run streak of a specific habit from list of habits.

    Parameters
    ----------
    habits : list of (habit_id, habit)
        List of habits.
    habit_id : str
        Id of habit.

    Returns
    -------
    int
        Longest streak value.
    """
    # Determine checkoff timestamps for given habit id from given habits
    checkoff_timestamps = [[(checkoff.timestamp.strftime("%Y-%m-%d")) for checkoff in habit[1].checkoffs]
                           for habit in habits if str(habit[1].id) == str(habit_id)]

    return __calculate_longest_streak(checkoff_timestamps)
