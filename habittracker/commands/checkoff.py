import json
import sys
import shelve
import os

import click
from prettytable import PrettyTable

import app_config as conf


def get_json_out(raw_text):
    """Convert input raw text and return JSON."""
    return json.dumps(raw_text, indent=4, sort_keys=False)


def get_human_out(raw_text):
    """Convert input raw text and return human readable format (table style)."""
    human_text = PrettyTable(["id", "name", "description", "periodicity", "created", "checkoffs"])
    human_text.add_row([raw_text["id"], raw_text["name"], raw_text["description"], raw_text["periodicity"], raw_text["created"],
                        "\n".join(raw_text["checkoffs"])])
    return human_text


@click.command(short_help="Check off given habit")
@click.option("-h", "--habit-id", required=True, type=str, help="Id of habit that has to be checked off.")
@click.option("-t", "--timestamp", required=True, type=str, help="Check off timestamp, format YYYY-MM-DD HH:MM:SS.f")
@click.option("-o", "--output", required=False, default="JSON",
              type=click.Choice(["JSON", "HUMAN"], case_sensitive=True), help="Output format. Default JSON.")
def cli(habit_id, timestamp, output):
    """Checks off a given habit."""
    # Check off given habit with given timestamp and save habit to database and return as json
    try:
        # Open habits database
        habits_db = shelve.open(os.path.join(conf.data_dir, conf.db_name))
        # Load habit
        habit = habits_db[habit_id]
        # Check off habit
        habit.check_off(timestamp)
        # Update habit
        habits_db[habit.id] = habit
        # Close habits database
        habits_db.close()
        # Return habit
        if output == "JSON":
            click.echo(get_json_out(habit.to_custom_dict()))
        else:
            click.echo(get_human_out(habit.to_custom_dict()))
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
