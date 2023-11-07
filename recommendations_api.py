from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_restx import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from pelicula import Pelicula
import json

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

@app.route('/recommendations', methods=['GET'])
def get_movie_recommendations():
    # Retrieve user ID and number K from the request parameters
    user_id = request.args.get('user_id')
    k = int(request.args.get('k'))

    if not user_id or not k:
        abort(400, "You must specify both user_id and k")

    """
    http://localhost:5000/recommendations?user_id=1&k=3
    devolver como mínimo nombre, año, url, géneros y lugar en el ranking de la recomendación de la película. Obtener los datos de la película de la DB relacional.
    """
    # Get recommendations based on the user ID
    #recommendations = movie_recommendations.get(user_id, [])

    session = Session()
    # this will be replaced later for the data obtained from vector DB
    peli1 = Pelicula.get_by_id(session, 1)
    peli2 = Pelicula.get_by_id(session, 2)
    peli3 = Pelicula.get_by_id(session, 3)
    peli4 = Pelicula.get_by_id(session, 4)
    peli5 = Pelicula.get_by_id(session, 5)
    peli6 = Pelicula.get_by_id(session, 6)
    peli7 = Pelicula.get_by_id(session, 7)
    recommendations = [peli1, peli2, peli3, peli4, peli5, peli6, peli7]

    # Return K movie recommendations
    return jsonify(recommendations[:k])

@app.route('/similar_movies', methods=['GET'])
def get_similar_movies():
    movie_id = request.args.get('movie_id')
    k = int(request.args.get('k'))

    if not movie_id or not k:
        abort(400, "You must specify both movie_id and k")
    """
    http://localhost:5000/similar_movies?movie_id=1&k=3
    devolver como mínimo nombre, año, url, géneros y lugar en el ranking de la recomendación de la película. Obtener los datos de la película de la DB relacional.
    """

    # Get recommendations based on the user ID
    # recommendations = movie_recommendations.get(user_id, [])

    session = Session()
    # this will be replaced later for the data obtained from vector DB
    peli1 = Pelicula.get_by_id(session, 8)
    peli2 = Pelicula.get_by_id(session, 9)
    peli3 = Pelicula.get_by_id(session, 10)
    peli4 = Pelicula.get_by_id(session, 11)
    peli5 = Pelicula.get_by_id(session, 12)
    peli6 = Pelicula.get_by_id(session, 13)
    peli7 = Pelicula.get_by_id(session, 14)
    recommendations = [peli1, peli2, peli3, peli4, peli5, peli6, peli7]

    # Return K movie recommendations
    return jsonify(recommendations[:k])

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    session = Session()
    movie = Pelicula.get_by_id(session, movie_id)
    if movie:
        return json.dumps(movie), 200
    else:
        return jsonify({'error': 'Movie not found'}), 404

@app.route('/health')
def health_check():
    return jsonify(status='OK')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
