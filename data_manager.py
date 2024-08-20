import os
import platform
import logging
import json
from pathlib import Path
from typing import Dict, Any
import humanize
import msgspec

logger = logging.getLogger(__name__)


class MasterList(msgspec.Struct):
    """Contains sets of all unique names, categories, and tags."""

    names: set[str] = set()
    categories: set[str] = set()
    tags: set[str] = set()


class Expense(msgspec.Struct):
    """Describes data associated with an expense."""

    amount: float
    name: str
    category: str
    tags: set[str] | None = set()
    date: str | None = None
    time: str | None = None
    description: str | None = None
    notes: str | None = None


class DateTime(msgspec.Struct):
    """Describes data associated with a DatetimePicker Panel widget."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int | None = 0


class Data:
    """Class for managing user data.

    Attributes
    ----------
    app_data_dir
        Directory for financepro app data.
    user_app_data_dir
        Directory for app data of current user.
    user_data_file
        Path to the JSON data file of the current user.
    boot_user_data
        Dictionary of all user expenses at the time of login.
    boot_user_config
        User configuration at the time of login.
    new_user_data
        Dictionary of all new data inputted since login.

    """

    def __init__(self, username="guest"):
        """Initializes data management object.

        Parameters
        ----------
        username
            username of current user.

        """

        self.username = username

        # Find file path of user data based on OS
        if not self.get_appdata_path():
            # User data folder not found - create it
            self.create_new_user()

        # Load data from files
        self.load_data()
        # Represents all new data for this session
        self.new_user_data = {
            "expenses": [],
            "names": [],
            "categories": [],
            "tags": [],
        }

    def get_appdata_path(self):
        """Function that sets the appdata path to save/load user data from."""

        # Determine app data path based on OS
        os_type = platform.system()
        if os_type == "Darwin":  # macOS
            self.app_data_dir = os.path.join(
                os.path.expanduser("~"), "Library", "Application Support", "financepro"
            )
        elif os_type == "Linux":  # Linux
            self.app_data_dir = os.path.join(
                os.path.expanduser("~"), ".local", "share", "financepro"
            )
        elif os_type == "Windows":  # Windows
            self.app_data_dir = os.path.join(os.getenv("APPDATA"), "financepro")
        else:
            raise NotImplementedError(f"Unsupported operating system: {os_type}")

        # User data directory
        self.user_app_data_dir = os.path.join(self.app_data_dir, self.username)
        # User data file
        self.user_data_file = os.path.join(self.user_app_data_dir, "user_data.json")
        # User config file
        self.user_config_file = os.path.join(self.user_app_data_dir, "user_config.json")

        if not os.path.isfile(self.user_data_file):
            # User data does not exist
            try:
                os.makedirs(os.path.dirname(self.user_data_file))
            except FileExistsError:
                # TODO: File actually does exist
                pass

            return False

        # User does exist
        return True

    def get_user_data_size(self):
        """Function for determining the overall size of the user's data files."""

        # Sum sizes of all files in directory recursively
        total_size = sum(
            f.stat().st_size
            for f in Path(self.user_app_data_dir).rglob("*")
            if f.is_file()
        )
        # Convert total file size to human readable format
        return humanize.naturalsize(total_size, binary=True)

    def create_new_user(self):
        """Function that initializes files and data for a new user."""

        # Create new data file for user
        with open(self.user_data_file, "w") as file:
            json.dump({}, file)

        # Create new config/info file for user
        user_data_size = self.get_user_data_size()
        user_config = {
            "username": self.username,
            "launches": 1,
            "data_size": user_data_size,
        }
        with open(
            os.path.join(self.user_app_data_dir, "user_config.json"), "w"
        ) as file:
            json.dump(user_config, file)

    def load_data(self):
        """Loads user data and config from respective files.
        This function initializes the boot_user_data and boot_user_config attributes.
        """

        with open(self.user_data_file, "r") as file:
            self.boot_user_data = json.load(file)
        # Initialize combined data
        self.combined_user_data = self.boot_user_data

        with open(self.user_config_file, "r") as file:
            self.boot_user_config = json.load(file)

    def save_data(self):
        """Handles saving user data to JSON files."""
        pass

    def add_expense(self, expense: Expense):
        """Handles adding an expense.

        Parameters
        ----------
        expense
            Expense object containing all expense data.

        """

        self.new_user_data["expenses"].append(expense)
        self.combined_user_data["expenses"].append(expense)
