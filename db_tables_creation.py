from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from persona import Base as PersonaBase, Persona
from pelicula import Base as PeliculaBase, Pelicula
from score import Base as ScoreBase, Score
from usuario import Usuario
from trabajador import Trabajador

# Define the database connection URL
DB_URL = "postgresql://postgres:itba123@localhost:5432/itba_db"

# Create a database engine
engine = create_engine(DB_URL)

# Create a session factory
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    # Create all tables defined in the Base
    PersonaBase.metadata.create_all(engine)
    PeliculaBase.metadata.create_all(engine)
    ScoreBase.metadata.create_all(engine)

    df_peliculas = Pelicula.create_df_from_csv(filename="datasets/peliculas.csv")
    df_peliculas = Pelicula.rename_columns(df_peliculas)
    df_peliculas.to_sql("Pelicula", engine, if_exists='replace', index=False)

    df_personas = Persona.create_df_from_csv(filename="datasets/personas.csv")
    personas_instances = [Persona.create_object_from_df_row(row) for _, row in df_personas.iterrows()]
    session.add_all(personas_instances)

    df_scores = Score.create_df_from_csv(filename="datasets/scores.csv")
    df_scores.to_sql("Score", engine, if_exists='replace', index=False)

    df_users = Usuario.create_df_from_csv(filename="datasets/usuarios.csv")
    df_users.to_sql("Usuario", engine, if_exists='replace', index=False)

    df_trabajadores = Trabajador.create_df_from_csv(filename="datasets/trabajadores.csv")
    df_trabajadores.to_sql("Trabajador", engine, if_exists='replace', index=False)

    session.commit()
    session.close()

