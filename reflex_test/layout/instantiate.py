
from ..components.filters import Dropdown, Filters, TagInputComponent, DateRangeComponent, DatePickerComponent
from ..data_model.load_data import load_data, num_cols, date_col, cat_cols
from ..core.sqlite import SQLTable

table = SQLTable('data/test.db')

df = load_data()




options_dict = {
    col: [
        {
            'value': val,
            'label': val
        } for val in df[col].unique()
    ]
    for col in cat_cols
}


dropdowns = {name: Dropdown(name, options=options) for name, options in options_dict.items()}

filters = Filters('filters', filter_objs=dropdowns.values(), table=table)

taginput = TagInputComponent('tag')

date_picker = DatePickerComponent('date_picker')
