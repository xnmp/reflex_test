
from sklearn.base import BaseEstimator, TransformerMixin

class EncodeTransformer(BaseEstimator, TransformerMixin):
    def __init__(self) -> None:
        from FlagEmbedding import FlagModel
        self.model = FlagModel('/home/wangc26/RG271_dash/models/bge-small-en-v1.5')
    def transform(self, text_series):
        return self.model.encode(text_series.tolist())
    def fit(self, X, y=None):
        return self


from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from openTSNE.sklearn import TSNE
from daal4py.sklearn.cluster import DBSCAN
# from hdbscan import HDBSCAN
# from pacmap import PaCMAP
# from umap import UMAP


def default_embedder():
    return make_pipeline(
        TfidfVectorizer(analyzer='word', ngram_range=(1,2), max_features=2000),
        # EncodeTransformer(),
        TruncatedSVD(n_components=50, random_state=42),
        TSNE(perplexity=30, initialization='pca', random_state=42), #metric='cosine'
        # UMAP(metric='cosine', n_components=10),
        # PaCMAP(n_components=2, n_neighbors=None, MN_ratio=0.5, FP_ratio=2.0)
    )

