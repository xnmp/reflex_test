import reflex as rx
import plotly.express as px
import plotly

from django.utils.functional import cached_property

from ..core.statefulness import Stateful, state, state_var, handler
from ..utils.helpers import maybe_sample


class WordFreqBar(Stateful):
    
    @state
    def fig(self) -> plotly.graph_objects.Figure:
        return plotly.graph_objects.Figure()
    
    @handler
    async def update(self):
        text_series = await self.get_source('data')
        self.fig = self.calculate_fig(text_series)
        
    @property
    def element(self):
        return rx.vstack(rx.plotly(data=self.fig), width='45%', height='40vh', overflow='auto')

    def __init__(self, name='word_freq_bar', 
                 base_series=None, 
                 n_records=25, x_label='prominence', kind='tf', 
                 max_fit=5000, 
                 tf_threshold=None, title_name="default", colored=False):
        self.name = name
        self.n_records = n_records
        self.x_label = x_label
        self.max_fit = max_fit
        self.kind = kind
        if base_series is not None:
            self.update_base(base_series)
        self.tf_threshold = tf_threshold
        self.title_name = title_name
        self.is_colored = colored
    
    @cached_property
    def word_finder(self):
        from ..utils.tfidf_compare import StandoutWordFinder
        return StandoutWordFinder(kind=self.kind)

    def update_base(self, base_series):
        if len(base_series) > self.max_fit:
            base_series = base_series.sample(self.max_fit)
        self.word_finder.fit(base_series)
    
    def get_plotdata(self, text_series):
        word_df = self.word_finder.transform_both(text_series).rename(columns={'zscore':self.x_label})
        return word_df.sort_values(self.x_label)[-self.n_records:]
    
    def calculate_fig(self, text_series):
        text_series = maybe_sample(text_series, nmax=self.max_fit)
        df = self.get_plotdata(text_series)
        x = self.x_label if not self.is_colored else 'count'
        df_sorted = df.sort_values(x)

        kwargs = {}
        color_range = [-1, 2]
        if self.is_colored:
            kwargs['color'] = self.x_label
            kwargs['color_continuous_scale'] = 'RdYlBu_r'
            kwargs['range_color'] = color_range

        res = px.bar(df_sorted, x=x, y='word', orientation='h',
                    width=550, 
                    height=400*self.n_records/15,
                    **kwargs
                )
        
        res.update_layout(
            xaxis_title=x.capitalize(),
            yaxis_title='Word',
            dragmode=False,
            margin=dict(t=20, b=10, l=10, r=10),
            coloraxis_colorbar=dict(
                thickness=15,  # Thickness of the color bar
                len=0.5,  # Length of the color bar as a fraction of the plot height
                yanchor="top",  # Anchor the color bar at the bottom of the plot
                y=0.8,  # Position the color bar 10% from the bottom of the plot
                tickvals= color_range,
                ticktext=['Low', 'High']
            )
        )
        
        return res
