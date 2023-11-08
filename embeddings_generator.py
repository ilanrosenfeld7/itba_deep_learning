from opensearchpy import Field, Boolean, Float, Integer, Document, Keyword, Text, DenseVector, Nested, Date, Object
from opensearchpy import OpenSearch
import numpy as np
import pandas as pd
import datetime
# import tensorflow

host = 'localhost'
port = 9200
auth = ('admin', 'admin')

client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = False,
)

print("---------------------")
print("HEALTH:")
print(client.cluster.health())

print("---------------------")
print("EXISTE INDICE MOVIES:")
print(client.indices.exists('movie'))

# CÓDIGO GASPAR

scores_df = pd.read_csv('datasets/scores.csv')
peliculas_df = pd.read_csv('datasets/peliculas.csv')

# %%
score_peli_df = scores_df.merge(peliculas_df,how='left',right_on='id',left_on='movie_id')
score_peli_df

# %%

dict_pelis = {}
for n,i in enumerate(score_peli_df.movie_id.unique()):
    dict_pelis.update({i:n+1})
dict_users = {}
for n,i in enumerate(score_peli_df.user_id.unique()):
    dict_users.update({i:n+1})
dict_pelis

# %%
score_peli_df['movie_id'] = score_peli_df['movie_id'].map(dict_pelis)
score_peli_df['user_id'] = score_peli_df['user_id'].map(dict_users)
score_peli_df[score_peli_df['Name']=='Goofy Movie, A (1995)']

# %% MODELO BASE
print("---------------------")
df_train = score_peli_df.iloc[0:80000]
df_validation = score_peli_df.iloc[80000:90000]
df_test = score_peli_df.iloc[90000:]
print("SHAPES TRAIN, VALIDATION, TEST:")
print(df_train.shape,df_validation.shape,df_test.shape)

# %%
print("---------------------")
print("voy a predecir el rating que le da a la pelicula un usuario con el promedio de raiting de la pelicula")
avg_score_movie = df_train.groupby('movie_id')['rating'].mean().reset_index()
avg_score_movie
