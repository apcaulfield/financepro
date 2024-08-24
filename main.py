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
        self.template = pn.template.BootstrapTemplate(
            title="Finance Pro",
        )

        self.data_manager = DataManager()
        self.components = self.__create_components()
        self.__create_watchers()
        self.__create_layout()

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
                input_specific_expense_description = pn.widgets.TextAreaInput(
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
                    "description": input_specific_expense_description,
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
                    expense.tags
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                date = [
                    [
                        expense.date_time.year,
                        expense.date_time.month,
                        expense.date_time.day,
                    ]
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                time = [
                    [
                        expense.date_time.hour,
                        expense.date_time.minute,
                        expense.date_time.second,
                    ]
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                description = [
                    expense.description
                    for expense in self.data_manager.combined_user_data.expenses
                ]
                notes = [
                    expense.notes
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
            pass

        # END: create_visual_components()

        return {
            "data": __create_data_components(),
            "visual": None,
        }

    def __create_watchers(self):
        """Function that defines widget dependencies."""

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
                if self.components["data"]["add"]["name"].value == None:
                    missing_fields.append("Name")
                if self.components["data"]["add"]["category"].value == None:
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

            def save_data_btn_clk(event):
                self.data_manager.save_data()

            self.components["data"]["manage"]["save"].on_click(save_data_btn_clk)

        __create_add_expense_watchers()
        __create_manage_data_watchers()

    def __create_layout(self):
        def __create_data_layouts():
            """Creates layout of data managing components."""

            def __create_add_data_layout():
                """Creates the layout of the "add expense" tab."""
                return pn.Column(*self.components["data"]["add"].values())

            def __create_search_data_layout():
                """Creates the layout of the "search" tab."""
                return pn.Column(*self.components["data"]["search"].values())

            def __create_manage_data_layout():
                """Creates the layout for the "manage" tab."""
                return pn.Column(*self.components["data"]["manage"].values())

            # END: create_add_x_layout functions

            return pn.Tabs(
                ("Add", __create_add_data_layout()),
                ("Search", __create_search_data_layout()),
                ("Manage", __create_manage_data_layout()),
            )

        # Sidebar
        sidebar_tabs = pn.Tabs(("Data", __create_data_layouts()), ("View", None))
        self.template.sidebar.append(sidebar_tabs)

        # Main
        self.template.main.append(self.components["data"]["tabulator"])

    def serve_layout(self):
        """Function that is accessed by pn.serve()."""
        return self.template


def main():
    my_gui = GUI()
    pn.serve(my_gui.serve_layout)


if __name__ == "__main__":
    main()
