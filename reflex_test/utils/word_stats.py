import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.colors as colors
import dash_extendable_graph as deg

from django.utils.functional import cached_property
from dash import dcc, html
from dash.dependencies import Output
from wordcloud import WordCloud
from core.dash_object_abc import Callback, DashObject, DataDependentObject, DashGraph
from utils.dash_helpers import go_figure
from utils.helpers import maybe_sample


class DashWordCloud(DashGraph, DataDependentObject):

    def __init__(self, name='wordcloud', height=500, width=500, **kwargs):
        self.name = name
        self.wordcloud = WordCloud(background_color="white", contour_width=0.1, #mask=mask
                    contour_color="black",  max_font_size=150, #random_state=42,
                    colormap="Dark2", width=width, height=height,
                    prefer_horizontal=1,
                    relative_scaling=0.4,
                    )
    
    def generate_wc(self, text_series, *args, **kwargs):
        return self.wordcloud.generate(' '.join(text_series))

    def update(self, text_series, *args, **kwargs):
        text_series = maybe_sample(text_series, nmax=5000)
        wc_image = self.generate_wc(text_series, *args, **kwargs)
        res = go_figure(wc_image, height=self.wordcloud.height, width=self.wordcloud.width)
        return res

    @cached_property
    def element(self):
        return dcc.Graph(self.name, style={'height': '40vh', 'maxHeight': '35vh', 'maxWidth': '35vw', 'overflow': 'auto'})


class DashWordCloudColoured(DashWordCloud):
    
    @staticmethod
    def recolor_wordcloud(wc_img, color_dict, palette=sns.color_palette("coolwarm", as_cmap=True)):
        def color_func(word, font_size, position, orientation, **kwargs):
            return colors.rgb2hex(palette(color_dict[word]))
        wc_img.recolor(color_func=color_func)
        return wc_img
    
    def generate_wc(self, text_series, swf):

        # swf is a fitted StandOutWordFinder

        word_freqs = swf.transform_both(text_series)
        wc_image = self.wordcloud.generate_from_frequencies(
            word_freqs.set_index('word')['count'].to_dict(),
        )

        # recolor
        from utils.helpers import power_normalize
        word_freqs['cmap'] = power_normalize(word_freqs['zscore'])
        color_dict = word_freqs.set_index('word')['cmap'].to_dict()
        wc_image = self.recolor_wordcloud(wc_image, color_dict)

        return wc_image


class WordFreqBar(DashGraph, DataDependentObject):

    input_property = 'clickData'

    @staticmethod
    def remove_bigram_counts(hh: pd.Series):

        # removes count of bigrams from the counts of constituent unigrams

        bigrams = [w for w in hh.index if len(w.split()) > 1]

        for w in hh.index:
            for bigram in bigrams:
                if w in bigram.split():
                    hh.loc[w] -= hh.loc[bigram]
                    # the least it can get to is zero
                    hh.loc[w] = np.maximum(0, hh.loc[w])

        return hh


    def input_value(self, clickData):
        # returns the keyword that was clicked
        if clickData is None:
            return clickData
        return clickData['points'][0]['label'], clickData['button']


    def __init__(self, name='word_freq_bar', 
                 base_series=None, col='case_sumy_x_cleaned', 
                 id_col='CASE_REFN_I', 
                 n_records=25, x_label='prominence', kind='tf', 
                 tf_threshold=None, title_name="default", colored=False):
        self.name = name
        self.n_records = n_records
        self.x_label = x_label
        self.kind = kind
        if base_series is not None:
            self.fit(base_series)
        self.tf_threshold = tf_threshold
        self.title_name = title_name
        self.is_colored = colored
    
    @cached_property
    def element(self):
        return html.Div([
            deg.ExtendableGraph(self.name, style={'height': '40vh', 'maxHeight': '35vh', 'maxWidth': '35vw', 'overflow': 'auto'}), 
            dcc.Store(id=f'{self.name}_dummy'),
            dcc.Store(id=f'{self.name}_has_suppressed_context', data=False),
        ])

    @property
    def title(self):
        return self.title_name
    
    # @session_property
    @cached_property
    def word_finder(self):
        from utils.tfidf_compare import StandoutWordFinder
        return StandoutWordFinder(kind=self.kind)

    def fit(self, text_series):
        print("Fitting...")
        self.word_finder.fit(text_series)
        print('DONE')
    
    @property
    def is_fitted(self):
        return self.word_finder.is_fitted
    
    def get_plotdata(self, text_series):
        word_df = self.word_finder.transform_both(text_series)
        word_df.columns = [word_df.columns[0], 'prominence', word_df.columns[2]]

        if self.tf_threshold is not None:
            word_df = word_df.loc[lambda x: x['tf_count'] <= self.tf_threshold]
        return word_df.sort_values(self.x_label)[-self.n_records:]

    def update(self, text_series):
        text_series = maybe_sample(text_series, nmax=5000)
        df = self.get_plotdata(text_series)

        x = 'prominence' if not self.is_colored else 'count'
        
        df_sorted = df.sort_values(x)

        kwargs = {}
        color_range = [-1, 2]
        if self.is_colored:
            kwargs['color'] = 'prominence'        
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
    
    @Callback(
        outputs=lambda x: Output(f'{x.name}_dummy', 'data'),
        inputs=lambda x: [
            x.deps['ingested_data'].input('data', suffix='initial_trigger'),
        ],
        states=lambda x: x.deps['ingested_data'].state(),
    )
    def update_on_new_base_series(self, is_triggered, new_df):
        if not self.is_fitted:
            self.fit(new_df.sample(2000).drop_duplicates('CASE_REFN_I')['case_sumy_x_cleaned'])
        return {}

    def register_clientside(self, app):
        # suppress the default context menu
        app.clientside_callback(
            'window.suppress_default_context_menu', 
            self.output('data', suffix='has_suppressed_context'),
            self.input('clickData'),
            self.state('id'),
            self.state('data', suffix='has_suppressed_context')
        )
