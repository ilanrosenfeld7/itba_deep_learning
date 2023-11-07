from flask import Flask, jsonify
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
        'app_name': 'Access API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

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
