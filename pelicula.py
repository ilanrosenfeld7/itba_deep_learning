import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt
from sqlalchemy import Column, Integer, String, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pelicula(Base):
    __tablename__ = 'Pelicula'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    fecha_lanzamiento = Column(DateTime, nullable=False)
    imdb_url = Column(String(255), nullable=False)
    generos = Column(ARRAY(String), nullable=False)
    
    generos_de_peliculas = ["unknown", "Action","Adventure","Animation","Children's","Comedy","Crime","Documentary","Drama",
                   "Fantasy","Film-Noir","Horror","Musical","Mystery","Romance","Sci-Fi","Thriller","War","Western"]

    def __init__(self, nombre, fecha_lanzamiento, imdb_url, generos, id = None):
        self.nombre = nombre
        self.fecha_lanzamiento = fecha_lanzamiento
        self.imdb_url = imdb_url
        self.generos = generos
        self.id = id

    def __repr__(self):
        return f'Nombre: {self.nombre}, Fecha Lanzamiento: {self.fecha_lanzamiento}, IMDB URL: {self.imdb_url}, Generos: {", ".join(self.generos)}\n'

    @classmethod
    def rename_columns(cls, df):
        # Create a dictionary with the column name mappings
        column_mappings = {'Name': 'nombre', 'Release Date': 'fecha_lanzamiento', 'IMDB URL':'imdb_url'}
        # Rename the columns
        df = df.rename(columns=column_mappings)
        return df

    @classmethod
    def get_by_id(cls, session, movie_id):
        row = session.query(Pelicula.id, Pelicula.nombre, Pelicula.fecha_lanzamiento, Pelicula.imdb_url).filter_by(id=movie_id).first()
        # Convert the row to a dictionary
        return {
            "id": row.id,
            "nombre": row.nombre,
            "fecha_lanzamiento": row.fecha_lanzamiento.strftime("%Y-%m-%d"),
            "imdb_url": row.imdb_url
        }

    def class_instance_to_df_row(self):
        """
        Transforma una instancia de la clase a un Dataframe row de pandas
        """
        basic_info_dict = {'id': self.id, 'Name': self.nombre, 'Release Date': self.fecha_lanzamiento, 'IMDB URL': self.imdb_url}
        generos_info_dict = dict([(genero, 1) if genero in self.generos else (genero,0) for genero in Pelicula.generos_de_peliculas])
        pelicula_info_dict = [basic_info_dict | generos_info_dict]
        return pd.DataFrame.from_records(pelicula_info_dict)

    def write_df(self, df_mov, overwrite = False):
        """
        Este método recibe el dataframe de películas y agrega la película
        Si el id es None, toma el id más alto del DF y le suma uno. 
        Si el id ya existía, si overwite = False no la agrega y devuelve un error, sino, lo sobreescribe.
        """
        if not self.id:
            self.id = df_peliculas["id"].max() + 1
            print(f"Se asigna el id maximo a la pelicula: {self.id}")
            df_mov = pd.concat([df_mov, self.class_instance_to_df_row()], ignore_index=True)
        else:
            if self.id in df_peliculas["id"].values: # TODO pasar a query
                if not overwrite:
                    print(f"Error: el id de pelicula {self.id} ya existe")
                else: 
                    df_mov.loc[df_mov['id'] == self.id] = self.class_instance_to_df_row().values.tolist()[0]
            else: 
                df_mov = pd.concat([df_mov, self.class_instance_to_df_row()], ignore_index=True)
        return df_mov

    @classmethod
    def create_object_from_df_row(cls, row):
        """
        Crea una instancia de la clase a partir de una fila de un dataframe
        """
        generos = [genero for genero in Pelicula.generos_de_peliculas if row[genero] == 1]
        return Pelicula(row['Name'], row["Release Date"], row["IMDB URL"], generos, row['id'])

    @classmethod
    def create_df_from_csv(cls, filename):
        """
        Crea un dataframe de peliculas a partir de un csv, y realiza algunas limpiezas/transformaciones
        """
        df_peliculas = pd.read_csv(filename)

        df_peliculas.dropna(subset=['Release Date'], inplace=True)
        df_peliculas["Release Date"] = df_peliculas["Release Date"].apply(lambda x: datetime.strptime(x, "%d-%b-%Y"))
        
        df_peliculas["IMDB URL"].fillna("http://us.imdb.com/M/title-exact?Unknown", inplace=True)
        
        return df_peliculas

    @classmethod
    def get_from_df(cls, df_mov, id=None, nombre = None, anios = None, generos = None):
        """
        Este class method devuelve una lista de objetos 'Pelicula' buscando por:
        # id: id --> se considera que se pasa un único id
        # nombre: nombre de la película --> se pasa un string y se busca peliculas que contengan tal substring en su nombre
        # anios: [desde_año, hasta_año]
        # generos: [generos]
        """
        if id:
            df_mov = df_mov.query('id == ' + str(id))
        if nombre:
            df_mov = df_mov.query(f"Name.str.contains('{nombre}')")
        if anios:
            df_mov = df_mov.loc[(df_mov['Release Date'] >= datetime(anios[0],1,1)) & (df_mov['Release Date'] <= datetime(anios[1],1,1))]
        if generos:
            logical_conjunction = " and ".join(["`" + genero + "` == 1" for genero in generos])
            df_mov = df_mov.query(logical_conjunction)
        return df_mov
    
    @classmethod
    def get_stats(cls, df_mov, anios=None, generos=None):
        """
        # Este class method imprime una serie de estadísticas calculadas sobre los resultados de una consulta al DataFrame df_mov. 
        # Las estadísticas se realizarán sobre las filas que cumplan con los requisitos de:
        # anios: [desde_año, hasta_año]
        # generos: [generos]
        # Las estadísticas son:
        # - Datos película más vieja
        # - Datos película más nueva
        # - Bar plots con la cantidad de películas por año/género.
        """
        df_mov = Pelicula.get_from_df(df_mov, anios=anios, generos=generos)

        cantidad_peliculas = len(df_mov)
        print(f"Cantidad de peliculas: {cantidad_peliculas}")

        # Obtener películas más vieja
        pelicula_mas_vieja = df_mov.loc[df_mov['Release Date'].idxmin()]['Name']
        print(f"Pelicula más vieja: {pelicula_mas_vieja}")

        pelicula_mas_nueva = df_mov.loc[df_mov['Release Date'].idxmax()]['Name']
        print(f"Pelicula más nueva: {pelicula_mas_nueva}")

        peliculas_por_anio = df_mov.groupby(df_mov['Release Date'].dt.year).size()
        plt.bar(peliculas_por_anio.index, peliculas_por_anio.values)
        plt.xlabel('Anio')
        plt.ylabel('Numero de peliculas')
        plt.title(f'Numero de peliculas por anio para anios={anios} y generos={generos}')
        # hacer que crezca de a enteros
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MultipleLocator(base=1))
        plt.show()
        
        # creo columna sintética genero
        df_mov["genero"] = None
        for index, row in df_mov.iterrows():
            pelicula_instance = Pelicula.create_object_from_df_row(row)
            df_mov.loc[index, 'genero'] = ",".join(pelicula_instance.generos)

        # Parto la columna 'genero' por la coma y le hago un explode
        df_mov['genero'] = df_mov['genero'].str.split(',')
        df_mov_exploded = df_mov.explode('genero')

        peliculas_por_genero = df_mov_exploded.groupby('genero').size()
        # Plot the grouped data
        peliculas_por_genero.plot(kind='bar')
        # Add labels and title to the plot
        plt.xlabel('Generos')
        plt.ylabel('Count')
        plt.title(f'Numero de peliculas por genero para anios={anios} y generos={generos}')
        # Show the plot
        plt.show()

    def remove_from_df(self, df_mov):
        """
        # Borra del DataFrame el objeto contenido en esta clase.
        # Para realizar el borrado todas las propiedades del objeto deben coincidir
        # con la entrada en el DF. Caso contrario imprime un error.
        """
        df_row = self.class_instance_to_df_row()
        # se asume para cada id hay a lo sumo una película
        row_con_mismo_id = Pelicula.get_from_df(df_mov, id=self.id)
        if not row_con_mismo_id.empty:
            if (df_row.equals(row_con_mismo_id)):
                df_mov = df_mov[df_mov['id'] != self.id]
                print(f"Se ha borrado la pelicula con id {self.id}")
            else: print("Error: existe fila con mismo id pero no todas las propiedades son iguales")
        else: print("No existe un row con el mismo id que la instancia")
        return df_mov

# python -W ignore pelicula.py
if __name__ == '__main__':
    # Cargar CSV a un dataframe
    df_peliculas = Pelicula.create_df_from_csv(filename="datasets/peliculas.csv")

    # Creo película 1 sin Id
    print("Agregado New Movie 1 sin id")
    peli1 = Pelicula("New Movie 1", datetime(1972, 10, 25), "http://us.imdb.com/M/title-exact?new_movie_1", ["Action","Drama","Crime"])
    # Agrego peli 1 al dataframe, al no tener ID, le asignará el max + 1 = 1683
    df_peliculas = peli1.write_df(df_peliculas)
    # Valido se agregó correctamente
    print(Pelicula.get_from_df(df_peliculas, id=1683))
    print("--------------")

    # Creo película 2 con Id no existente
    print("Test Case 2: Agregando New Movie 2 con id inexistente")
    peli2 = Pelicula("New Movie 2", datetime(1972, 10, 25), "http://us.imdb.com/M/title-exact?new_movie_2", ["Action","Drama","Crime"], 2000)
    # Agrego peli 2 al dataframe, se agregará sin problemas por ser un Id nuevo
    df_peliculas = peli2.write_df(df_peliculas)
    # Valido se agregó correctamente
    print(Pelicula.get_from_df(df_peliculas, id=2000))
    print("--------------")
    
    # Creo película 3 con Id ya existente (3)
    print("Test Case 3: Agregando New Movie 3 con id existente, sin overwrite")
    peli3 = Pelicula("New Movie 3", datetime(1972, 10, 25), "http://us.imdb.com/M/title-exact?new_movie_3", ["Action","Drama","Crime"], 3)
    # Trato de agregar peli 3 al dataframe, me dará error porque por default el overwite es False
    df_peliculas = peli3.write_df(df_peliculas)
    print("--------------")

    # Trato de agregarla ahora con overwrite True
    print("Test Case 4: Agregando New Movie 3 con id repetido, con overwrite")
    df_peliculas = peli3.write_df(df_peliculas, True)
    # Valido reemplazó correctamente la peli con id 3
    print(Pelicula.get_from_df(df_peliculas, id=3))
    print("--------------")

    print("Probando get_from_df con nombre=Seven")
    print(Pelicula.get_from_df(df_peliculas, nombre="Seven"))
    print("--------------")

    print("Probando get_from_df con id=690 & nombre=Seven")
    print(Pelicula.get_from_df(df_peliculas, id=690, nombre="Seven"))
    print("--------------")

    print("Probando get_from_df con anios=1990, 1991")
    print(Pelicula.get_from_df(df_peliculas, anios=(1990, 1991)))
    print("--------------")

    print("Probando get_from_df con anios=1990, 1991, generos=[Thriller]")
    print(Pelicula.get_from_df(df_peliculas, anios=(1990, 1991), generos=["Thriller"]))
    print("--------------")

    print("Probando get_from_df con anios=1990, 1991, generos=[Thriller, Sci-Fi]")
    print(Pelicula.get_from_df(df_peliculas, anios=(1990, 1991), generos=["Thriller","Sci-Fi"]))
    print("--------------")


    print("Probando delete row con id inexistente")
    peli4 = Pelicula("New Movie 4", datetime(1972, 10, 25), "http://us.imdb.com/M/title-exact?new_movie_4", ["Action","Drama","Crime"], 5000)
    df_peliculas = peli4.remove_from_df(df_peliculas)
    print("--------------")

    print("Probando delete row con id existente pero sin coincidir todas las propiedades")
    peli4 = Pelicula("New Movie 4", datetime(1972, 10, 25), "http://us.imdb.com/M/title-exact?new_movie_4", ["Action","Drama","Crime"], 1)
    df_peliculas = peli4.remove_from_df(df_peliculas)
    print("--------------")

    print(f"Probando delete row con id existente y coincidiendo todas las propiedades (Toy Story). Actual count: {len(df_peliculas)}")
    peli4 = Pelicula("Toy Story (1995)", datetime(1995, 1, 1), "http://us.imdb.com/M/title-exact?Toy%20Story%20(1995)", ["Animation","Children's","Comedy"], 1)
    df_peliculas = peli4.remove_from_df(df_peliculas)
    print(f"Nuevo count: {len(df_peliculas)}")
    print("--------------")

    print("Probando get general stats")
    print(Pelicula.get_stats(df_peliculas))
    print("--------------")

    print("Probando get stats entre 1990 y 1992, genero Thriller")
    print(Pelicula.get_stats(df_peliculas, anios=[1990,1992], generos=['Thriller']))
    print("--------------")