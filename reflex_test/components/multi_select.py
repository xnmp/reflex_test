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
#     # is_disabled: rx.Var[bool] = False
#     # is_clearable: rx.Var[bool] = True
#     # is_searchable: rx.Var[bool] = True


