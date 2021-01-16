import os
import json

import pytest

from habit import Habit
import analytics


DATA_DIR = os.path.join(os.path.realpath(os.path.pardir), "habittracker", "data")


@pytest.fixture()
def sample_habits_objects():
    sample_data_file_name = os.path.join(DATA_DIR, "sample_data.json")
    if os.path.exists(sample_data_file_name):
        # Read json file with example data
        with open(sample_data_file_name, encoding="utf-8") as json_file:
            # Load json file containing example data
            sample_habits = json.load(json_file)
            # Create habit coming from json and save to habit database
            sample_habits_objects = list()
            for item in sample_habits["sample_data"]:
                habit = Habit(item["name"], item["description"], item["periodicity"])
                for checkoff_date in item["checkoffs"]:
                    habit.check_off(checkoff_date)
                sample_habits_objects.append((habit.id, habit))
            return sample_habits_objects
    else:
        assert False, f"File {sample_data_file_name} doest not exist."


class TestListHabits:
    @pytest.mark.unit
    @pytest.mark.positive
    def test_list_habits_valid_option_all(self, sample_habits_objects):
        expected_list_length = len(sample_habits_objects)
        expected_habit_names = [habit[1].name for habit in sample_habits_objects]
        actual = analytics.list_habits(sample_habits_objects)
        actual_habit_names = [habit[1].name for habit in actual]
        assert sorted(actual_habit_names) == sorted(expected_habit_names)
        assert len(actual) == expected_list_length

    @pytest.mark.unit
    @pytest.mark.negative
    def test_list_habits_invalid_option_habits_missing(self):
        with pytest.raises(TypeError) as exc_info:
            analytics.list_habits()
        expected_error_message = "list_habits() missing 1 required positional argument: 'habits'"
        assert str(exc_info.value) == expected_error_message


class TestListHabitsByPeriodicity:
    @pytest.mark.unit
    @pytest.mark.positive
    @pytest.mark.parametrize("expected_periodicity", ["DAILY", "WEEKLY"])
    def test_list_habits_by_periodicity_valid_option_all(self, sample_habits_objects, expected_periodicity):
        expected_habit_names = [habit[1].name for habit in sample_habits_objects
                                if habit[1].periodicity.name == expected_periodicity]
        expected_list_length = len(expected_habit_names)
        actual = analytics.list_habits_by_periodicity(sample_habits_objects, expected_periodicity)
        actual_habit_names = [habit[1].name for habit in actual]
        assert sorted(actual_habit_names) == sorted(expected_habit_names)
        assert len(actual) == expected_list_length

    @pytest.mark.unit
    @pytest.mark.negative
    @pytest.mark.parametrize("expected_periodicity", ["DAILY", "WEEKLY"])
    def test_list_habits_by_periodicity_invalid_option_habits_missing(self, expected_periodicity):
        with pytest.raises(TypeError) as exc_info:
            analytics.list_habits_by_periodicity(periodicity=expected_periodicity)
        expected_error_message = "list_habits_by_periodicity() missing 1 required positional argument: 'habits'"
        assert str(exc_info.value) == expected_error_message

    @pytest.mark.unit
    @pytest.mark.negative
    def test_list_habits_by_periodicity_invalid_option_periodicity_missing(self, sample_habits_objects):
        with pytest.raises(TypeError) as exc_info:
            analytics.list_habits_by_periodicity(habits=sample_habits_objects)
        expected_error_message = "list_habits_by_periodicity() missing 1 required positional argument: 'periodicity'"
        assert str(exc_info.value) == expected_error_message


class TestGetLongestStreak:
    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_longest_streak_valid_option_all(self, sample_habits_objects):
        expected_longest_streak = 11
        actual = analytics.get_longest_streak(sample_habits_objects)
        assert actual == expected_longest_streak

    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_longest_streak_valid_option_all_empty_habits(self):
        expected_longest_streak = 0
        actual = analytics.get_longest_streak(habits=[])
        assert actual == expected_longest_streak


class TestGetLongestStreakForHabit:
    @pytest.mark.unit
    @pytest.mark.positive
    @pytest.mark.parametrize("expected_longest_streaks", [["Meditating", 5],
                                                          ["Workout", 4],
                                                          ["Drink 2 liter of water", 11],
                                                          ["Didn't watch TV", 1],
                                                          ["No spend", 1]])
    def test_get_longest_streak_for_habit_valid_option_all(self, sample_habits_objects, expected_longest_streaks):
        habit_id = [habit[1].id for habit in sample_habits_objects if habit[1].name == expected_longest_streaks[0]]
        actual = analytics.get_longest_streak_for_habit(sample_habits_objects, habit_id[0])
        assert actual == expected_longest_streaks[1]

    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_longest_streak_for_habit_invalid_option_habit_id_not_in_objects(self, sample_habits_objects):
        expected_longest_streak = 0
        actual = analytics.get_longest_streak_for_habit(habits=sample_habits_objects, habit_id="42")
        assert actual == expected_longest_streak

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_longest_streak_for_habit_invalid_option_habits_missing(self):
        with pytest.raises(TypeError) as exc_info:
            analytics.get_longest_streak_for_habit(habit_id="42")
        expected_error_message = "get_longest_streak_for_habit() missing 1 required positional argument: 'habits'"
        assert str(exc_info.value) == expected_error_message

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_longest_streak_for_habit_invalid_option_habit_id_missing(self, sample_habits_objects):
        with pytest.raises(TypeError) as exc_info:
            analytics.get_longest_streak_for_habit(habits=sample_habits_objects)
        expected_error_message = "get_longest_streak_for_habit() missing 1 required positional argument: 'habit_id'"
        assert str(exc_info.value) == expected_error_message
