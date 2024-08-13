import os
import platform
import json


class Data:
    """Class for managing user data.

    Attributes
    ----------
    data_file_path
        Path to the JSON data file of the current user.
    data
        Dictionary of all user expenses.

    """

    def __init__(self, user="guest"):
        """Initializes data management object.

        Parameters
        ----------
        user
            name of current user.

        """

        # Find file path of user data based on OS
        self.set_appdata_path(user)

    def set_appdata_path(self, user: str):
        """Function that sets the appdata path to save/load user data from."""

        os_type = platform.system()
        if os_type == "Darwin":  # macOS
            app_data_dir = os.path.join(
                os.path.expanduser("~"),
                "Library",
                "Application Support",
                "financepro",
                user,
            )
        elif os_type == "Linux":  # Linux
            app_data_dir = os.path.join(
                os.path.expanduser("~"), ".local", "share", "financepro", user
            )
        elif os_type == "Windows":  # Windows
            app_data_dir = os.path.join(os.getenv("APPDATA"), "financepro", user)
        else:
            raise NotImplementedError(f"Unsupported operating system: {os_type}")

        self.data_file_path = os.path.join(app_data_dir, "user_data.json")

        # Make folder if it doesn't yet exist
        os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)

        # Check if data file exists
        if not os.path.isfile(self.data_file_path):
            with open(self.data_file_path, "w") as f:
                # Create new data file for user
                json.dump({}, f)

        # Retrieve data from file
        with open(self.data_file_path, "r") as f:
            self.data = json.load(f)
