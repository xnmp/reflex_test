from .filters import DropdownComponent, TagInputComponent,  DatePickerComponent
from .outputs import Constellation, DisplayTable
from .word_stats import WordFreqBar
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

dropdowns = {name: DropdownComponent(name, options=options) for name, options in options_dict.items()}
taginput_and = TagInputComponent('tag_and', and_or='AND')
taginput_or = TagInputComponent('tag_or', and_or='OR')
taginput_not = TagInputComponent('tag_not', and_or='NOT')

date_picker_min = DatePickerComponent('date_picker_min', column_name='CASE_RECV_S', gt_or_lt='>=')
date_picker_max = DatePickerComponent('date_picker_max', column_name='CASE_RECV_S', gt_or_lt='<=')

all_filters = list(dropdowns.values()) + [taginput_and, taginput_or, taginput_not, date_picker_min, date_picker_max]

display_table = DisplayTable('display_table', filter_objs=all_filters, table=table)

constellation = Constellation('constellation')
word_freq_bar = WordFreqBar('word_freq_bar', base_series=df['case_sumy_x_cleaned'], source_data=display_table)
# .add_sources(
#     data={'state': display_table, 'transform': lambda x: x._data['case_sumy_x_cleaned']}
# )
