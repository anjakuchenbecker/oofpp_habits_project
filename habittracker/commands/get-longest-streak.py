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
    human_text = PrettyTable(["longest streak"])
    human_text.add_row([raw_text["longest_streak"]])
    return human_text


@click.command(short_help="Return the longest streak of all currently tracked habits")
@click.option("-o", "--output", required=False, default="JSON",
              type=click.Choice(["JSON", "HUMAN"], case_sensitive=True), help="Output format. Default JSON.")
def cli(output):
    """Return the longest streak of all currently tracked habits."""
    try:
        # Open habits database
        habits_db = shelve.open(os.path.join(conf.data_dir, conf.db_name))
        # Load habits
        habits = [habit for habit in habits_db.items()]
        # Close habits database
        habits_db.close()
        # Retrieve longest streak
        longest_streak = analytics.get_longest_streak(habits)
        return_value = {"longest_streak": longest_streak}
        # Return longest streak
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
