from pelicula import Pelicula
from persona import Persona
from trabajador import Trabajador
from score import Score
from usuario import Usuario

def load_all(file_personas, file_trabajadores, file_usuarios, file_peliculas, file_scores):
    """
    El código de carga realiza un chequeo de consistencia entre los DataFrames y eliminar cualquier inconsistencia que se detecte. Por ejemplo un id presente en el DataFrame de usuarios 
    que no está presente en el DataFrame de personas, o un id de película que esté en el DataFrame de Scores, que no esté presente en el DataFrame de películas.
    """
    df_personas = Persona.create_df_from_csv(filename=file_personas)
    df_trabajadores = Trabajador.create_df_from_csv(filename=file_trabajadores)
    df_usuarios = Usuario.create_df_from_csv(filename=file_usuarios)
    df_peliculas = Pelicula.create_df_from_csv(filename=file_peliculas)
    df_scores = Score.create_df_from_csv(filename=file_scores)

    print(f"Cantidades antes de filtros: personas {len(df_personas)}, trabajadores {len(df_trabajadores)}, usuarios {len(df_usuarios)}, peliculas {len(df_peliculas)}, scores {len(df_scores)}")
    # filtro usuarios que no hayan sido de alta como personas
    df_usuarios_validos = df_usuarios[df_usuarios['id'].isin(df_personas['id'])]

    # filtro trabajadores que no hayan sido de alta como personas
    df_trabajadores_validos = df_trabajadores[df_trabajadores['id'].isin(df_personas['id'])]
    
    # filtro scores cuyos ids de usuarios y/o peliculas no sean válidos
    df_scores_validos = df_scores[df_scores['user_id'].isin(df_usuarios_validos['id']) & df_scores['movie_id'].isin(df_peliculas['id'])] 

    print(f"Cantidades tras filtros: personas {len(df_personas)}, trabajadores {len(df_trabajadores_validos)}, usuarios {len(df_usuarios_validos)}, peliculas {len(df_peliculas)}, scores {len(df_scores_validos)}")
    
    return df_personas, df_trabajadores_validos, df_usuarios_validos, df_peliculas, df_scores_validos

def save_all(df_personas, df_trabajadores, df_usuarios, df_peliculas, df_scores, file_personas="personas.csv", file_trabajadores="trabajadores.csv", file_usuarios="usuarios.csv", file_peliculas="peliculas.csv", file_scores="scores.csv"):
    """
    Salva los dataframes a CSVs
    """
    try:
        df_personas.to_csv(file_personas, index=False)
        df_trabajadores.to_csv(file_trabajadores, index=False)
        df_usuarios.to_csv(file_usuarios, index=False)
        df_peliculas.to_csv(file_peliculas, index=False)
        df_scores.to_csv(file_scores, index=False)
        return 0
    except:
        return -1
    
if __name__ == '__main__':
    df_personas, df_trabajadores, df_usuarios, df_peliculas, df_scores = load_all(
        "datasets/personas.csv",
        "datasets/trabajadores.csv",
        "datasets/usuarios.csv",
        "datasets/peliculas.csv",
        "datasets/scores.csv"
    )

    save_all_result = save_all(df_personas, 
             df_trabajadores, 
             df_usuarios, 
             df_peliculas, 
             df_scores,
             "datasets/personas.csv",
             "datasets/trabajadores.csv",
             "datasets/usuarios.csv",
             "datasets/peliculas.csv",
             "datasets/scores.csv"
             )
    if save_all_result == 0:
        print("CSVs guardados exitosamente")
    else: print("Error en el guardado de CSVs")