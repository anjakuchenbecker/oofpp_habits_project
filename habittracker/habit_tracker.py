import os
import shelve
import glob
import json
import sys

import click

import app_config as conf
import habit


class MyCLI(click.MultiCommand):
    """Enables "Custom Multi Commands" (click framework)

    Note: get_command extended with error handling in case of unknown command is called.

    For details please refer to https://click.palletsprojects.com/en/7.x/commands/#custom-multi-commands
    """

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(conf.plugin_folder):
            if filename.endswith(".py"):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(conf.plugin_folder, name + ".py")
        if glob.glob(fn):
            with open(fn) as f:
                code = compile(f.read(), fn, "exec")
                eval(code, ns, ns)
            return ns['cli']
        else:
            # Inform user: Return error if command is invalid and exit application
            click.secho("################# ERROR #################", bg="red", fg="white", bold=True)
            click.secho("! Invalid command !", bg="red", fg="white", bold=True)
            click.secho(f"Command {name} is invalid.", bg="red", fg="white", bold=True)
            click.secho("########################################", bg="red", fg="white", bold=True)
            sys.exit(1)


def initialize_database():
    """Initialize database with example habits at first run

    Create and populate habits database with example data if habit database not yet exists:

    - Five examples habits (three on daily and two on weekly basis)

    - Each with tracking data for a period of four or five weeks

    Example data coming from */data/sample_data.json*
    """
    try:
        sample_data_json = os.path.join(conf.data_dir, "sample_data.json")
        # Initialize database if necessary
        if not glob.glob(os.path.join(conf.data_dir, f"{conf.db_name}.dat")):
            if glob.glob(sample_data_json):
                # Read json file with example data
                with open(sample_data_json, encoding="utf-8") as json_file:
                    # Load json file containing example data
                    data = json.load(json_file)
                    # Create habits database
                    habits_db = shelve.open(os.path.join(conf.data_dir, conf.db_name))
                    # Create habit coming from json and save to habit database
                    for item in data["sample_data"]:
                        sample_habit = habit.Habit(item["name"], item["description"], item["periodicity"])
                        for checkoff_date in item["checkoffs"]:
                            sample_habit.check_off(checkoff_date)
                        habits_db[str(sample_habit.id)] = sample_habit
                    # Close habits database
                    habits_db.close()
            else:
                # Inform user: Return error if </data/sample_data.json> does not exist and exit application
                click.secho("################# ERROR #################", bg="red", fg="white", bold=True)
                click.secho("! Failed to initialize database !", bg="red", fg="white", bold=True)
                click.secho("A problem occurred with file <data/sample_data.json>:", bg="red", fg="white", bold=True)
                click.secho(f"- File does not exist", bg="red", fg="white", bold=True)
                click.secho("---------------- SOLUTION ---------------", bg="red", fg="white", bold=True)
                click.secho("1====> Place file to <data/sample_data.json>", bg="red", fg="white", bold=True)
                click.secho("2====> Run *~HaTraBa~* again", bg="red", fg="white", bold=True)
                click.secho("########################################", bg="red", fg="white", bold=True)
                sys.exit(1)

    except json.JSONDecodeError as e:
        # Inform user: Return error if </data/sample_data.json> is invalid and exit application
        click.secho("################# ERROR #################", bg="red", fg="white", bold=True)
        click.secho("! Failed to initialize database !", bg="red", fg="white", bold=True )
        click.secho("A problem occurred with file <data/sample_data.json>:", bg="red", fg="white", bold=True)
        click.secho(f"- Invalid json format: {e}", bg="red", fg="white", bold=True)
        click.secho("---------------- SOLUTION ---------------", bg="red", fg="white", bold=True)
        click.secho("1====> Fix file <data/sample_data.json>", bg="red", fg="white", bold=True)
        click.secho("2====> Run *~HaTraBa~* again", bg="red", fg="white", bold=True)
        click.secho("########################################", bg="red", fg="white", bold=True)
        sys.exit(1)
    except Exception as e:
        # Inform user: Return error if unexpected error occurred and exit application
        click.secho("################# ERROR #################", bg="red", fg="white", bold=True)
        click.secho("! An unexpected error occurred !", bg="red", fg="white", bold=True)
        click.secho(f"{type(e).__name__}: {e}", bg="red", fg="white", bold=True)
        click.secho("########################################", bg="red", fg="white", bold=True)
        sys.exit(1)


def callback(test):
    # Init application conf
    if test:
        conf.db_name = "test_habitdb"
    else:
        conf.db_name = "habitdb"
    # Initialize db if necessary
    initialize_database()


cli = MyCLI(params=[click.Option(("--test",), is_flag=True, default=False, help="Run in test mode")],
            callback=callback,
            help=f"Welcome to *~HaTraBa~* (Version 1.0.0) - a CLI-based habit tracking backend!")

if __name__ == "__main__":
    # Run CLI
    cli()
