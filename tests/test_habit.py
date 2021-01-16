import os
import json
from datetime import datetime, timezone

import pytest

from habit import Habit


DATA_DIR = os.path.join(os.path.realpath(os.path.pardir), "habittracker", "data")


@pytest.fixture()
def sample_habits():
    sample_data_file_name = os.path.join(DATA_DIR, "sample_data.json")
    if os.path.exists(sample_data_file_name):
        # Read json file with example data
        with open(sample_data_file_name, encoding="utf-8") as json_file:
            # Load json file containing example data
            sample_habits = json.load(json_file)
            return sample_habits["sample_data"]
    else:
        assert False, f"File {sample_data_file_name} doest not exist."


@pytest.fixture()
def habit_object(sample_habits):
    return Habit(name=sample_habits[0]["name"], description=sample_habits[0]["description"],
                 periodicity=sample_habits[0]["periodicity"])


@pytest.mark.unit
@pytest.mark.positive
def test_create_valid_option_all_daily(sample_habits):
    expected_name = sample_habits[0]["name"]
    expected_description = sample_habits[0]["description"]
    expected_periodicity = sample_habits[0]["periodicity"]
    expected_created = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    expected_checkoffs = []
    actual = Habit(name=expected_name, description=expected_description, periodicity=expected_periodicity)
    assert actual.name == expected_name
    assert actual.description == expected_description
    assert actual.periodicity.name == expected_periodicity
    assert actual.checkoffs == expected_checkoffs
    assert str(actual.created[:10]) == str(expected_created)


@pytest.mark.unit
@pytest.mark.positive
def test_create_valid_option_all_weekly(sample_habits):
    expected_name = sample_habits[-1]["name"]
    expected_description = sample_habits[-1]["description"]
    expected_periodicity = sample_habits[-1]["periodicity"]
    expected_created = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    expected_checkoffs = []
    actual = Habit(name=expected_name, description=expected_description, periodicity=expected_periodicity)
    assert actual.name == expected_name
    assert actual.description == expected_description
    assert actual.periodicity.name == expected_periodicity
    assert actual.checkoffs == expected_checkoffs
    assert str(actual.created[:10]) == str(expected_created)


@pytest.mark.unit
@pytest.mark.negative
def test_create_invalid_option_name_missing(sample_habits):
    expected_description = sample_habits[0]["description"]
    expected_periodicity = sample_habits[0]["periodicity"]
    with pytest.raises(TypeError) as exc_info:
        Habit(description=expected_description, periodicity=expected_periodicity)
    expected_error_message = "__init__() missing 1 required positional argument: 'name'"
    assert str(exc_info.value) == expected_error_message


@pytest.mark.unit
@pytest.mark.negative
def test_create_invalid_option_description_missing(sample_habits):
    expected_name = sample_habits[0]["name"]
    expected_periodicity = sample_habits[0]["periodicity"]
    with pytest.raises(TypeError) as exc_info:
        Habit(name=expected_name, periodicity=expected_periodicity)
    expected_error_message = "__init__() missing 1 required positional argument: 'description'"
    assert str(exc_info.value) == expected_error_message


@pytest.mark.unit
@pytest.mark.negative
def test_create_invalid_option_periodicity_missing(sample_habits):
    expected_name = sample_habits[0]["name"]
    expected_description = sample_habits[0]["description"]
    with pytest.raises(TypeError) as exc_info:
        Habit(name=expected_name, description=expected_description)
    expected_error_message = "__init__() missing 1 required positional argument: 'periodicity'"
    assert str(exc_info.value) == expected_error_message


@pytest.mark.unit
@pytest.mark.negative
def test_create_invalid_option_periodicity_invalid(sample_habits):
    expected_name = sample_habits[0]["name"]
    expected_description = sample_habits[0]["description"]
    with pytest.raises(TypeError) as exc_info:
        Habit(name=expected_name, description=expected_description)
    expected_error_message = "__init__() missing 1 required positional argument: 'periodicity'"
    assert str(exc_info.value) == expected_error_message


@pytest.mark.unit
@pytest.mark.positive
def test_checkoff_valid_option_all(habit_object):
    expected_checkoffs_length = 1
    expected_habit_checkoff_timestamp = "2020-12-01 23:59:00.123456"
    habit_object.check_off(expected_habit_checkoff_timestamp)
    actual_habit = habit_object
    actual_last_habit_checkoff_timestamp = str(datetime.strptime(str(actual_habit.checkoffs[-1].timestamp),
                                                                 "%Y-%m-%d %H:%M:%S.%f"))
    assert actual_last_habit_checkoff_timestamp == expected_habit_checkoff_timestamp
    assert len(actual_habit.checkoffs) == expected_checkoffs_length


@pytest.mark.unit
@pytest.mark.negative
def test_checkoff_invalid_option_timestamp_missing(habit_object):
    with pytest.raises(TypeError) as exc_info:
        habit_object.check_off()
    expected_error_message = "check_off() missing 1 required positional argument: 'date'"
    assert str(exc_info.value) == expected_error_message


@pytest.mark.unit
@pytest.mark.negative
def test_checkoff_invalid_option_timestamp_invalid(habit_object):
    invalid_habit_checkoff_timestamp = "2020-12-01"
    with pytest.raises(ValueError) as exc_info:
        habit_object.check_off(invalid_habit_checkoff_timestamp)
    expected_error_message = f"time data '{invalid_habit_checkoff_timestamp}' " \
                             f"does not match format '%Y-%m-%d %H:%M:%S.%f'"
    assert str(exc_info.value) == expected_error_message


@pytest.mark.unit
@pytest.mark.negative
def test_checkoff_invalid_option_timestamp_already_checked_off(habit_object):
    expected_habit_checkoff_timestamp = "2020-12-01 23:59:00.123456"
    with pytest.raises(ValueError) as exc_info:
        habit_object.check_off(expected_habit_checkoff_timestamp)
        habit_object.check_off(expected_habit_checkoff_timestamp)
    expected_error_message = f"Habit has been already checked off at given time {expected_habit_checkoff_timestamp}"
    assert str(exc_info.value) == expected_error_message


@pytest.mark.unit
@pytest.mark.positive
def test_to_custom_dict(habit_object):
    actual = habit_object.to_custom_dict()
    assert type(actual) is dict
    assert list(actual.keys()) == ['id', 'name', 'description', 'periodicity', 'created', 'checkoffs']
    assert actual["id"] == habit_object.id
    assert actual["name"] == habit_object.name
    assert actual["description"] == habit_object.description
    assert actual["periodicity"] == habit_object.periodicity.name
    assert actual["created"] == habit_object.created
    assert actual["checkoffs"] == []
