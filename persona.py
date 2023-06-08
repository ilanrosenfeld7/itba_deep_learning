import pandas as pd
from datetime import datetime

class Persona:

    def __init__(self, nombre_completo, anio_nacimiento, genero, codigo_postal, id=None):
        self.id = id
        self.nombre_completo = nombre_completo
        self.anio_nacimiento = anio_nacimiento
        self.genero = genero
        self.codigo_postal = codigo_postal
    
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