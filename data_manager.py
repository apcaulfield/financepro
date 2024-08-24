import os
import platform
import logging
import json
import datetime
from pathlib import Path
from typing import List

import humanize
import msgspec

logger = logging.getLogger(__name__)


class Expense(msgspec.Struct):
    """Describes data associated with an expense."""

    amount: float
    name: str
    category: str
    tags: set[str] | None = set()
    date_time: datetime.datetime = None
    description: str | None = None
    notes: str | None = None


class UserData(msgspec.Struct):
    """Describes the structure of all user JSON data."""

    expenses: List[Expense] = []
    names: set[str] = set()
    categories: set[str] = set()
    tags: set[str] = set()


class UserConfig(msgspec.Struct):
    """Describes the structure of user config.json files."""

    username: str
    launches: int
    data_size: str


class DataManager:
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
        Dictionary containing all new data inputted since login.
    combined_user_data
        Dictionary containing data from boot up and data created during current execution.

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
        if not self.set_appdata_path():
            # User data folder not found - create it
            self.create_new_user()

        # Load data from files
        self.load_data()
        # Represents all new data for this session
        self.new_user_data = UserData()

    def set_appdata_path(self) -> bool:
        """Function that sets the appdata path to save/load user data from.
        Returns true if the user already exists and returns false if
        the user app data directory cannot be found."""

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
        self.user_data_file = os.path.join(self.user_app_data_dir, "data.json")
        # User configuration file
        self.user_config_file = os.path.join(self.user_app_data_dir, "config.json")

        if not os.path.isdir(self.user_app_data_dir):
            # User app data folder does not exist
            try:
                os.makedirs(self.user_app_data_dir)
            except FileExistsError:
                # TODO: Directory was created between the time of checking if it exists and making it
                pass

            # User does not exist
            return False

        # User does exist
        return True

    def get_user_data_size(self):
        """Function for determining the overall size of the user's data files."""

        # Sum sizes of all files in directory and its subdirectories
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
        with open(self.user_data_file, "wb") as file:
            new_user_data = UserData()
            json_new_user_data = msgspec.json.encode(new_user_data)
            file.write(json_new_user_data)

        # Create new config/info file for user
        with open(self.user_config_file, "wb") as file:
            user_data_size = self.get_user_data_size()
            user_config = UserConfig(
                username=self.username,
                launches=1,
                data_size=user_data_size,
            )
            json_new_user_config = msgspec.json.encode(user_config)
            file.write(json_new_user_config)

    def load_data(self):
        """Loads user data and config from respective files.
        Initializes the boot_user_data, combined_user_data, and boot_user_config attributes.
        """

        # Load user data file
        with open(self.user_data_file, "rb") as file:
            file_contents = file.read()
            self.boot_user_data = msgspec.json.decode(file_contents, type=UserData)
        # Initialize combined user expenses
        self.combined_user_data = self.boot_user_data

        # Load user configuration file
        with open(self.user_config_file, "rb") as file:
            self.boot_user_config = json.load(file)

    def save_data(self):
        """Handles saving user data to JSON files."""
        # TODO
        pass

    def add_expense(self, expense: Expense):
        """Handles adding an expense.

        Parameters
        ----------
        expense
            Expense object containing all expense data.

        """

        # Add name, category, and tags to respective lists if they are not in them already
        self.new_user_data.expenses.append(expense)
        if expense.name not in self.combined_user_data.names:
            self.combined_user_data.names.add(expense.name)
            self.new_user_data.names.add(expense.name)
        if expense.category not in self.combined_user_data.categories:
            self.combined_user_data.categories.add(expense.category)
            self.new_user_data.categories.add(expense.category)
        new_tags = set(expense.tags) - self.combined_user_data.tags
        self.combined_user_data.tags.update(new_tags)
        self.new_user_data.tags.update(new_tags)
