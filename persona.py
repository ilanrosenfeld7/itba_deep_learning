import pandas as pd
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Define the Gender enum
class GenderEnum(Enum):
    FEMININE = "F"
    MASCULINE = "M"

class Persona(Base):
    __tablename__ = 'Persona'

    id = Column(Integer, primary_key=True)
    nombre_completo = Column(String(255), nullable=False)
    anio_nacimiento = Column(Integer, nullable=False)
    genero = Column(String(length=1), nullable=False)
    codigo_postal = Column(String(20), nullable=False)

    usuario = relationship("Usuario", uselist=False, back_populates="persona")
    trabajador = relationship("Trabajador", uselist=False, back_populates="persona")


    def __init__(self, nombre_completo, anio_nacimiento, genero, codigo_postal, id=None):
        self.id = id
        self.nombre_completo = nombre_completo
        self.anio_nacimiento = anio_nacimiento
        self.genero = genero
        self.codigo_postal = codigo_postal
    
    @classmethod
    def create_object_from_df_row(cls, row):
        """
        Crea una instancia de la clase a partir de una fila de un dataframe
        """
        return Persona(row["Full Name"], row["year of birth"], row['Gender'], row['Zip Code'], row['id'])
    
    @classmethod
    def create_df_from_csv(cls, filename):
        """
        Crea un dataframe de personas a partir de un csv
        """
        df_personas = pd.read_csv(filename)
        return df_personas

    def class_instance_to_df_row(self):
        """
        Transforma una instancia de la clase a un Dataframe row de pandas
        """
        persona_as_dict = {'id': self.id, 'Full Name': self.nombre_completo, 'year of birth': self.anio_nacimiento, 'Gender': self.genero, 'Zip Code': self.codigo_postal}
        return pd.DataFrame([persona_as_dict])
    
    @classmethod
    def get_from_df(cls, df_personas, id=None, nombre_completo=None, anios=None, genero=None, zip_code=None):
        """
        Este class method devuelve una lista de objetos 'Persona' buscando por:
        # id: id --> se considera que se pasa un único id
        # nombre_completo --> devuelve todas las personas que tienen el string pasado en su nombre
        # anios --> [desde_año, hasta_año]
        # genero: M o F
        # zip_code  --> se considera que se pasa un único zip code
        """

        if id:
            df_personas = df_personas.query('id == ' + str(id))
        if nombre_completo:
            df_personas = df_personas.query(f"`Full Name`.str.contains('{nombre_completo}')")
        if anios:
            df_personas = df_personas.loc[(df_personas['year of birth'] >= anios[0]) & (df_personas['year of birth'] <= anios[1])]
        if genero:
            df_personas = df_personas.query('Gender == ' + str(genero))
        if zip_code:
            df_personas = df_personas.query('`Zip Code` == ' + str(zip_code))
        return df_personas
    
    def write_df(self, df_personas, overwrite = False):
        """
        Este método recibe el dataframe de personas y agrega la persona
        Se asume hay una única persona con igual combinación de nombre completo y año de nacimiento
        """
        
        persona_existente = df_personas.query(f'`Full Name` == "{str(self.nombre_completo)}" and `year of birth` == {str(self.anio_nacimiento)}')
        if persona_existente.empty:
            self.id = df_personas["id"].max() + 1
            print(f"No existe persona con tal nombre y año de nacimiento. Se agregara con id maximo: {self.id}")
            df_personas = pd.concat([df_personas, self.class_instance_to_df_row()], ignore_index=True)
        elif overwrite:
            print("Ya existia la persona con tal nombre y año de nacimiento, se actualizará zip code y genero")
            self.id = persona_existente.iloc[0]['id']
            df_personas.loc[df_personas['id'] == self.id] = self.class_instance_to_df_row().values.tolist()[0]
        else: 
            print("Error: Ya existia la persona con tal nombre y año de nacimiento (se seteó overwrite en False)")
        return df_personas

    def remove_from_df(self, df_personas):
        """
        Borra del DataFrame el objeto contenido en esta clase.
        Para realizar el borrado sólo deben coincidir el full name y el anio de nacimiento
        """

        row_existente = Persona.get_from_df(df_personas, nombre_completo=self.nombre_completo, anios=[self.anio_nacimiento, self.anio_nacimiento])
        if row_existente.empty:
            print(f"No existe una persona con nombre_completo = {self.nombre_completo} y anio_nacimiento = {self.anio_nacimiento}")
        else: 
            print(f"Persona encontrada para nombre_completo = {self.nombre_completo} y anio_nacimiento = {self.anio_nacimiento}, con id {row_existente.iloc[0]['id']}, genero {row_existente.iloc[0]['Gender']} y zip code {row_existente.iloc[0]['Zip Code']}. Se borrará")
            df_personas = df_personas[df_personas['id'] != row_existente.iloc[0]['id']]
        return df_personas
    
    @classmethod
    def get_stats(cls, df_personas, anios=None,):
        """
        # Este class method imprime una serie de estadísticas calculadas sobre los resultados de una consulta al DataFrame df_personas. 
        # Las estadísticas se realizarán sobre las filas que cumplan con los requisitos de:
        # anios: [desde_año, hasta_año]
        # Las estadísticas son:
        # - Cantidad de personas por año de nacimiento y Género. 
        # - Cantidad total de personas.
        """
        from matplotlib import pyplot as plt

        df_personas = Persona.get_from_df(df_personas, anios=anios)

        # cantidad total de personas
        cantidad_personas = len(df_personas)
        print(f"Cantidad de personas: {cantidad_personas}")

        # Cantidad de personas por año de nacimiento y Género. 

        personas_por_anio_nacimiento = df_personas.groupby(df_personas['year of birth']).size()
        plt.bar(personas_por_anio_nacimiento.index, personas_por_anio_nacimiento.values)
        plt.xlabel('Anio nacimiento')
        plt.ylabel('Numero de personas')
        plt.title(f'Numero de personas por anio de nacimiento para anios={anios}')
        # hacer que crezca de a enteros
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MultipleLocator(base=1))
        plt.show()

        personas_por_genero = df_personas.groupby(df_personas['Gender']).size()
        plt.bar(personas_por_genero.index, personas_por_genero.values)
        plt.xlabel('Anio nacimiento')
        plt.ylabel('Numero de personas')
        plt.title(f'Numero de personas por genero para anios={anios}')
        # hacer que crezca de a enteros
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MultipleLocator(base=1))
        plt.show()
    
# python -W ignore persona.py
if __name__ == '__main__':
    # Cargar CSV a un dataframe
    df_personas = Persona.create_df_from_csv(filename="datasets/personas.csv")

    print(f"Probando nueva persona que no existía, actual count: {len(df_personas)}")
    persona1 = Persona("Ilan Rosenfeld", 1993, "M", 1900)
    df_personas = persona1.write_df(df_personas)
    print(f"Nuevo count: {len(df_personas)}")
    print("--------------")

    print("Probando persona ya existente (Robert Stanley), Overwrite False. Persona actual:")
    persona2 = Persona("Robert Stanley", 1974, "F", "12345")
    print(Persona.get_from_df(df_personas, nombre_completo=persona2.nombre_completo, anios=[persona2.anio_nacimiento, persona2.anio_nacimiento]))
    df_personas = persona2.write_df(df_personas)
    print("Persona se mantiene igual:")
    print(Persona.get_from_df(df_personas, id=[1]))
    print("--------------")
    
    print("Probando persona ya existente (Robert Stanley), Overwrite True. Persona actual:")
    print(Persona.get_from_df(df_personas, id=[1]))
    df_personas = persona2.write_df(df_personas, overwrite=True)
    print("Objeto actualizado:")
    print(Persona.get_from_df(df_personas, id=[1]))
    print("--------------")

    print(f"Probando delete con combinacion no existente, actual count: {len(df_personas)}")
    persona3 = Persona("Ficticious Person", 2001, "F", "44321")
    df_personas = persona3.remove_from_df(df_personas)
    print(f"Nuevo count: {len(df_personas)}")
    print("--------------")

    print(f"Probando delete con combinacion existente, actual count: {len(df_personas)}")
    persona4 = Persona("Janice Mccullough", 1965, "F", "15213")
    df_personas = persona4.remove_from_df(df_personas)
    print(f"Nuevo count: {len(df_personas)}")
    print("--------------")

    print("Probando get general stats")
    print(Persona.get_stats(df_personas))
    print("--------------")

    print("Probando get stats entre 1990 y 1992")
    print(Persona.get_stats(df_personas, anios=[1980,1992]))
    print("--------------")