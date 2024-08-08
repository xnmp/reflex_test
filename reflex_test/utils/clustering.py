import pandas as pd
import numpy as np
from scipy.sparse import issparse

from sklearn.preprocessing import LabelBinarizer


def group_means(output, group_col, feature_names=None, top_n=None):

    # groupby and take the mean, which works for sparse matrices and numpy arrays

    # group_means(tfidfs, plotdata['topic'])

    if issparse(output):
        lb = LabelBinarizer(sparse_output=True)
        # groups = group_col.groupby(group_col).groups
        grouped = lb.fit_transform(group_col)

        if lb.y_type_ == 'binary' and lb.classes_.shape[0] == 2:
            grouped = grouped.todense()
            grouped = np.hstack((grouped, 1-grouped))
            grouped = grouped.T.dot(output.todense())
        else:
            grouped = grouped.T.dot(output).todense()

        grouped = (
            pd.DataFrame(grouped, columns=feature_names, index=lb.classes_)
            .divide(group_col.value_counts().sort_index().values, axis=0)
        )

    else:
        grouped = pd.DataFrame(output, index=group_col, columns=feature_names).groupby(group_col.name).mean()

    # return grouped.apply(lambda x: x.nlargest(5).index.tolist(), axis=1)

    res = (grouped
        .unstack().reset_index()
        .set_axis(['word','group','value'], axis=1)
        .sort_values(['group','value'], ascending=[True, False])
    )

    if top_n is not None:
        top_res = (res
            .groupby('group', as_index=False)
            .apply(lambda x: x.iloc[:top_n])
            .reset_index(drop=True)
            # .assign(word_n=lambda x: x.groupby(['topic']).cumcount() + 1)
            # .set_index(['word_n','topic'])
            # .unstack('word_n')
        )

        return top_res

    return res


def get_cluster_names(df, top_n=5, cluster_col='cluster', tfidf=None, text_col=None):

    tfidfs0 = tfidf.transform(df[text_col])
    top_tfidfs = group_means(tfidfs0, 
                                df[cluster_col], 
                                feature_names=tfidf.get_feature_names_out(), 
                                top_n=top_n)
    top_tfidfs = top_tfidfs.set_index(['group','word'])['value']
    res = top_tfidfs.reset_index().groupby('group')['word'].agg(list)
    return res.apply('_'.join).reset_index().set_axis([cluster_col, f'{cluster_col}_name'], axis='columns')


def add_cluster_names(df, *args, **kwargs):
    # need to preserve the order of df, otherwise when the text visualizer takes the first 5000 they'll all be the same cluster
    # can merge like the below but it is slower
    # df = df.reset_index().merge(self.get_cluster_names(df)).sort_values('index').drop(columns='index')
    cluster_names = get_cluster_names(df, *args, **kwargs)
    cluster_names = {rec['cluster']: rec['cluster_name'] for rec in cluster_names.to_records()}
    df['cluster_name'] = df['cluster'].apply(cluster_names.get)
    return df

