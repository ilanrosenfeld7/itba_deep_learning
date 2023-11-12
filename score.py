import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt
from pelicula import Pelicula
from usuario import Usuario
from persona import Persona
from trabajador import Trabajador
from sqlalchemy import Column, Integer, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import desc

Base = declarative_base()

class Score(Base):

    __tablename__ = 'Score'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    pelicula_id = Column(Integer, nullable=False)
    puntuacion = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    def __init__(self, user_id, pelicula_id, puntuacion, timestamp, id=None):
        self.user_id = user_id
        self.pelicula_id = pelicula_id
        self.puntuacion = puntuacion
        self.timestamp = timestamp
        self.id = id

    @classmethod
    def rename_columns_and_compress_genders(cls, df):
        new_df = pd.DataFrame({
            'id': df['id'],
            'user_id': df['user_id'],
            'pelicula_id': df['movie_id'],
            'puntuacion': df['rating'],
            'timestamp': df['Date']
        })

        return new_df

    @classmethod
    def get_by_user_id(cls, session, user_id):
        rankings = session.query(Score).filter(Score.user_id == user_id).order_by(desc(Score.puntuacion)).all()
        rows = [{"id": row.id,
                 "user_id": row.user_id,
                 "pelicula_id": row.pelicula_id,
                 'puntuacion': row.puntuacion,
                 'timestamp': row.timestamp
                 }
                for row in rankings]
        return rows



    def class_instance_to_df_row(self):
        """
        Transforma una instancia de la clase a un Dataframe row de pandas
        """
        score_as_dict = {'id': self.id, 'user_id': self.user_id, 'movie_id': self.pelicula_id, 'rating': self.puntuacion, 'Date': self.timestamp}
        return pd.DataFrame([score_as_dict])
    
    def write_df(self, df_scores, overwrite = False):
        """
        Este método recibe el dataframe de scores y agrega el score
        # Si ya existía un score del user para la pelicula, y overwrite=True, actualiza el score y timestamp
        # Si no existía, lo agrega, con el id máximo + 1
        """
        ranking_para_user_y_movie = df_scores.query(f'user_id == {str(self.user_id)} and movie_id == {str(self.pelicula_id)}')
        if ranking_para_user_y_movie.empty:
            self.id = df_scores["id"].max() + 1
            print(f"No existe el ranking para ese user y movie, se agregara con id maximo: {self.id}")
            df_scores = pd.concat([df_scores, self.class_instance_to_df_row()], ignore_index=True)
        elif overwrite:
            print("Ya existia el ranking para user y movie, se actualizará puntuación y timestamp (se seteó overwrite en True)")
            self.id = ranking_para_user_y_movie.iloc[0]['id']
            df_scores.loc[df_scores['id'] == self.id] = self.class_instance_to_df_row().values.tolist()[0]
        else: 
            print("Error: Ya existia el ranking para user y movie (se seteó overwrite en False)")
        return df_scores
    
    @classmethod
    def get_from_df(cls, df_scores, id=None, users_ids = None, peliculas_ids = None):
        """
        Este class method devuelve una lista de objetos 'Score' buscando por:
        # id: id --> se considera que se pasa un único id
        # users_ids --> devuelve todos los score que tengan tales user ids en ellas
        # peliculas_ids --> devuelve todos los score que tengan tales peliculas id en ellas
        """

        if id:
            df_scores = df_scores.query('id == ' + str(id))
        if users_ids:
            logical_disjunction = " or ".join(list(map(lambda id: f"user_id == {id}", users_ids)))
            df_scores = df_scores.query(logical_disjunction)
        if peliculas_ids:
            logical_disjunction = " or ".join(list(map(lambda id: f"movie_id == {id}", peliculas_ids)))
            df_scores = df_scores.query(logical_disjunction)
        return df_scores
    
    @classmethod
    def create_df_from_csv(cls, filename):
        """
        Crea un dataframe de scores a partir de un csv
        """
        df_scores = pd.read_csv(filename)

        # Le doy nombre a columna inicial (id)
        column_names = df_scores.columns.tolist()
        df_scores = df_scores.rename(columns={column_names[0]: "id"})

        return df_scores

    def remove_from_df(self, df_scores):
        """
        Borra del DataFrame el objeto contenido en esta clase.
        Para realizar el borrado sólo deben coincidir el user_id y el pelicula_id
        """

        row_existente = Score.get_from_df(df_scores, users_ids=[self.user_id], peliculas_ids=[self.pelicula_id])
        if row_existente.empty:
            print(f"No existe un score para user_id = {self.user_id} y movie_id = {self.pelicula_id}")
        else: 
            print(f"Score encontrado para user_id = {self.user_id} y movie_id = {self.pelicula_id}, con id {row_existente.iloc[0]['id']}, puntuacion {row_existente.iloc[0]['rating']} y timestamp {row_existente.iloc[0]['Date']}. Se borrará")
            df_scores = df_scores[df_scores['id'] != row_existente.iloc[0]['id']]
        return df_scores

    @classmethod
    def puntuacion_promedio_usuarios_anio_genero(cls, df_scores, df_peliculas, df_users, anios=None, usuarios=None):
        # Puntuación promedio de usuario(s) por año(de película)/género

        # creo columna sintética genero y año de lanzamiento
        df_peliculas["genero"] = None
        for index, row in df_peliculas.iterrows():
            pelicula_instance = Pelicula.create_object_from_df_row(row)
            df_peliculas.loc[index, 'genero'] = ",".join(pelicula_instance.generos)
            df_peliculas.loc[index, 'anio_lanzamiento_pelicula'] = pelicula_instance.fecha_lanzamiento.year
        # Parto la columna 'genero' por la coma y le hago un explode
        df_peliculas['genero'] = df_peliculas['genero'].str.split(',')
        df_mov_exploded = df_peliculas.explode('genero')

        df_scores_peliculas_merged = pd.merge(df_scores, df_mov_exploded, left_on='movie_id', right_on='id')
        df_scores_peliculas_merged_filtered = df_scores_peliculas_merged.loc[(df_scores_peliculas_merged['Release Date'] >= datetime(anios[0],1,1)) & (df_scores_peliculas_merged['Release Date'] <= datetime(anios[1],1,1))]
        
        if usuarios:
            df_users = df_users[df_users['id'].isin(usuarios)]
        
        df_scores_peliculas_users_merged = pd.merge(df_scores_peliculas_merged_filtered, df_users, left_on='user_id', right_on='id')
        
        # Puntuación promedio de usuario(s) por año(de película)
        grouped_df = df_scores_peliculas_users_merged.groupby(['anio_lanzamiento_pelicula', 'user_id']).mean().reset_index()

        fig, ax = plt.subplots()

        users = grouped_df['user_id'].unique()
        x = grouped_df['anio_lanzamiento_pelicula'].unique()

        width = 0.2
        offset = -0.2 * len(users) / 2

        for i, user in enumerate(users):
            user_data = grouped_df[grouped_df['user_id'] == user]
            y = user_data['rating']
            ax.bar(x + offset + i * width, y, width=width, label=f'User {user}')

        ax.set_xlabel('Anio lanzamiento')
        ax.set_ylabel('Rating promedio')
        ax.set_title('Rating Promedio por usuario, dividido por anio de lanzamiento')
        ax.set_xticks(x)
        ax.legend()
        plt.show()

        # Puntuación promedio de usuario(s) por género
        grouped_df = df_scores_peliculas_users_merged.groupby(['genero', 'user_id']).mean().reset_index()

        # Create dictionary to map gender values to numeric positions
        gender_mapping = {gender: i for i, gender in enumerate(grouped_df['genero'].unique())}

        # Plot bar chart
        fig, ax = plt.subplots()

        users = grouped_df['user_id'].unique()
        width = 0.2
        offset = -0.2 * len(users) / 2

        for i, user in enumerate(users):
            user_data = grouped_df[grouped_df['user_id'] == user]
            y = user_data['rating']
            x_pos = [gender_mapping[gender] + offset + i * width for gender in user_data['genero']]
            ax.bar(x_pos, y, width=width, label=f'User {user}')

        ax.set_xlabel('Genero de pelicula')
        ax.set_ylabel('Rating Promedio')
        ax.set_title('Rating promedio por usuario, dividido por género de película')
        ax.set_xticks(range(len(gender_mapping)))
        ax.set_xticklabels(gender_mapping.keys())
        ax.legend()
        plt.show()


    @classmethod
    def puntuacion_promedio_peliculas(cls, df_scores, df_peliculas, df_users, df_personas, df_trabajadores, anios=None):
        # Puntuación promedio de películas por género de usuario(sexo)/rango etario/Ocupación.
        
        df_users_personas_merged = pd.merge(df_users, df_personas, on='id')
        df_scores_users_merged = pd.merge(df_scores, df_users_personas_merged, left_on='user_id', right_on='id')
        
        # Puntuación promedio de películas por género de usuario(sexo)
        grouped_df = df_scores_users_merged.groupby(['Gender']).mean().reset_index()

        fig, ax = plt.subplots()

        x = grouped_df['Gender']
        y = grouped_df['rating']

        ax.bar(x, y)
        ax.set_xlabel('Género de usuario')
        ax.set_ylabel('Rating promedio')
        ax.set_title('Rating promedio agrupado por género de usuario')
        plt.show()

        # Puntuación promedio de películas por rango etario
        def get_year_range(year):
            year_ranges = [(year, year + 20) for year in range(1900, 2011, 20)]
            for start, end in year_ranges:
                if start <= year <= end:
                    return f'{start}-{end}'
            return 'Year not in range'
        
        # Add a new column range
        df_scores_users_merged['rango_etario'] = df_scores_users_merged['year of birth'].apply(get_year_range)
        puntuacion_usuarios_por_rango_etario = df_scores_users_merged.groupby('rango_etario')['rating'].mean()
        puntuacion_usuarios_por_rango_etario.plot(kind='bar')

        plt.xlabel('Rango etario')
        plt.ylabel('Puntuación promedio')
        plt.title(f'Puntuación promedio por rango etareo')
        plt.show()

        # Puntuación promedio de películas por ocupación
        df_scores_users_merged = pd.merge(df_scores_users_merged, df_trabajadores, left_on='user_id', right_on='id')
        puntuacion_usuarios_por_ocupacion = df_scores_users_merged.groupby('Position')['rating'].mean()
        puntuacion_usuarios_por_ocupacion.plot(kind='bar')

        plt.xlabel('Ocupación')
        plt.ylabel('Puntuación promedio')
        plt.title(f'Puntuación promedio por Ocupación')
        plt.show()  

# python -W ignore score.py
if __name__ == '__main__':
    # Cargar CSV a un dataframe
    df_scores = Score.create_df_from_csv(filename="datasets/scores.csv")
    df_users = Usuario.create_df_from_csv(filename="datasets/usuarios.csv")
    df_peliculas = Pelicula.create_df_from_csv(filename="datasets/peliculas.csv")
    df_personas = Persona.create_df_from_csv(filename="datasets/personas.csv")
    df_trabajadores = Trabajador.create_df_from_csv(filename="datasets/trabajadores.csv")
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Probando nuevo score que no existía, actual count: {len(df_scores)}")
    score1 = Score(5000, 242, 4, current_timestamp)
    df_scores = score1.write_df(df_scores)
    print(f"Nuevo count: {len(df_scores)}")
    print("--------------")

    print("Probando score ya existente, Overwrite False. Objeto actual:")
    print(Score.get_from_df(df_scores, users_ids=[196], peliculas_ids=[242]))
    score2 = Score(196, 242, 4, current_timestamp)
    df_scores = score2.write_df(df_scores)
    print("Objeto se mantiene igual:")
    print(Score.get_from_df(df_scores, users_ids=[196], peliculas_ids=[242]))
    print("--------------")

    print("Probando score ya existente, Overwrite True. Objeto actual:")
    print(Score.get_from_df(df_scores, users_ids=[196], peliculas_ids=[242]))
    df_scores = score2.write_df(df_scores, overwrite=True)
    print("Objeto actualizado:")
    print(Score.get_from_df(df_scores, users_ids=[196], peliculas_ids=[242]))
    print("--------------")

    print(f"Probando delete con combinacion no existente, actual count: {len(df_scores)}")
    score3 = Score(333, 444, 3, current_timestamp)
    df_scores = score3.remove_from_df(df_scores)
    print(f"Nuevo count: {len(df_scores)}")
    print("--------------")

    print(f"Probando delete con combinacion existente, actual count: {len(df_scores)}")
    score3 = Score(186, 302, 3, current_timestamp)
    df_scores = score3.remove_from_df(df_scores)
    print(f"Nuevo count: {len(df_scores)}")
    print("--------------")

    print(f"Probando stats: puntuacion_promedio_usuarios_anio_genero para años 1990-1992, user=1")
    Score.puntuacion_promedio_usuarios_anio_genero(df_scores, df_peliculas, df_users, anios=[1990,1992], usuarios=[5,6,7,8])
    print("--------------")
    
    print(f"Probando stats: puntuacion_promedio_peliculas para años 1990-1992 ")
    Score.puntuacion_promedio_peliculas(df_scores, df_peliculas, df_users, df_personas, df_trabajadores, anios=[1990,1992])
    print("--------------")
    