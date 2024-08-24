import os
import platform
import logging
import re
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
    date_time: datetime.datetime | None = (
        None  # TODO: Leaving DatetimePicker GUI widget empty results in GUI Tabulator trying to access non-existing .year, .month, etc. values
    )
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
        Directory for financepro AppData.
    user_app_data_dir
        Directory for AppData of current user.
    user_data_file
        Path to the JSON data file of the current user.
    boot_user_data
        Dictionary of all user expenses at the time of login.
    boot_user_config
        User configuration at the time of login.
    new_user_data
        UserData object containing all new data inputted since last save.
    combined_user_data
        UserData object containing data from boot up and data created during current execution.

    """

    def __init__(self, username="guest"):
        """Initializes data management object.

        Parameters
        ----------
        username
            username of current user.

        """

        self.username = username

        # Find file path of user data based on OS and return True if it already exists
        user_AppData_folder_exists = self.set_AppData_path()

        # Create new blank logging file
        with open(self.user_logging_file, "w"):
            pass
        logging.basicConfig(filename=self.user_logging_file, level=logging.INFO)

        # AppData folder for specified username does not exist
        if not user_AppData_folder_exists:
            # User data folder not found - create it
            self.create_new_user()

        # Load data from files
        self.load_data()
        # Represents all new data for this session
        self.new_user_data = UserData()

    def set_AppData_path(self) -> bool:
        """Function that sets the AppData path to save/load user data from.
        Returns True if the user already exists and returns False if
        the user AppData directory cannot be found. Called on sign in."""

        # Determine AppData path based on OS
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
            self.app_data_dir = os.path.join(os.getenv("AppData"), "financepro")
        else:
            raise NotImplementedError(f"Unsupported operating system: {os_type}")

        # User data directory
        self.user_app_data_dir = os.path.join(self.app_data_dir, self.username)
        # User data file
        self.user_data_file = os.path.join(self.user_app_data_dir, "data.json")
        # User configuration file
        self.user_config_file = os.path.join(self.user_app_data_dir, "config.json")
        # User logging file
        self.user_logging_file = os.path.join(
            self.user_app_data_dir, "data_manager.log"
        )

        if not os.path.isdir(self.user_app_data_dir):
            # User AppData folder does not exist
            try:
                os.makedirs(self.user_app_data_dir)
            except FileExistsError:
                # Directory was created between the time of checking if it exists and making it (edge case)
                logger.warning(
                    f"Directory {self.user_app_data_dir} already existed on bootup."
                )
                if os.path.isfile(self.user_data_file):
                    # Data file already exists - don't call create new user function
                    logger.warning(
                        f"Data file found after unexpected existing directory on boot up. Not creating a new user."
                    )
                    return True

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
            try:
                self.boot_user_data = msgspec.json.decode(file_contents, type=UserData)
            except msgspec.ValidationError as e:
                # Convert error message to string and identify what caused it
                message = str(e)

                # Matches the field causing the error
                match = re.search(r"at '\$\.(.+?)'", message).group(1)
                if match:
                    logger.exception(f"Value at {match} appears to be an invalid type.")
                else:
                    # Could not find match
                    logger.exception(f"Unable to find what field caused this error.")

                # TODO: Remove or modify invalid field so file can be loaded

        # Initialize combined user expenses
        self.combined_user_data = self.boot_user_data

        # Load user configuration file
        with open(self.user_config_file, "rb") as file:
            file_contents = file.read()
            self.boot_user_config = msgspec.json.decode(file_contents, type=UserConfig)
        # Initialize config object that gets updated after boot up
        self.current_user_config = self.boot_user_config
        self.current_user_config.launches += 1

    def save_data(self):
        """Handles saving user data to JSON files."""

        # Write combined_user_data to JSON data file
        # TODO: Expense not being written to JSON file
        with open(self.user_data_file, "wb") as file:
            data = msgspec.json.encode(self.combined_user_data)
            file.write(data)

        # Set new_user_data back to nothing
        self.new_user_data = UserData()

        # Update user config file
        self.current_user_config.data_size = self.get_user_data_size()
        with open(self.user_config_file, "wb") as file:
            data = msgspec.json.encode(self.current_user_config)
            file.write(data)

    def revert_data(self):
        """Reverts data to last save point."""

        # Revert expenses
        self.combined_user_data.expenses = [
            expense
            for expense in self.combined_user_data.expenses
            if expense not in self.new_user_data.expenses
        ]
        # Revert names
        self.combined_user_data.names = [
            name
            for name in self.combined_user_data.names
            if name not in self.new_user_data.names
        ]
        # Revert categories
        self.combined_user_data.categories = [
            category
            for category in self.combined_user_data.categories
            if category not in self.new_user_data.categories
        ]
        # Revert tags
        self.combined_user_data.tags = [
            tag
            for tag in self.combined_user_data.tags
            if tag not in self.new_user_data.tags
        ]

        # Reset new_user_data
        self.new_user_data = UserData()

    def add_expense(self, expense: Expense):
        """Handles adding an expense.

        Parameters
        ----------
        expense
            Expense object containing all expense data.

        """

        # Add name, category, and tags to respective lists if they are not in them already
        self.new_user_data.expenses.append(expense)
        self.combined_user_data.expenses.append(expense)
        if expense.name not in self.combined_user_data.names:
            self.new_user_data.names.add(expense.name)
            self.combined_user_data.names.add(expense.name)
        if expense.category not in self.combined_user_data.categories:
            self.new_user_data.categories.add(expense.category)
            self.combined_user_data.categories.add(expense.category)
        new_tags = set(expense.tags) - self.combined_user_data.tags
        self.new_user_data.tags.update(new_tags)
        self.combined_user_data.tags.update(new_tags)
