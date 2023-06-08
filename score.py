import pandas as pd
from datetime import datetime

class Score:
    
    def __init__(self, user_id, pelicula_id, puntuacion, timestamp, id=None):
        self.user_id = user_id
        self.pelicula_id = pelicula_id
        self.puntuacion = puntuacion
        self.timestamp = timestamp
        self.id = id
    
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
    def puntuacion_promedio_usuarios(cls, df_mov):
        # TODO Puntuación promedio de usuario(s) por año(de película)/género.
        pass

    @classmethod
    def puntuacion_promedio_peliculas(cls, df_mov):
        # TODO Puntuación promedio de películas por género de usuario(sexo)/rango etáreo/Ocupación.
        pass

# python -W ignore score.py
if __name__ == '__main__':
    # Cargar CSV a un dataframe
    df_scores = Score.create_df_from_csv(filename="datasets/scores.csv")
    
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
    