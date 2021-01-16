from enum import Enum
from datetime import datetime, timezone
import uuid


class Habit:
    """A class to represent a habit.

    Attributes
    ----------
    id : str
        Unique identifier of the habit.
    name : str
        Name of the habit.
    description : str
        Description of the habit.
    periodicity : Periodicity
        Periodicity of the habit.
    created : str
        Creation timestamp of the habit.
    checkoffs : list of Checkoffs
        List of all check offs.

    Methods
    -------
    checkoff(date):
        Mark the habit as completed (checked-off).

    to_custom_dict():
        Return dictionary representation of habit.

    """
    class Periodicity(Enum):
        """A class to represent a periodicity.
        """
        DAILY = 1, "Daily basis"
        WEEKLY = 2, "Weekly basis"

    def __init__(self, name, description, periodicity):
        """Constructs all the necessary attributes for the habit object.

        Parameters
        ----------
        name : str
            Name of the habit.
        description : str
            Description of the habit.
        periodicity : Periodicity
            Periodicity of the habit.
        """
        self.id = uuid.uuid4().hex
        self.name = name
        self.description = description
        self.periodicity = self.Periodicity[periodicity.upper()]
        self.created = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
        self.checkoffs = []

    def check_off(self, date):
        """ Mark the habit as completed (checked-off).

        Parameters
        ----------
        date : str
            Completion timestamp (format "%Y-%m-%d %H:%M:%S.%f").

        Returns
        -------
        Checkoff
            Checkoff object containing the completion timestamp.

        Raises
        ------
        ValueError
            If habit has been already checked off at given timestamp or date does not match format.
        """
        date_formatted = str(datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f"))
        if date_formatted in list(checkoff.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f") for checkoff in self.checkoffs):
            raise ValueError(f"Habit has been already checked off at given time {date_formatted}")
        self.checkoffs.append(Checkoff(self, date))
        return self.checkoffs[-1]

    def to_custom_dict(self):
        """Return dictionary representation of habit.

        Returns
        -------
        dict
            Dictionary containing all currently stored habit details.
        """
        # Build custom representation
        checkoffs = []
        for checkoff in self.checkoffs:
            checkoffs.append(checkoff.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"))
        custom_dict = {"id": self.id,
                       "name": self.name,
                       "description": self.description,
                       "periodicity": self.periodicity.name,
                       "created": self.created,
                       "checkoffs": checkoffs
                       }
        return custom_dict


class Checkoff:
    """A class to represent the completion (checked-off) of a habit.

        Attributes
        ----------
        habit : Habit
            Habit object.
        date : str
            Completion timestamp (format "%Y-%m-%d %H:%M:%S.%f").
    """
    def __init__(self, habit, date):
        """Constructs all the necessary attributes for the checkoff object.

        Parameters
        ----------
        habit : Habit
            Habit object.
        date : str
            Completion timestamp (format "%Y-%m-%d %H:%M:%S.%f").

        """
        self.habit = habit
        self.timestamp = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
