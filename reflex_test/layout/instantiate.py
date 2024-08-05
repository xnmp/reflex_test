
from ..components.filters import Dropdown, Filters
from ..data_model.load_data import load_data, num_cols, date_col, cat_cols
from ..core.sqlite import SQLTable

table = SQLTable('data/test.db')

df = load_data()




options_dict ={
    'flavor': [
        {"value": "chocolate", "label": "Chocolate"},
        {"value": "strawberry", "label": "Strawberry"},
        {"value": "vanilla", "label": "Vanilla"}
    ],
    'color': [
        {"value": "green", "label": "Green"},
        {"value": "red", "label": "Red"},
        {"value": "blue", "label": "Blue"}
    ]
}


options_dict = {
    col: [
        {
            'value': val,
            'label': val
        } for val in df[col].unique()
    ]
    for col in cat_cols
}


# need: 
# DateRangePicker for date cols - https://hypeserver.github.io/react-date-range/
# Slider for num cols 
# TextInput for text cols - https://www.npmjs.com/package/react-tagsinput or react-tag-input-component


# dropdowns = {name: Dropdown(name, options=options) for name, options in options_dict.items()}

dropdowns = {name: Dropdown(name, options=options) for name, options in options_dict.items()}

filters = Filters('filters', filter_objs=dropdowns.values(), table=table)

