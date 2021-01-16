import os
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from habit_tracker import cli


DATA_DIR = os.path.join(os.path.realpath(os.path.pardir), "habittracker", "data")


def remove_test_db_files():
    db_files = ["test_habitdb.bak", "test_habitdb.dat", "test_habitdb.dir"]
    for item in db_files:
        if os.path.exists(os.path.join(DATA_DIR, item)):
            os.remove(os.path.join(DATA_DIR, item))


@pytest.fixture
def habit():
    runner = CliRunner()
    result = runner.invoke(cli, ["--test", "create", "-n", "habitname", "-d", "habitdescription", "-p", "DAILY"])
    return json.loads(result.output)


@pytest.fixture
def habit_checked_off(habit):
    runner = CliRunner()
    runner.invoke(cli, ["--test", "checkoff", "-h", habit["id"], "-t", "2020-12-01 23:59:00.123456"])
    return habit["id"]


@pytest.fixture()
def rename_sample_data_json():
    original_name = os.path.join(DATA_DIR, "sample_data.json")
    manipulated_name = os.path.join(DATA_DIR, "sample_data_.json")
    if os.path.exists(original_name):
        os.rename(original_name, manipulated_name)
        yield
        os.rename(manipulated_name, original_name)
    else:
        assert False, f"File {original_name} doest not exist."


@pytest.fixture()
def make_invalid_sample_data_json():
    original_name = os.path.join(DATA_DIR, "sample_data.json")
    manipulated_name = os.path.join(DATA_DIR, "sample_data_.json")
    if os.path.exists(original_name):
        os.rename(original_name, manipulated_name)
        Path(original_name).touch()
        yield
        os.remove(original_name)
        os.rename(manipulated_name, original_name)
    else:
        assert False, f"File {original_name} doest not exist."


@pytest.fixture()
def get_sample_data_habit_names():
    sample_data_file_name = os.path.join(DATA_DIR, "sample_data.json")
    if os.path.exists(sample_data_file_name):
        habit_names = []
        # Read json file with example data
        with open(sample_data_file_name, encoding="utf-8") as json_file:
            # Load json file containing example data
            data = json.load(json_file)
            for habit in data["sample_data"]:
                habit_names.append(habit["name"])
        return habit_names
    else:
        assert False, f"File {sample_data_file_name} doest not exist."


@pytest.fixture()
def get_sample_data_habit_names_periodicity_daily():
    sample_data_file_name = os.path.join(DATA_DIR, "sample_data.json")
    if os.path.exists(sample_data_file_name):
        habit_names = []
        # Read json file with example data
        with open(sample_data_file_name, encoding="utf-8") as json_file:
            # Load json file containing example data
            data = json.load(json_file)
            for habit in data["sample_data"]:
                if habit["periodicity"] == "DAILY":
                    habit_names.append(habit["name"])
        return habit_names
    else:
        assert False, f"File {sample_data_file_name} doest not exist."


@pytest.fixture()
def get_sample_data_habit_names_periodicity_weekly():
    sample_data_file_name = os.path.join(DATA_DIR, "sample_data.json")
    if os.path.exists(sample_data_file_name):
        habit_names = []
        # Read json file with example data
        with open(sample_data_file_name, encoding="utf-8") as json_file:
            # Load json file containing example data
            data = json.load(json_file)
            for habit in data["sample_data"]:
                if habit["periodicity"] == "WEEKLY":
                    habit_names.append(habit["name"])
        return habit_names
    else:
        assert False, f"File {sample_data_file_name} doest not exist."


class TestBasic:
    @pytest.mark.functionality
    @pytest.mark.negative
    def test_cli_unknown_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "update"])
        assert "ERROR" in result.output
        assert "Invalid command" in result.output
        assert result.exit_code == 1

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_initialize_database_no_database_and_no_sample_data_json(self, rename_sample_data_json):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "--help"])
        assert "ERROR" in result.output
        assert "Failed to initialize database" in result.output
        assert result.exit_code == 1

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_initialize_database_no_database_and_invalid_sample_data_json(self, make_invalid_sample_data_json):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "--help"])
        assert "ERROR" in result.output
        assert "Failed to initialize database" in result.output
        assert result.exit_code == 1


class TestCommandCreate:

    # noinspection PyMethodMayBeStatic
    def setup_method(self):
        remove_test_db_files()

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        remove_test_db_files()

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_create_in_cli_valid_option_all_daily(self):
        habit_name = "habitname"
        habit_description = "habitdescription"
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "-n", habit_name,
                                     "-d", habit_description, "-p", periodicity])
        data = json.loads(result.output)
        assert data["name"] == habit_name
        assert data["description"] == habit_description
        assert data["periodicity"] == periodicity
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_create_in_cli_valid_option_all_weekly(self):
        habit_name = "habitname"
        habit_description = "habitdescription"
        periodicity = "WEEKLY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "-n", habit_name,
                                     "-d", habit_description, "-p", periodicity])
        data = json.loads(result.output)
        assert data["name"] == habit_name
        assert data["description"] == habit_description
        assert data["periodicity"] == periodicity
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_create_in_cli_invalid_option_name_missing(self):
        habit_description = "habitdescription"
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "-d", habit_description, "-p", periodicity])
        assert "Error" in result.output
        assert "Missing option" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_create_in_cli_invalid_option_name_with_blanks_but_wo_quotation_marks(self):
        habit_name = "habitname"
        habit_description = "habitdescription"
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "-n", habit_name, habit_name,
                                     "-d", habit_description, "-p", periodicity])
        assert "Error" in result.output
        assert "Got unexpected extra argument" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_create_in_cli_invalid_option_description_missing(self):
        habit_name = "habitname"
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "-n", habit_name, "-p", periodicity])
        assert "Error" in result.output
        assert "Missing option" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_create_in_cli_invalid_option_description_with_blanks_but_wo_quotation_marks(self):
        habit_name = "habitname"
        habit_description = "habitdescription"
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "-n", habit_name,
                                     "-d", habit_description, habit_description, "-p", periodicity])
        assert "Error" in result.output
        assert "Got unexpected extra argument" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_create_in_cli_invalid_option_periodicity_missing(self):
        habit_name = "habitname"
        habit_description = "habitdescription"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "-n", habit_name, "-d", habit_description])
        assert "Error" in result.output
        assert "Missing option" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_create_in_cli_invalid_option_periodicity_invalid(self):
        habit_name = "habitname"
        habit_description = "habitdescription"
        periodicity = "DAILYY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "create", "-n", habit_name,
                                     "-d", habit_description, "-p", periodicity])
        assert "Error" in result.output
        assert "Invalid value" in result.output
        assert result.exit_code == 2


class TestCommandCheckoff:

    # noinspection PyMethodMayBeStatic
    def setup_method(self):
        remove_test_db_files()

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        remove_test_db_files()

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_checkoff_in_cli_valid_option_all(self, habit):
        habit_id = habit["id"]
        habit_timestamp = "2020-12-01 23:59:00.123456"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "checkoff", "-h", habit_id,  "-t", habit_timestamp])
        data = json.loads(result.output)
        assert len(habit["checkoffs"])+1 == len(data["checkoffs"])
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_checkoff_in_cli_invalid_option_habit_id_missing(self):
        habit_timestamp = "2020-12-01 23:59:00.123456"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "checkoff", "-t", habit_timestamp])
        assert "Error" in result.output
        assert "Missing option" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_checkoff_in_cli_invalid_option_habit_id_invalid(self):
        habit_id = "42"
        habit_timestamp = "2020-12-01 23:59:00.123456"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "checkoff", "-h", habit_id, "-t", habit_timestamp])
        assert "KeyError" in result.output
        assert f"{habit_id}" in result.output
        assert result.exit_code == 1

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_checkoff_in_cli_invalid_option_timestamp_missing(self, habit):
        habit_id = habit["id"]
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "checkoff", "-h", habit_id])
        assert "Error" in result.output
        assert "Missing option" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_checkoff_in_cli_invalid_option_timestamp_invalid(self, habit):
        habit_id = habit["id"]
        habit_timestamp = "2020-12-01"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "checkoff", "-h", habit_id, "-t", habit_timestamp])
        assert "ValueError" in result.output
        assert f"{habit_timestamp}" in result.output
        assert result.exit_code == 1

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_checkoff_in_cli_valid_option_timestamp_already_checked_off(self, habit_checked_off):
        habit_id = habit_checked_off
        habit_timestamp = "2020-12-01 23:59:00.123456"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "checkoff", "-h", habit_id, "-t", habit_timestamp])
        assert "ValueError" in result.output
        assert f"{habit_timestamp}" in result.output
        assert result.exit_code == 1


class TestCommandDelete:

    # noinspection PyMethodMayBeStatic
    def setup_method(self):
        remove_test_db_files()

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        remove_test_db_files()

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_delete_in_cli_valid_option_all(self, habit):
        habit_id = habit["id"]
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "delete", "-h", habit_id])
        data = json.loads(result.output)
        assert data["id"] == habit_id
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_delete_in_cli_invalid_option_habit_id_missing(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "delete"])
        assert "Error" in result.output
        assert "Missing option" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_delete_in_cli_invalid_option_habit_id_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "delete", "-h"])
        assert "Error" in result.output
        assert "option requires an argument" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_delete_in_cli_invalid_option_habit_id_invalid(self):
        habit_id = "42"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "delete", "-h", habit_id])
        assert "KeyError" in result.output
        assert f"{habit_id}" in result.output
        assert result.exit_code == 1


class TestCommandListHabits:

    # noinspection PyMethodMayBeStatic
    def setup_method(self):
        remove_test_db_files()

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        remove_test_db_files()

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_list_habits_in_cli_valid_option_no_limit(self, get_sample_data_habit_names):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits"])
        data = json.loads(result.output)
        for habit in data:
            assert habit["name"] in get_sample_data_habit_names
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_list_habits_in_cli_valid_option_with_limit(self, get_sample_data_habit_names):
        limit = min([*range(1, len(get_sample_data_habit_names)+1)], default=0)
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits", "-l", limit])
        data = json.loads(result.output)
        assert len(data) == limit
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_list_habits_in_cli_invalid_option_limit_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits", "-l"])
        assert "Error" in result.output
        assert "option requires an argument" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_list_habits_in_cli_invalid_option_limit_negative(self):
        limit = -1
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits", "-l", limit])
        assert "ValueError" in result.output
        assert f"{limit}" in result.output
        assert result.exit_code == 1

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_list_habits_in_cli_invalid_option_limit_string(self):
        runner = CliRunner()
        string = "limit"
        result = runner.invoke(cli, ["--test", "list-habits", "-l", string])
        assert "Error" in result.output
        assert "Invalid value" in result.output
        assert result.exit_code == 2


class TestCommandListHabitByPeriodicity:

    # noinspection PyMethodMayBeStatic
    def setup_method(self):
        remove_test_db_files()

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        remove_test_db_files()

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_list_habits_by_periodicity_in_cli_valid_option_daily_no_limit(
            self, get_sample_data_habit_names_periodicity_daily):
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits-by-periodicity", "-p", periodicity])
        data = json.loads(result.output)
        for habit in data:
            assert habit["name"] in get_sample_data_habit_names_periodicity_daily
            assert habit["periodicity"] == periodicity
        assert len(get_sample_data_habit_names_periodicity_daily) == len(data)
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_list_habits_by_periodicity_in_cli_valid_option_daily_with_limit(
            self, get_sample_data_habit_names_periodicity_daily):
        limit = min([*range(1, len(get_sample_data_habit_names_periodicity_daily) + 1)], default=0)
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits-by-periodicity", "-p", periodicity, "-l", limit])
        data = json.loads(result.output)
        for habit in data:
            assert habit["periodicity"] == periodicity
        assert len(data) == limit
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_list_habits_by_periodicity_in_cli_valid_option_weekly_no_limit(self):
        periodicity = "WEEKLY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits-by-periodicity", "-p", periodicity])
        data = json.loads(result.output)
        for habit in data:
            assert habit["periodicity"] == periodicity
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_list_habits_by_periodicity_in_cli_valid_option_weekly_with_limit(
            self, get_sample_data_habit_names_periodicity_weekly):
        periodicity = "WEEKLY"
        runner = CliRunner()
        limit = min([*range(1, len(get_sample_data_habit_names_periodicity_weekly) + 1)], default=0)
        result = runner.invoke(cli, ["--test", "list-habits-by-periodicity", "-p", periodicity, "-l", limit])
        data = json.loads(result.output)
        for habit in data:
            assert habit["periodicity"] == periodicity
        assert len(data) == limit
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_list_habits_by_periodicity_in_cli_invalid_option_periodicity_invalid(self):
        periodicity = "DAILYY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits-by-periodicity", "-p", periodicity])
        assert "Error" in result.output
        assert "Invalid value" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_list_habits_by_periodicity_in_cli_invalid_option_limit_empty(self):
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits-by-periodicity", "-p", periodicity, "-l"])
        assert "Error" in result.output
        assert "option requires an argument" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_list_habits_by_periodicity_in_cli_invalid_option_limit_negative(self):
        limit = -1
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits-by-periodicity", "-p", periodicity, "-l", limit])
        assert "ValueError" in result.output
        assert f"{limit}" in result.output
        assert result.exit_code == 1

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_list_habits_by_periodicity_in_cli_invalid_option_limit_string(self):
        limit = "limit"
        periodicity = "DAILY"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "list-habits-by-periodicity", "-p", periodicity, "-l", limit])
        assert "Error" in result.output
        assert "Invalid value" in result.output
        assert result.exit_code == 2


class TestCommandGetLongestStreak:

    # noinspection PyMethodMayBeStatic
    def setup_method(self):
        remove_test_db_files()

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        remove_test_db_files()

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_get_longest_streak_in_cli_valid(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "get-longest-streak"])
        data = json.loads(result.output)
        assert data["longest_streak"] >= 0
        assert result.exit_code == 0


class TestCommandGetLongestStreakForHabit:

    # noinspection PyMethodMayBeStatic
    def setup_method(self):
        remove_test_db_files()

    # noinspection PyMethodMayBeStatic
    def teardown_method(self):
        remove_test_db_files()

    @pytest.mark.functionality
    @pytest.mark.positive
    def test_get_longest_streak_for_habit_in_cli_valid_with_habit_id(self, habit):
        habit_id = habit["id"]
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "get-longest-streak-for-habit", "-h", habit_id])
        data = json.loads(result.output)
        assert data["longest_streak"] == 0
        assert result.exit_code == 0

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_get_longest_streak_for_habit_in_cli_invalid_option_habit_id_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "get-longest-streak-for-habit", "-h"])
        assert "Error" in result.output
        assert "option requires an argument" in result.output
        assert result.exit_code == 2

    @pytest.mark.functionality
    @pytest.mark.negative
    def test_get_longest_streak_for_habit_in_cli_invalid_option_habit_id_invalid(self):
        habit_id = "42"
        runner = CliRunner()
        result = runner.invoke(cli, ["--test", "get-longest-streak-for-habit", "-h", habit_id])
        assert "KeyError" in result.output
        assert f"{habit_id}" in result.output
        assert result.exit_code == 1
