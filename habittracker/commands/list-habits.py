import json
import shelve
import sys
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
    human_text = PrettyTable(["id", "name", "description", "periodicity", "created", "checkoffs"])
    for item in raw_text:
        human_text.add_row([item["id"], item["name"], item["description"], item["periodicity"], item["created"],
                            "\n".join(item["checkoffs"])])
    return human_text


@click.command(short_help="Return a list of all currently tracked habits")
@click.option("-l", "--limit", default=0, type=int,
              help="A limit on the number of objects to be returned, must be positive. Default is no limit.")
@click.option("-o", "--output", required=False, default="JSON",
              type=click.Choice(["JSON", "HUMAN"], case_sensitive=True), help="Output format. Default JSON.")
def cli(limit, output):
    """Return a list of all currently tracked habits.

    The habits are returned sorted by creation date, with the most recently created habit appearing first.
    """
    try:
        # Open habits database
        habits_db = shelve.open(os.path.join(conf.data_dir, conf.db_name))
        # Load habits
        habits = [habit for habit in habits_db.items()]
        # Close habits database
        habits_db.close()
        # Analyze
        habit_list = analytics.list_habits(habits)
        # Return habit
        return_value = []
        for item in habit_list:
            return_value.append(item[1].to_custom_dict())
        # Reverse order, that the most recently created habit appearing first
        return_value = sorted(return_value, key=lambda k: k["created"], reverse=True)

        # Apply limit if given
        if limit > 0:
            if output == "JSON":
                click.echo(get_json_out(return_value[:limit]))
            else:
                click.echo(get_human_out(return_value[:limit]))
        elif limit < 0:
            raise ValueError(f"A negative limit (given {limit}) is not permitted")
        else:
            if output == "JSON":
                click.echo(get_json_out(return_value))
            else:
                click.echo(get_human_out(return_value))
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
