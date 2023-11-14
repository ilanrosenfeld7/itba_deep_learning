from opensearchpy import OpenSearch
from opensearchpy import Field, Boolean, Float, Integer, Document, Keyword, Text, DenseVector, Nested, Date, Object
import datetime
import joblib
import warnings
import json


index_name = 'movie'

# Disable all warnings
warnings.filterwarnings("ignore")

class KNNVector(Field):
    name = "knn_vector"
    def __init__(self, dimension, method, **kwargs):
        super(KNNVector, self).__init__(dimension=dimension, method=method, **kwargs)


method = {
    "name": "hnsw",
    "space_type": "cosinesimil",
    "engine": "nmslib"
}


class Movie(Document):
    movie_id = Keyword()
    url = Keyword()
    name = Text()
    created_at = Date()

    vector = KNNVector(
        96,
        method
    )
    class Index:
        name = index_name
        settings = {
                'index': {
                'knn': True
            }
        }

    def save(self, ** kwargs):
        self.meta.id = self.movie_id
        return super(Movie, self).save(** kwargs)


if __name__ == '__main__':
    print("------------------------------")
    print("VALIDANDO CONEXIÓN CON OPENSEARCH")

    # Read the opensearch properties file
    with open('connection_properties.json', 'r') as file:
        opensearch_properties = json.load(file)

    client = OpenSearch(
        hosts=[{'host': opensearch_properties["opensearch"]["host"], 'port': opensearch_properties["opensearch"]["port"]}],
        http_auth=(opensearch_properties["opensearch"]["username"], opensearch_properties["opensearch"]["password"]),
        use_ssl=True,
        verify_certs=False,
    )
    # %%
    print(client.cluster.health())

    print(f"EXISTE INDICE MOVIE: {client.indices.exists('movie')}")
    if client.indices.exists('movie'):
        print("ELIMINANDO INDICE MOVIE")
        client.indices.delete('movie')

    Movie.init(using=client)

    print("------------------------------")
    print("PERSISTIENDO EMBEDDINGS MOVIES EN OPENSEARCH")
    # Assuming the DataFrame was saved using joblib.dump and the file is named 'data.joblib'
    df_movies = joblib.load('peliculas_df')
    array_embeddings = joblib.load('embedding_movies_genre')

    #print(array_embeddings[265])
    #print(array_embeddings[266])
    """"""
    # Iterate over DataFrame and ndarray elements
    for i, row in df_movies.iterrows():
            try:
                mv = Movie(
                    movie_id=row['movie_id'],
                    url=row["IMDB URL"],
                    name=row['Name'],
                    vector=list(array_embeddings[i]),
                    created_at=datetime.datetime.now()
                )
                mv.save(using=client)
            except:
                print(f"ERROR WITH {i}")
