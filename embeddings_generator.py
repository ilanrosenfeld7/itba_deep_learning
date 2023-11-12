import pandas as pd
from keras.layers import Input, Embedding, Flatten, Dropout, Concatenate, Dense, Activation, Lambda
from keras import Model
from keras.regularizers import l2
from keras.optimizers import Adam
from opensearchpy import Field, Boolean, Float, Integer, Document, Keyword, Text, DenseVector, Nested, Date, Object
from opensearchpy import OpenSearch
import warnings
import datetime

# Set warning filter to 'ignore'
warnings.filterwarnings('ignore')

scores_df = pd.read_csv('datasets/scores.csv')
peliculas_df = pd.read_csv('datasets/peliculas.csv')
users_df = pd.read_csv("datasets/usuarios.csv")

u_unique = scores_df.user_id.unique()
user2Idx = {o:i+1 for i,o in enumerate(u_unique)}

m_unique = scores_df.movie_id.unique()
movie2Idx = {o:i+1 for i,o in enumerate(m_unique)}

def join_df(left, right, left_on, right_on=None):
    if right_on is None: right_on = left_on
    return left.merge(right, how='left', left_on=left_on, right_on=right_on,
                      suffixes=("", "_y"))

ratings = join_df(scores_df, peliculas_df, "movie_id", "id")

print(len(ratings))

ratings.user_id = ratings.user_id.apply(lambda x: user2Idx[x])
ratings.movie_id = ratings.movie_id.apply(lambda x: movie2Idx[x])

print(ratings.head())

# ratings['Date'] = ratings['Date']/max(ratings['Date'])

from sklearn.model_selection import train_test_split
ratings_train, ratings_val = train_test_split(ratings, test_size=0.2)

n_split = 20000
ratings_train = ratings[n_split:]
ratings_val = ratings[:n_split]
print(f"Len train: {len(ratings_train)}, len val: {len(ratings_val)}")

n_users = int(ratings.user_id.nunique())
n_movies = int(ratings.movie_id.nunique())
n_users_train = int(ratings_train.user_id.nunique())
n_movies_train = int(ratings_train.movie_id.nunique())
print(n_users, n_movies, n_users_train, n_movies_train)

max_rating = ratings_train['rating'].max()
min_rating = ratings_train['rating'].min()
av_rating = ratings_train['rating'].mean()
max_rating, min_rating, av_rating

# Diferencia: las dimensiones de los Latent factors pueden ser distintos
n_latent_factors_user = 5
n_latent_factors_movie = 8

genre = ['Action', 'Adventure', 'Animation',
              "Children's", 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
              'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
              'Thriller', 'War', 'Western']

genre_input = Input(shape=[len(genre)],name='genre')
timestamp_input = Input(shape=[1],name='timestamp')
movie_input = Input(shape=[1],name='Item')
movie_embedding = Embedding(n_movies + 1, n_latent_factors_movie, name='Movie-Embedding', embeddings_regularizer = l2(0.001))(movie_input)
movie_vec = Flatten(name='FlattenMovies')(movie_embedding)
# movie_vec = Dropout(0.2)(movie_vec)


user_input = Input(shape=[1],name='User')
user_vec = Flatten(name='FlattenUsers')(Embedding(n_users + 1, n_latent_factors_user,name='User-Embedding', embeddings_regularizer = l2(0.001))(user_input))
# user_vec = Dropout(0.2)(user_vec)


concat = Concatenate(name='Concat')([
    movie_vec, user_vec, timestamp_input, genre_input
])
# concat = Dropout(0.2)(concat)

x = Dense(50,name='FullyConnected-1', activation='relu', kernel_regularizer=l2(0.001))(concat)
#x = Dropout(0.5)(x)
#x = Dense(50,name='FullyConnected-1', activation='relu')(concat)
#x = Dropout(0.5)(x)


## Se pueden sacar las siguientes dos lineas para no forzar a sigmoidea
x = Dense(1, activation='sigmoid',name='Activation')(x)
x = Lambda(lambda z: (max_rating - min_rating) * z + min_rating)(x)
##

model = Model([user_input, movie_input, timestamp_input, genre_input], x)
model.summary()

print("EMBEDDINGS")

movie_embeddings_layer = model.layers[2]
user_embeddings_layer = model.layers[3]
movie_embeddings_layer.name, user_embeddings_layer.name

movie_embeddings_matrix = movie_embeddings_layer.get_weights()[0]
user_embeddings_matrix = user_embeddings_layer.get_weights()[0]
movie_embeddings_matrix.shape, user_embeddings_matrix.shape


print("TEST.PY PARA OPENSEARCH")

# %%
users_df['userIdx'] = users_df['id'].apply(lambda x: user2Idx[x])
peliculas_df['movieIdx'] = peliculas_df['id'].apply(lambda x: movie2Idx[x])

# %%
host = 'localhost'
port = 9200
auth = ('admin', 'admin')

client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = False,
)
# %%
client.cluster.health()

print(f"EXISTE INDICE MOVIE: {client.indices.exists('movie')}")
if client.indices.exists('movie'):
    print("ELIMINANDO INDICE MOVIE")
    client.indices.delete('movie')

class KNNVector(Field):
    name = "knn_vector"
    def __init__(self, dimension, method, **kwargs):
        super(KNNVector, self).__init__(dimension=dimension, method=method, **kwargs)

method = {
    "name": "hnsw",
    "space_type": "cosinesimil",
    "engine": "nmslib"
}

index_name = 'movie'
class Movie(Document):
    movie_id = Keyword()
    url = Keyword()
    name = Text()
    created_at = Date()

    vector = KNNVector(
        movie_embeddings_matrix.shape[1],
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
# %%
# %%
Movie.init(using=client)
# %%
# client.indices.get(index="*")
# %%


# %%
print(f"CONTENIDO INDICE: {client.indices.get('movie')}")
# %%

# %%

print("PERSISTIENDO DATAFRAME AL INDICE")
for i, row in peliculas_df.iterrows():
    mv = Movie(
        movie_id = row.id,
        url = row["IMDB URL"],
        name = row['Name'],
        vector = list(movie_embeddings_matrix[row.movieIdx]),
        created_at = datetime.datetime.now()
    )
    mv.save(using=client)
# %%