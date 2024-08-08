import numpy as np
import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
# import matplotlib.colors as colors

from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer

from utils.helpers import maybe_sample


class StandoutWordFinder(TransformerMixin):

    # given a series of text, and a "base" series, gives the standout words in the series
    # the idea: get the tfidfs that are very different from the mean tfidf of the base series
    
    def __init__(self, nmax=3000, fit_limit=5000, kind='tfidf'):
        self.means = None
        self.stds = None
        self.kind = kind
        self.fit_limit = fit_limit
        if self.kind == 'tfidf':
            self.transformer = TfidfVectorizer(ngram_range=(1,2), max_features=nmax)#, stop_words='english')
        elif kind == 'tf':
            self.transformer = CountVectorizer(ngram_range=(1,2), max_features=nmax, binary=True)#, stop_words='english')
        else:
            raise ValueError("'Kind' must be one of ('tfidf','tf')")
        # self.nmax = nmax

    def fit(self, base_text_series):

        if not isinstance(base_text_series, pd.Series):
            raise TypeError('Input should be a Pandas series of text')
        
        # if len(base_text_series) > self.nmax:
        #     base_text_series = base_text_series.sample(self.nmax)

        transformed = self.transformer.fit_transform(maybe_sample(base_text_series, self.fit_limit))
        self.means = transformed.mean(axis=0)
        variances = transformed.power(2).mean(axis=0) - np.square(self.means)
        self.stds = np.sqrt(variances)
        return self
    
    @property
    def words(self):
        return self.transformer.get_feature_names_out()
    
    @property
    def is_fitted(self):
        from sklearn.utils.validation import check_is_fitted
        from sklearn.exceptions import NotFittedError
        try:
            check_is_fitted(self.transformer)
        except NotFittedError:
            return False
        return self.means is not None and self.stds is not None

    def transform(self, text_series, z_threshold=None):

        if not isinstance(text_series, pd.Series):
            raise TypeError('Input should be a Pandas series of text')
        
        transformed = self.transformer.transform(text_series)
        means = transformed.mean(axis=0)

        zscores = (means - self.means) / self.stds
        res = pd.Series(np.ravel(zscores), index=self.words).sort_values(ascending=False)

        if z_threshold is not None:
            res = res[np.abs(res) >= z_threshold]

        return res
    
    def transform_tfs(self, text_series):
        # transforms tf only, not tfidf
        if self.kind == 'tfidf':
            vect = CountVectorizer(ngram_range=(1,2), vocabulary=self.words, binary=True)#, stop_words='english')
        else:
            vect = self.transformer
        props = vect.transform(text_series).mean(axis=0)
        res = pd.Series(np.ravel(props), index=self.words).sort_values(ascending=False)
        return res
    
    def transform_both(self, text_series):

        # for the less common words, they basically are where the tfidf_zscore is high but the tf_count is low

        # example usage:
        # sw = StandoutWordFinder(kind='tf')
        # sumys_base = df['case_sumy_x_cleaned']
        # sumys_compare = df.loc[lambda x: x['OUTCOME_0'] == '2 = Monetary remedy', 'case_sumy_x_cleaned']

        # sw.fit(sumys_base)
        # word_freqs = sw.transform_both(sumys_compare)
        
        tfidf_zscores = self.transform(text_series).to_frame().reset_index()
        tfidf_zscores.columns = ['word','zscore']

        tf_counts = self.transform_tfs(text_series).to_frame().reset_index()
        tf_counts.columns = ['word','count']

        return tfidf_zscores.merge(tf_counts)

    
    def test(self, text_series, base_text_series):

        # testing that it gives the same result as standard scaler (standard scaler doesn't work on sparse)
        
        # example usage:
        # df_sample = df.sample(10000)
        # df_200 = df_sample.loc[lambda x: x['OUTCOME_0'] == '2 = Monetary remedy']
        # sw = StandoutWords()
        # sw.test(df_200['case_sumy_x_cleaned'], df_sample['case_sumy_x_cleaned'])

        tfidfs = self.transformer.fit_transform(base_text_series)

        scaler = StandardScaler()
        scaler.fit(tfidfs.toarray())

        self.fit(base_text_series)
        zscores = self.transform(text_series, z_threshold=None).to_frame()

        tfidfs_2 = self.transformer.transform(text_series)
        test_res = scaler.transform(np.asarray(tfidfs_2.mean(axis=0)))

        zscores['test'] = np.ravel(np.sort(test_res))[::-1]

        if np.abs((zscores[0] - zscores['test'])).sum() < 1e-10:
            print('Test passed!')
        else:
            raise ValueError('Test failed.')

