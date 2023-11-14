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
from opensearch_api import get_movie_vector, get_k_similar_movies

app = Flask(__name__)
api = Api(app, title='ITBA Recommendations API', description='API documentation using Swagger')

# Read the opensearch properties file
with open('connection_properties.json', 'r') as file:
    connection_properties = json.load(file)

postgres_user = connection_properties["postgres"]["username"]
postgres_password = connection_properties["postgres"]["password"]
postgres_host = connection_properties["postgres"]["_host_docker"]
postgres_port = connection_properties["postgres"]["port"]
postgres_db = connection_properties["postgres"]["db"]
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
db = SQLAlchemy(app)

client = OpenSearch(
        hosts=[{'host': connection_properties["opensearch"]["_host_docker"], 'port': connection_properties["opensearch"]["port"]}],
        http_auth=(connection_properties["opensearch"]["username"], connection_properties["opensearch"]["password"]),
        use_ssl=True,
        verify_certs=False,
)

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
        peli["ranking"] = i+1

    return peliculas_con_info


@app.route('/similar_movies', methods=['GET'])
def get_similar_movies():
    movie_id = request.args.get('movie_id')
    k = int(request.args.get('k')) + 1

    if not movie_id or not k:
        abort(400, "You must specify both movie_id and k")

    movie_vector = get_movie_vector(client, movie_id)
    if movie_vector:
        similar_movies = get_k_similar_movies(client, movie_vector, k)
        session = Session()
        # Agrego ranking index y cruzo info con RDBMS
        k_similar_movies = []
        for i, hit in enumerate(similar_movies):
            if not int(hit["_source"]["movie_id"]) == int(movie_id):
                new_json = Pelicula.get_by_id(session, hit["_source"]["movie_id"])
                new_json["ranking"] = i
                k_similar_movies.append(new_json)

        return k_similar_movies

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
