import json
import sys
import shelve
import os

import click
from prettytable import PrettyTable

import app_config as conf
import habit


def get_json_out(raw_text):
    """Convert input raw text and return JSON."""
    return json.dumps(raw_text, indent=4, sort_keys=False)


def get_human_out(raw_text):
    """Convert input raw text and return human readable format (table style)."""
    human_text = PrettyTable(["id", "name", "description", "periodicity", "created", "checkoffs"])
    human_text.add_row([raw_text["id"], raw_text["name"], raw_text["description"], raw_text["periodicity"], raw_text["created"],
                        "\n".join(raw_text["checkoffs"])])
    return human_text


@click.command(short_help="Create habit with given details")
@click.option("-n", "--name", required=True, type=str, help="Name of habit")
@click.option("-d", "--description", required=True, type=str, help="Description of habit")
@click.option("-p", "--periodicity", required=True,
              type=click.Choice(["DAILY", "WEEKLY"], case_sensitive=True), help="Periodicity of habit")
@click.option("-o", "--output", required=False, default="JSON",
              type=click.Choice(["JSON", "HUMAN"], case_sensitive=True), help="Output format. Default JSON.")
def cli(name, description, periodicity, output):
    """Create habit with given details."""
    # Create habit with given details and save habit to database and return as json
    try:
        # Create habit
        habit_created = habit.Habit(name, description, periodicity)
        # Open habits database
        habits_db = shelve.open(os.path.join(conf.data_dir, conf.db_name))
        # Save habit
        habits_db[habit_created.id] = habit_created
        # Close habits database
        habits_db.close()
        # Return habit
        if output == "JSON":
            click.echo(get_json_out(habit_created.to_custom_dict()))
        else:
            click.echo(get_human_out(habit_created.to_custom_dict()))
    except Exception as e:
        # Inform user: Return error if unexpected error occurred and exit application
        click.secho("################# ERROR #################", bg="red", fg="white", bold=True)
        click.secho("! An unexpected error occurred !", bg="red", fg="white", bold=True)
        click.secho(f"{type(e).__name__}: {e}", bg="red", fg="white", bold=True)
        click.secho("########################################", bg="red", fg="white", bold=True)
        sys.exit(1)
