def get_movie_vector(client, movie_id):

    # Buscar movie en opensearch
    query = {
        "query": {
            "term": {
                "movie_id": {
                    "value": movie_id
                }
            }
        }
    }
    response = client.search(index='movie', body=query)
    if response['hits']['hits']:
        return response['hits']['hits'][0]["_source"]["vector"]
    return None


def get_k_similar_movies(client, movie_vector, k):
    query = {
        "size": k,
        "query": {
            "knn": {
                "vector": {
                    "vector": movie_vector,
                    "k": k
                }
            }
        }
    }
    response = client.search(index='movie', body=query)
    return response.get("hits", {}).get("hits", [])