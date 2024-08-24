"""Creates GUI contents, layouts, and dependencies."""

from typing import Dict, Any
import datetime

from bokeh.models.widgets.tables import NumberFormatter
import pandas as pd
import panel as pn

from data_manager import DataManager, Expense

# Turn on notifications
pn.extension(notifications=True)

# Load CSS formatting file
with open("CSS/gui_bootstrap.css") as f:
    pn.config.raw_css.append(f.read())


class GUI:
    def __init__(self) -> None:
        self.data_manager = DataManager()
        self.template = pn.template.BootstrapTemplate(
            title=f"Finance Pro: {self.data_manager.username}",
        )

        self.components = self.__create_components()
        self.__create_watchers()
        self.__create_layout()

    def go_to_login_page(self, event):
        """Called when returning to the login page."""

        # Check if unsaved data was present
        if event.obj.name == "Yes":
            # User chose to save data
            self.data_manager.save_data()
        elif event.obj.name == "No":
            # User chose not to save data
            self.data_manager.revert_data()

        self.components["logout"]["prompt"].visible = False

    def logout_btn_clk(self, _event):
        """Called when the "Logout" button is clicked."""

        print(type(self.components["data"]["add"]["time"].value))

        # Check if user has unsaved expenses
        if len(self.data_manager.new_user_data.expenses) > 0:
            self.components["data"]["tabulator"].visible = False
            # Text of prompt is updated with number of unsaved expenses
            self.components["logout"][
                "text"
            ].object = f"""## You have {len(self.data_manager.new_user_data.expenses)} unsaved expenses. Would you like to keep them?"""
            # Forces re-render
            self.components["logout"]["text"].param.trigger("object")
            self.components["logout"]["prompt"].visible = True

    def __create_components(self) -> Dict[str, Any]:
        """Returns all components present in the GUI."""

        def __create_data_components() -> Dict[str, Any]:
            """Contains functions that create widgets associated with the add, search, and manage data tabs."""

            def __create_add_expense() -> Dict[str, Any]:
                """Widgets for adding a new expense."""
                input_expense_amount = pn.widgets.FloatInput(
                    name="Amount",
                    placeholder="Required",
                    start=0.00,
                    step=1,
                )
                input_expense_name = pn.widgets.AutocompleteInput(
                    name="Name",
                    case_sensitive=False,
                    restrict=False,
                    placeholder="Required",
                )
                input_expense_category = pn.widgets.TextInput(
                    name="Category", placeholder="Required"
                )
                input_expense_tags = pn.widgets.MultiChoice(name="Tags")
                input_expense_date_time = pn.widgets.DatetimePicker(
                    name="Date/Time", enable_seconds=False, military_time=False
                )
                input_expense_description = pn.widgets.TextAreaInput(
                    name="Description",
                    placeholder="Optional",
                    height=300,
                    resizable="height",
                )
                input_expense_notes = pn.widgets.TextAreaInput(
                    name="Notes", placeholder="Optional", height=100, resizable="height"
                )
                btn_add_expense = pn.widgets.Button(name="Add Expense")

                return {
                    "amount": input_expense_amount,
                    "name": input_expense_name,
                    "category": input_expense_category,
                    "tags": input_expense_tags,
                    "time": input_expense_date_time,
                    "description": input_expense_description,
                    "notes": input_expense_notes,
                    "button": btn_add_expense,
                }

            def __create_search_expense() -> Dict[str, Any]:
                """Widgets for deleting an expense."""

                options = ["Name", "Category", "Tag(s)", "Location", "Description"]
                delete_search_options = pn.widgets.CheckBoxGroup(
                    options=options, value=options
                )
                input_delete_keyword = pn.widgets.TextInput(
                    placeholder="Enter keyword..."
                )
                input_date_time_range = pn.widgets.DatetimeRangePicker(
                    name="Date/Time", enable_seconds=False, military_time=False
                )

                return {
                    "options": delete_search_options,
                    "keyword": input_delete_keyword,
                    "time": input_date_time_range,
                }

            def __create_manage_data() -> Dict[str, Any]:
                """Widgets for managing data."""

                save_btn = pn.widgets.Button(name="Save newly added data")

                return {"save": save_btn}

            def __create_tabulator() -> pn.widgets.Tabulator:
                """Widgets associated with the tabulator."""

                tabulator_formats = {"float": NumberFormatter(format="$0.00")}

                # Extract all data fields
                names = [
                    expense.name
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                amounts = [
                    expense.amount
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                categories = [
                    expense.category
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                tags = [
                    expense.tags if expense.tags else set()
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                date = [
                    (
                        [
                            expense.date_time.year,
                            expense.date_time.month,
                            expense.date_time.day,
                        ]
                        if expense.date_time
                        else [None, None, None]
                    )
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                time = [
                    (
                        [
                            expense.date_time.hour,
                            expense.date_time.minute,
                            expense.date_time.second,
                        ]
                        if expense.date_time
                        else [None, None, None]
                    )
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                description = [
                    expense.description if expense.description else ""
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                notes = [
                    expense.notes if expense.notes else ""
                    for expense in self.data_manager.combined_user_data.expenses
                ]

                df = pd.DataFrame(
                    {
                        "Name": names,
                        "Amount": amounts,
                        "Category": categories,
                        "Tags": tags,
                        "Date": date,
                        "Time": time,
                        "Description": description,
                        "Notes": notes,
                    }
                )
                tabulator = pn.widgets.Tabulator(
                    df,
                    formatters=tabulator_formats,
                    theme="bootstrap",
                    layout="fit_data",
                )

                return tabulator

            return {
                "add": __create_add_expense(),
                "search": __create_search_expense(),
                "manage": __create_manage_data(),
                "tabulator": __create_tabulator(),
            }

        # END: create_data_components()

        def __create_visual_components():
            """Contains functions that create components associated with visualizing data."""
            return None

        # END: create_visual_components()

        def __create_logout_components():
            """Widgets associated with logging in and out."""
            logout_btn = pn.widgets.Button(name="Logout")

            # Buttons to chose whether or not to keep unsaved data
            save_btn = pn.widgets.Button(name="Yes")
            do_not_save_btn = pn.widgets.Button(name="No")
            logout_text = pn.pane.Markdown(
                f"""## You have {len(self.data_manager.new_user_data.expenses)} unsaved expenses. Would you like to keep them?"""
            )
            # Logout prompt column
            logout_prompt = pn.Column(
                logout_text,
                save_btn,
                do_not_save_btn,
                visible=False,
            )

            return {
                "logout_btn": logout_btn,
                "text": logout_text,
                "prompt": logout_prompt,
                "save_data": save_btn,
                "do_not_save_data": do_not_save_btn,
            }

        return {
            "logout": __create_logout_components(),
            "data": __create_data_components(),
            "visual": __create_visual_components(),
        }

    def __create_watchers(self):
        """Function that defines widget dependencies."""

        def __create_logout_watchers():
            """Defines dependencies and behaviors for widgets associated with logging in and out."""

            self.components["logout"]["logout_btn"].on_click(self.logout_btn_clk)
            self.components["logout"]["save_data"].on_click(self.go_to_login_page)
            self.components["logout"]["do_not_save_data"].on_click(
                self.go_to_login_page
            )

        def __create_add_expense_watchers():
            """Defines dependencies and behaviors for widgets under the "add" tab."""

            def add_expense_btn_clk(event):
                """Writes expense data fields to user memory.
                Called when the add expense button is clicked."""

                # Check for required fields
                # TODO: Currently doesn't work
                missing_fields = []
                if self.components["data"]["add"]["amount"].value == None:
                    missing_fields.append("Amount")
                if self.components["data"]["add"]["name"].value in ["", None]:
                    missing_fields.append("Name")
                if self.components["data"]["add"]["category"].value in ["", None]:
                    missing_fields.append("Category")
                if missing_fields:
                    # Missing field is present
                    pn.state.notifications.error(
                        "Missing fields: " + ", ".join(missing_fields)
                    )
                    # Don't save current expense
                    return

                expense_data = Expense(
                    amount=self.components["data"]["add"]["amount"].value,
                    name=self.components["data"]["add"]["name"].value,
                    category=self.components["data"]["add"]["category"].value,
                    tags=self.components["data"]["add"]["tags"].value,
                    date_time=self.components["data"]["add"]["time"].value,
                    description=self.components["data"]["add"]["description"].value,
                    notes=self.components["data"]["add"]["notes"].value,
                )

                # Add expense to user memory
                self.data_manager.add_expense(expense_data)

                self.components["data"]["add"]["amount"].value = 0
                self.components["data"]["add"]["name"].value = ""
                self.components["data"]["add"]["category"].value = ""
                self.components["data"]["add"]["tags"].value = []
                self.components["data"]["add"]["time"].value = None
                self.components["data"]["add"]["description"].value = ""
                self.components["data"]["add"]["notes"].value = ""

                # TODO: Update tabulator
                # self.components["data"]["tabulator"]

            # === Create watchers === #
            self.components["data"]["add"]["button"].on_click(add_expense_btn_clk)

        def __create_manage_data_watchers():
            """Defines dependencies and behavior for widgets under the "manage" tab."""

            # Save data button f
            self.components["data"]["manage"]["save"].on_click(
                lambda _event: self.data_manager.save_data()
            )
            pn.state.notifications.success("Successfully saved new expenses to memory!")

        __create_logout_watchers()
        __create_add_expense_watchers()
        __create_manage_data_watchers()

    def __create_layout(self):
        """Creates the GUI layout."""

        def __create_data_layouts():
            """Creates layout of data managing components."""

            # BEGIN: Functions that generate widgets for each tab in sidebar

            def __create_add_data_layout():
                """Creates the layout of the "add expense" tab."""
                return pn.Column(*self.components["data"]["add"].values())

            def __create_search_data_layout():
                """Creates the layout of the "search" tab."""
                return pn.Column(*self.components["data"]["search"].values())

            def __create_manage_data_layout():
                """Creates the layout for the "manage" tab."""
                return pn.Column(*self.components["data"]["manage"].values())

            # END: sidebar tab widget layouts

            return pn.Tabs(
                ("Add", __create_add_data_layout()),
                ("Search", __create_search_data_layout()),
                ("Manage", __create_manage_data_layout()),
            )

        # Header
        self.template.header.append(self.components["logout"]["logout_btn"])

        # Sidebar
        sidebar_tabs = pn.Tabs(("Data", __create_data_layouts()), ("View", None))
        self.template.sidebar.append(sidebar_tabs)

        # Main
        self.template.main.append(self.components["data"]["tabulator"])
        self.template.main.append(self.components["logout"]["prompt"])

    def serve_layout(self):
        """Function that is accessed by pn.serve()."""
        return self.template


def main():
    my_gui = GUI()
    pn.serve(my_gui.serve_layout)


if __name__ == "__main__":
    main()
