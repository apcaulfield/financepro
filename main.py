from typing import Dict, Any

import panel as pn

class GUI:
    def __init__(self) -> None:
        self.template = pn.template.BootstrapTemplate(title="Finance Pro")
        self.components = self.__create_components()

    def __create_components(self) -> Dict[str:Any]:
        """Function that returns all components present in the GUI."""

        def __create_add_data_components(self) -> Dict[str:Any]:
            """Contains functions that create widgets associated with creating new data."""

            def __create_add_expense_name(self) -> Dict[str:Any]:
                """Widgets for adding a new expense name."""

                input_expense_name = pn.widgets.TextInput(
                    name="Name"
                )  # placeholder="expense name",
                input_expense_category = pn.widgets.TextInput(name="Category")
                input_expense_tags = pn.widgets.MultiChoice(
                    name="Default tags", placeholder="Optional"
                )
                input_expense_location = pn.widgets.TextInput(
                    name="Default location", placeholder="Optional"
                )
                input_expense_description = pn.widgets.TextInput(
                    name="Description", placeholder="Optional"
                )

                return {
                    "name": input_expense_name,
                    "category": input_expense_category,
                    "tags": input_expense_tags,
                    "location": input_expense_location,
                    "description": input_expense_description,
                }

            def __create_add_category(self) -> Dict[str:Any]:
                """Widgets for adding a new category of expenses."""

                input_category = pn.widgets.TextInput(name="Category")
                input_tags = pn.widgets.MultiChoice(
                    name="Default tags", placeholder="Optional"
                )

                return {"category": input_category, "tags": input_tags}

            def __create_add_tag(self) -> Dict[str:Any]:
                """Widget for adding a new tag."""

                return pn.widgets.MultiChoice(name="Add tags")

            def __create_add_expense(self) -> Dict[str:Any]:
                """Widgets for adding a new expense."""

                input_expense_amount = pn.widgets.FloatInput(
                    name="Amount",
                    start=0.00,
                    placeholder=0.00,
                    step=1,
                    format="${:,.2f}",
                )
                input_expense_name = pn.widgets.AutocompleteInput(
                    name="Name",
                    case_sensitive=False,
                    restrict=False,
                )  # placeholder="expense name",
                input_expense_category = pn.widgets.TextInput(name="Category")
                input_expense_tags = pn.widgets.MultiChoice(name="Default tags")
                input_expense_date_time = pn.widgets.DateTimePicker(
                    enable_seconds=False, military_time=False
                )
                input_specific_expense_description = pn.widgets.TextInput(
                    name="Description"
                )

                return {
                    "amount": input_expense_amount,
                    "name": input_expense_name,
                    "category": input_expense_category,
                    "tags": input_expense_tags,
                    "time": input_expense_date_time,
                    "description": input_specific_expense_description,
                }

            return {
                "add_name": __create_add_expense_name(),
                "add_category": __create_add_category,
                "add_tag": __create_add_tag,
                "add_expense": __create_add_expense,
            }

        return {
            "add": __create_add_data_components(),
        }

    def create_layout(self):
        pass


def main():
    pass


if __name__ == "__main__":
    main()
