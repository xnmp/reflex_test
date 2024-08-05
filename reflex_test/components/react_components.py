import reflex as rx
from typing import List, Dict, Any

class MultiSelect(rx.Component):
    library = "react-select"
    tag = "MultiSelect"
    is_default = True
    options: rx.Var[List[Dict[str, Any]]]
    on_change: rx.EventHandler[lambda args: [args]]
    is_multi: rx.Var[bool] = False
    value: rx.Var[dict]
    placeholder: rx.Var[str]
    # style: rx.Var[Dict[str, Any]]  # Add this line
#     # is_disabled: rx.Var[bool] = False
#     # is_clearable: rx.Var[bool] = True
#     # is_searchable: rx.Var[bool] = True


# need: 
# DateRangePicker for date cols - https://hypeserver.github.io/react-date-range/
# Slider for num cols 
# TextInput for text cols - https://www.npmjs.com/package/react-tagsinput or react-tag-input-component
# try ag grid: https://www.npmjs.com/package/ag-grid-react


class DateRange(rx.Component):
    library = "react-date-range"
    tag = "DateRange"  # or "DateRangePicker" depending on which component you want to use
    ranges: rx.Var[Dict[str, Any]]
    onChange: rx.EventHandler
    months: rx.Var[int] = 2
    direction: rx.Var[str] = "horizontal"


class TagInput(rx.Component):
    library = "react-tagsinput"
    tag = "TagsInput"
    value: rx.Var[List[str]]
    onChange: rx.EventHandler
    addKeys: rx.Var[List[str]] = ["Enter", "Tab"]
    removeKeys: rx.Var[List[str]] = ["Backspace"]


class AgGrid(rx.Component):
    library = "ag-grid-react"
    tag = "AgGridReact"
    columnDefs: rx.Var[List[Dict[str, Any]]]
    rowData: rx.Var[List[Dict[str, Any]]]

