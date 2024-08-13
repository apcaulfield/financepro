"""Creates GUI contents, layouts, and dependencies."""

from typing import Dict, Any

import panel as pn

# Load CSS formatting file
with open("CSS/gui_bootstrap.css") as f:
    pn.config.raw_css.append(f.read())


class GUI:
    def __init__(self) -> None:
        """Initializes the GUI class object."""

        self.template = pn.template.BootstrapTemplate(
            title="Finance Pro",
        )

        self.components = self.__create_components()
        self.__create_layout()

    def __create_components(self) -> Dict[str, Any]:
        """Function that returns all components present in the GUI."""

        def __create_data_components() -> Dict[str, Any]:
            """Contains functions that create widgets associated with managing data."""

            def __create_add_expense() -> Dict[str, Any]:
                """Widgets for adding a new expense."""
                input_expense_amount = pn.widgets.FloatInput(
                    name="Amount",
                    start=0.00,
                    placeholder="0.00",
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

                return {
                    "amount": input_expense_amount,
                    "name": input_expense_name,
                    "category": input_expense_category,
                    "tags": input_expense_tags,
                    "time": input_expense_date_time,
                    "description": input_specific_expense_description,
                }

            def __create_delete_expense():
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

            return {
                "add": __create_add_expense(),
                "delete": __create_delete_expense(),
            }

        return {
            "data": __create_data_components(),
        }

    def __create_layout(self):
        def __create_data_layouts():
            """Creates layout of data managing components."""

            def __create_add_data_layout():
                """Creates the layout of the "add expense" tab."""
                return pn.Column(*self.components["data"]["add"].values())

            def __create_delete_data_layout():
                """Creates the layout of the "add category" tab."""
                return pn.Column(*self.components["data"]["delete"].values())

            # END: create_add_x_layout functions

            return pn.Tabs(
                ("Add", __create_add_data_layout()),
                ("Delete", __create_delete_data_layout()),
            )

        sidebar_tabs = pn.Tabs(("Data", __create_data_layouts()), ("View", None))
        self.template.sidebar.append(sidebar_tabs)

    def serve_layout(self):
        """Function that is accessed by pn.serve()."""
        return self.template


def main():
    my_gui = GUI()
    pn.serve(my_gui.serve_layout)


if __name__ == "__main__":
    main()
