from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_restx import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from pelicula import Pelicula
from score import Score
from prediction_score import PredictionScore
import json
from opensearchpy import OpenSearch

app = Flask(__name__)
api = Api(app, title='ITBA Recommendations API', description='API documentation using Swagger')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:itba123@localhost:5432/itba_db'
db = SQLAlchemy(app)

# Create the engine and session
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)

SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Movie recommendations API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

host = 'localhost'
port = 9200
auth = ('admin', 'admin')

client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = False,
)


@app.route('/recommendations', methods=['GET'])
def get_movie_recommendations():
    # Retrieve user ID and number K from the request parameters
    user_id = request.args.get('user_id')
    k = int(request.args.get('k'))

    if not user_id or not k:
        abort(400, "You must specify both user_id and k")

    session = Session()

    # Traer todos los ids de peliculas de rankings hechos por el usuario
    ranked_movies = Score.get_by_user_id(session, user_id)

    # Traer predicciones para el usuario de peliculas aun no vistas y ordenadas descendentemente por predicción de ranking
    predictions = PredictionScore.get_by_user_id_and_ranked_movies(session, user_id, ranked_movies)
    if not predictions:
        return "User has already ranked all movies", 200

    peliculas_con_info = [Pelicula.get_by_id(session, prediction["movie_id"]) for prediction in predictions[:k]]
    for i, peli in enumerate(peliculas_con_info):
        peli["lugar_en_ranking"] = i+1

    return peliculas_con_info


@app.route('/similar_movies', methods=['GET'])
def get_similar_movies():
    movie_id = request.args.get('movie_id')
    k = int(request.args.get('k')) + 1

    if not movie_id or not k:
        abort(400, "You must specify both movie_id and k")

    # Define the search query
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
        vector = response['hits']['hits'][0]["_source"]["vector"]
        query = {
            "size": k,
            "query": {
                "knn": {
                    "vector": {
                        "vector": vector,
                        "k": k
                    }
                }
            }
        }
        response = client.search(index='movie', body=query)

        session = Session()

        k_similar_movies = []
        for i, hit in enumerate(response.get("hits", {}).get("hits", [])):
            if not int(hit["_source"]["movie_id"]) == int(movie_id):
                new_json = Pelicula.get_by_id(session, hit["_source"]["movie_id"])
                new_json["ranking"] = i
                k_similar_movies.append(new_json)

        return json.dumps(k_similar_movies)

    else: return jsonify({'error': 'Movie not found'}), 404


@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    session = Session()
    movie = Pelicula.get_by_id(session, movie_id)
    if movie:
        return json.dumps(movie), 200
    else:
        return jsonify({'error': 'Movie not found'}), 404


@app.route('/scores/<int:user_id>', methods=['GET'])
def get_rating(user_id):
    session = Session()
    rankings = Score.get_by_user_id(session, user_id)
    if rankings:
        return rankings, 200
    else:
        return jsonify({'error': 'Movie not found'}), 404

@app.route('/health')
def health_check():
    return jsonify(status='OK')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=90)
