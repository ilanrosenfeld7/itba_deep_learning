from persona import Persona
import pandas as pd
from datetime import datetime

class Trabajador(Persona):
    def __init__(self, id, fecha_nacimiento, genero, codigo_postal, fecha_alta, puesto, categoría, horario_trabajo):
        super().__init__(id, fecha_nacimiento, genero, codigo_postal)
        self.fecha_alta = fecha_alta
        self.puesto = puesto
        self.categoría = categoría
        self.horario_trabajo = horario_trabajo

    @classmethod
    def create_df_from_csv(cls, filename):
        """
        Crea un dataframe de trabajadores a partir de un csv
        """
        df_trabajadores = pd.read_csv(filename)
        return df_trabajadores

    def class_instance_to_df_row(self):
        """
        Transforma una instancia de la clase a un Dataframe row de pandas
        """
        trabajador_as_dict = {'id': self.id, 'Start Date': self.fecha_alta, 'Position': self.puesto, 'Category': self.categoría, 'Working Hours': self.horario_trabajo}
        return pd.DataFrame([trabajador_as_dict])
    
    @classmethod
    def get_from_df(cls, df_trabajadores, id=None, fechas_alta=None, puestos=None, categories=None, horario_trabajo=None):
        """
        Este class method devuelve una lista de objetos 'Trabajador' buscando por:
        # id: id --> se considera que se pasa un único id
        # puestos --> puestos a buscar
        # fechas_alta --> [desde, hasta]
        # categorias --> categorias a buscar
        # horario_trabajo --> horario trabajo a buscar
        """

        if id:
            df_trabajadores = df_trabajadores.query('id == ' + str(id))
        if puestos:
            logical_disjunction = " or ".join(list(map(lambda puesto: f"Position == {puesto}", puestos)))
            df_trabajadores = df_trabajadores.query(logical_disjunction)
        if fechas_alta:
            df_trabajadores = df_trabajadores.loc[(df_trabajadores['Start Date'] >= fechas_alta[0]) & (df_trabajadores['Start Date'] <= fechas_alta[1])]
        if categories:
            logical_disjunction = " or ".join(list(map(lambda cat: f"Category == {cat}", categories)))
            df_trabajadores = df_trabajadores.query(logical_disjunction)
        if horario_trabajo:
            df_trabajadores = df_trabajadores.query('Working Hours == ' + str(horario_trabajo))
        return df_trabajadores

    
    def write_df(self, df_personas, df_trabajadores, overwrite = False):
        """
        Este método recibe el dataframe de trabajadores y el de personas.
        # Si la persona ya existe, valida si el trabajador existe, si es asi lo reemplaza en base a overwrite, sino, lo crea. También actualiza persona
        # Si la persona no existía, crea tanto a la persona como al trabajador
        """

        # creo una instancia de Persona a partir de los datos de Trabajador
        persona_del_trabajador = Persona(self.nombre_completo, self.anio_nacimiento, self.genero, self.codigo_postal)
        # invoco al write de persona, que creara a la misma si no existe, o actualizará si hiciera falta
        df_personas = persona_del_trabajador.write_df(df_personas, overwrite=overwrite)
        # obtengo la persona antigua/nueva para quedarme con el id
        persona_existente = Persona.get_from_df(df_personas, nombre_completo=self.nombre_completo, anios=[self.anio_nacimiento, self.anio_nacimiento])

        self.id = persona_existente.iloc[0]['id']
        # reviso si el trabajador ya existía para la persona, sino, lo creo, si si, actualizo en base a Overwrite
        trabajador_existente = Trabajador.get_from_df(df_trabajadores, id = self.id)
        if trabajador_existente.empty:
            # si no existía el trabajador para el id de persona, lo creo
            print(f"No existía trabajador para el id persona {self.id}, agregandolo con id {self.id}")
            df_trabajadores = pd.concat([df_trabajadores, self.class_instance_to_df_row()], ignore_index=True)
        else:
            if overwrite:
                print(f"Ya existia el trabajador con id {self.id}, overwrite=True asi que se actualizarán sus datos")
                df_trabajadores.loc[df_trabajadores['id'] == self.id, ['id', 'Start Date','Position','Category','Working Hours']] = self.class_instance_to_df_row().values.tolist()[0]
            else:
                print(f"Error: Ya existia el trabajador con id {self.id} y overwrite=False")
        return df_personas, df_trabajadores

    
    def remove_from_df(self, df_trabajadores):
        """
        Borra del DataFrame el objeto contenido en esta clase.
        obtengo la persona primero para conocer el id
        """
        persona_existente = Persona.get_from_df(df_personas, nombre_completo=self.nombre_completo, anios=[self.anio_nacimiento, self.anio_nacimiento])
        if persona_existente.empty:
            print(f"Error: No existe una persona con nombre_completo = {self.nombre_completo} y anio_nacimiento = {self.anio_nacimiento}, entonces tampoco existirá un trabajador asociado")
        else:
            self.id = persona_existente.iloc[0]['id']
            trabajador_existente = Trabajador.get_from_df(df_trabajadores, id=persona_existente.iloc[0]['id'])
            if trabajador_existente.empty:
                print(f"Error: Si bien existe la persona con id {self.id}, no existe un trabajador asociado")
            else: 
                print(f"A borrar trabajador con  nombre_completo = {self.nombre_completo} y anio_nacimiento = {self.anio_nacimiento}, id {trabajador_existente.iloc[0]['id']}")
                df_trabajadores = df_trabajadores[df_trabajadores['id'] != trabajador_existente.iloc[0]['id']]
        return df_trabajadores
    

# python -W ignore trabajador.py
if __name__ == '__main__':
    # Cargar CSV a un dataframe
    df_trabajadores = Trabajador.create_df_from_csv(filename="datasets/trabajadores.csv")
    df_personas = Persona.create_df_from_csv(filename="datasets/personas.csv")
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Probando nueva persona que no existía, actual count personas: {len(df_personas)}, actual count trabajadores: {len(df_trabajadores)}")
    trabajador1 = Trabajador("Charles Darwin", 1993, "M", 1900, "2023-06-07", "Tech Manager", "A", "9 - 18")
    df_personas, df_trabajadores = trabajador1.write_df(df_personas, df_trabajadores)
    print(f"Nuevo count personas: {len(df_personas)}, nuevo count trabajadores: {len(df_trabajadores)}")
    print("--------------")
    
    
    print("Probando persona y trabajador ya existentes, Overwrite False.")
    trabajador2 = Trabajador("Matthew Brentley",1977,"M",10309, "2023-06-08", "Developer", "A", "8 - 14")
    print("persona actual: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=trabajador2.nombre_completo, anios=[trabajador2.anio_nacimiento,trabajador2.anio_nacimiento])
    print(persona_actual)
    print("trabajador actual: ")
    print(Trabajador.get_from_df(df_trabajadores, id=persona_actual.iloc[0]['id']))
    df_personas, df_trabajadores = trabajador2.write_df(df_personas, df_trabajadores)
    print(f"Nuevo count personas: {len(df_personas)}, nuevo count trabajadores: {len(df_trabajadores)}")
    print("--------------")
    
    
    print("Probando persona y trabjador ya existentes, Overwrite True.")
    print("persona actual: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=trabajador2.nombre_completo, anios=[trabajador2.anio_nacimiento,trabajador2.anio_nacimiento])
    print(persona_actual)
    print("trabjador actual: ")
    print(Trabajador.get_from_df(df_trabajadores, id=persona_actual.iloc[0]['id']))
    df_personas, df_trabajadores = trabajador2.write_df(df_personas, df_trabajadores, overwrite=True)
    print("nueva persona: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=trabajador2.nombre_completo, anios=[trabajador2.anio_nacimiento,trabajador2.anio_nacimiento])
    print(persona_actual)
    print("nuevo trabjador: ")
    print(Trabajador.get_from_df(df_trabajadores, id=persona_actual.iloc[0]['id']))
    print(f"Nuevo count personas: {len(df_personas)}, nuevo count trabjadores: {len(df_trabajadores)}")
    print("--------------")
    
    print("Agregando a Juan Gomez para probar el siguiente caso de uso")
    persona_sin_trabajador = Persona("Juan Gomez", 1970, "M", 4353)
    df_personas = persona_sin_trabajador.write_df(df_personas)
    print("--------------")

    
    print("Probando write con persona ya existente pero no el trabajador, Overwrite True.")
    trabajador_de_persona_sin_trabajador = Trabajador("Juan Gomez", 1970, "M", 4353, "2023-06-10", "Tester", "C", "10 - 16")
    print("persona actual: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=persona_sin_trabajador.nombre_completo, anios=[persona_sin_trabajador.anio_nacimiento,persona_sin_trabajador.anio_nacimiento])
    print(persona_actual)
    print("trabajador actual: ")
    print(Trabajador.get_from_df(df_trabajadores, id=persona_actual.iloc[0]['id']))
    df_personas, df_trabajadores = trabajador_de_persona_sin_trabajador.write_df(df_personas, df_trabajadores, overwrite=True)
    print("misma persona: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=persona_sin_trabajador.nombre_completo, anios=[persona_sin_trabajador.anio_nacimiento,persona_sin_trabajador.anio_nacimiento])
    print(persona_actual)
    print("nuevo usuario: ")
    print(Trabajador.get_from_df(df_trabajadores, id=persona_actual.iloc[0]['id']))
    print(f"Nuevo count personas: {len(df_personas)}, nuevo count users: {len(df_trabajadores)}")
    print("--------------")

    print(f"Probando delete con persona no existente, actual count: {len(df_trabajadores)}")
    trabajador3 = Trabajador("Ficticious Person", 2001, "F", "44321","2023-06-10", "Tester", "C", "10 - 16")
    df_users = trabajador3.remove_from_df(df_trabajadores)
    print(f"Nuevo count: {len(df_trabajadores)}")
    print("--------------")

    print("Agregando a Fake Trabajador para probar el siguiente caso de uso")
    persona_sin_trabajador_2 = Persona("Fake Trabajador", 1955, "M", 6789)
    df_personas = persona_sin_trabajador_2.write_df(df_personas)
    print("--------------")

    print(f"Probando delete con persona existente, pero sin trabajador, actual count: {len(df_trabajadores)}")
    trabajador4 = Trabajador("Fake Trabajador", 1955, "M", 6789, "2023-06-15", "PM", "D", "10 - 18")
    df_trabajadores = trabajador4.remove_from_df(df_trabajadores)
    print(f"Nuevo count: {len(df_trabajadores)}")
    print("--------------")

    print(f"Probando delete con persona existente, y también trabajador, actual count: {len(df_trabajadores)}")
    df_trabajadores = trabajador2.remove_from_df(df_trabajadores)
    print(f"Nuevo count: {len(df_trabajadores)}")
    print("--------------")
  