from opensearchpy import Field, Boolean, Float, Integer, Document, Keyword, Text, DenseVector, Nested, Date, Object
from opensearchpy import OpenSearch
import joblib

# %%
host = 'localhost'
port = 9200
auth = ('admin', 'admin')


if __name__ == '__main__':
    print("------------------------------")
    print("VALIDANDO CONEXIÓN CON OPENSEARCH")
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
    )
    # %%
    print(client.cluster.health())

    print("------------------------------")
    print("PERSISTIENDO EMBEDDINGS MOVIES EN OPENSEARCH")
    # Assuming the DataFrame was saved using joblib.dump and the file is named 'data.joblib'
    df_embeddings = joblib.load('embedding_movies_genre')
    print(type(df_embeddings))

    # Iterate over the embeddings and insert each one into OpenSearch
    for embedding in df_embeddings:
        # Convert ndarray to a JSON-compatible format
        embedding_json = embedding.tolist()
        print(embedding_json)
        # Insert the embedding into OpenSearch
        #client.index(index='your_index_name', body={'embedding': embedding_json})