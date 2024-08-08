from copy import copy
import numpy as np
import plotly.express as px

from utils.clustering import group_means

def make_constellation(plotdata, hover_cols=['cluster_name','root_cause_hover','CASE_SUMY_X_hover'], 
              x='embed_x', y='embed_y', color_col='color',
              text_col='CASE_SUMY_X_cleaned', cluster_col='cluster',
              tfidf=None,
              width=800, height=800):

    plotdata = copy(plotdata)

    for col in hover_cols:
        plotdata[f'{col}_hover'] = plotdata[col].fillna('').str.wrap(65).apply(lambda x: x.replace('\n', '<br>'))
    hover_cols = [f'{col}_hover' for col in hover_cols]

    fig = px.scatter(
        plotdata, width=width, height=height, 
        x=x, y=y, color=color_col,
        size_max=16, 
        color_continuous_scale='turbo', 
        hover_data=hover_cols,
        opacity=0.7
    )

    # hide the color bar
    fig.update_coloraxes(showscale=False)

    hovertemplate = ['<b><span style="text-decoration:underline;">'
                        + col.replace('_hover','').replace('_',' ').title()
                        + f'</span></b>: %{{customdata[{i}]}}' 
                        for i, col in enumerate(hover_cols)]

    hovertemplate = '<br><br>'.join(hovertemplate)
    fig.update_traces(hovertemplate=hovertemplate)

    fig.update_layout(
        dragmode='select',
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
    )

    fig = annotate_graph(fig, plotdata, cluster_col, text_col, tfidf=tfidf)

    return fig


def annotate_graph(fig, plotdata, cluster_col, text_col, tfidf=None, top_n=2):
    import networkx as nx

    tfidfs0 = tfidf.transform(plotdata[text_col])
    top_tfidfs = group_means(tfidfs0, 
                                plotdata[cluster_col], 
                                feature_names=tfidf.get_feature_names_out(), 
                                top_n=top_n)

    top_tfidfs = top_tfidfs.set_index(['group','word'])['value']
    word_list = top_tfidfs.reset_index().groupby('group')['word'].agg(list)
    cluster_centers = plotdata.groupby('cluster')[['embed_x','embed_y']].mean()

    for cluster, words in word_list.items():

        if cluster == -1:
            continue

        G = nx.Graph()
        G.add_nodes_from(words)
        pos = nx.spring_layout(G, seed=42)
        x_center, y_center = cluster_centers.loc[cluster]

        for word, (x,y) in pos.items():
            size = max(1, np.power(top_tfidfs.loc[cluster, word], 0.45) * 25)
            fig.add_annotation(
                x = x_center + x * 1.5,
                y = y_center + y * 1.5,
                text=word, 
                showarrow=False, 
                font={
                    'size': size,
                    'color':'rgba(34,139,34, 0.99)',
                }
            )

    return fig
