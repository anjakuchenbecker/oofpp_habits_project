import json
import sys
import shelve
import os

import click
from prettytable import PrettyTable

import app_config as conf
import analytics


def get_json_out(raw_text):
    """Convert input raw text and return JSON."""
    return json.dumps(raw_text, indent=4, sort_keys=False)


def get_human_out(raw_text):
    """Convert input raw text and return human readable format (table style)."""
    human_text = PrettyTable(["id", "name", "longest streak"])
    human_text.add_row([raw_text["id"], raw_text["name"], raw_text["longest_streak"]])
    return human_text


@click.command(short_help="Return the longest streak for the given habit")
@click.option("-h", "--habit-id", type=str, required=True, help="Id of habit that has to be "
                                                                "analyzed for longest streak.")
@click.option("-o", "--output", required=False, default="JSON",
              type=click.Choice(["JSON", "HUMAN"], case_sensitive=True), help="Output format. Default JSON.")
def cli(habit_id, output):
    """Return the longest streak for the given habit."""
    try:
        # Open habits database
        habits_db = shelve.open(os.path.join(conf.data_dir, conf.db_name))
        # Load habits
        habits = [habit for habit in habits_db.items()]
        # Close habits database
        habits_db.close()
        # Retrieve longest streak
        if habit_id == "None":
            raise KeyError()
        else:
            if any(habit[0] == habit_id for habit in habits):
                longest_streak = analytics.get_longest_streak_for_habit(habits, habit_id)
                habit_name = list(habit[1].name for habit in habits if habit[1].id == habit_id)[0]
                return_value = {"id": habit_id, "name": habit_name, "longest_streak": longest_streak}
            else:
                raise KeyError()
        # Return longest streak
        if output == "JSON":
            click.echo(get_json_out(return_value))
        else:
            click.echo(get_human_out(return_value))
    except KeyError as e:
        # Inform user: Return error if given id is invalid and exit application
        click.secho("################# ERROR #################", bg="red", fg="white", bold=True)
        click.secho("! An error occurred !", bg="red", fg="white", bold=True)
        click.secho(f"{type(e).__name__}: Given id {habit_id} is invalid", bg="red", fg="white", bold=True)
        click.secho("########################################", bg="red", fg="white", bold=True)
        sys.exit(1)
    except ValueError as e:
        # Inform user: Return error if unexpected error occurred and exit application
        click.secho("################# ERROR #################", bg="red", fg="white", bold=True)
        click.secho("! An error occurred !", bg="red", fg="white", bold=True)
        click.secho(f"{type(e).__name__}: {e}", bg="red", fg="white", bold=True)
        click.secho("########################################", bg="red", fg="white", bold=True)
        sys.exit(1)
    except Exception as e:
        # Inform user: Return error if unexpected error occurred and exit application
        click.secho("################# ERROR #################", bg="red", fg="white", bold=True)
        click.secho("! An unexpected error occurred !", bg="red", fg="white", bold=True)
        click.secho(f"{type(e).__name__}: {e}", bg="red", fg="white", bold=True)
        click.secho("########################################", bg="red", fg="white", bold=True)
        sys.exit(1)