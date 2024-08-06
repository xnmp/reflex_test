import datetime as dt
import reflex as rx
from typing import List, Dict, Any, Callable

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
    ranges: rx.Var[List[Dict[str, Any]]]
    onChange: rx.EventHandler[lambda args: [args]]
    months: rx.Var[int] = 2
    direction: rx.Var[str] = "horizontal"


class DatePicker(rx.Component):
    library = 'antd'
    tag = 'DatePicker'
    onChange: rx.EventHandler[lambda args: [args]]
    value: rx.Var[Any]
    format: rx.Var[Any] #= 'YYYY-MM-DD'
    allowClear: rx.Var[bool] = True
    minDate: rx.Var[Any]
    maxDate: rx.Var[Any]


class TagInput(rx.Component):
    library = "react-tagsinput"
    tag = "TagsInput"
    value: rx.Var[List[str]]
    onChange: rx.EventHandler[lambda args: [args]]
    is_default = True
    onlyUnique: rx.Var[bool] = True
    addKeys: rx.Var[List[str]] = ["Enter", "Tab"]
    removeKeys: rx.Var[List[str]] = ["Backspace"]
    inputProps: rx.Var[Dict[str, Any]]
    pasteSplit: rx.Var[Any] #Callable[[str], List[str]] = lambda x: list(map(str.strip, x.split(',')))


class AgGrid(rx.Component):
    library = "ag-grid-react"
    tag = "AgGridReact"
    columnDefs: rx.Var[List[Dict[str, Any]]]
    rowData: rx.Var[List[Dict[str, Any]]]

