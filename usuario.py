from persona import Persona
import pandas as pd
from datetime import datetime

class Usuario(Persona):

    def __init__(self, id, fecha_nacimiento, genero, codigo_postal, ocupacion, fecha_alta):
        super().__init__(id, fecha_nacimiento, genero, codigo_postal)
        self.ocupacion = ocupacion
        self.fecha_alta = fecha_alta
    
    @classmethod
    def create_df_from_csv(cls, filename):
        """
        Crea un dataframe de usuarios a partir de un csv
        """
        df_usuarios = pd.read_csv(filename)
        return df_usuarios

    def class_instance_to_df_row(self):
        """
        Transforma una instancia de la clase a un Dataframe row de pandas
        """
        user_as_dict = {'id': self.id, 'Occupation': self.ocupacion, 'Active Since': self.fecha_alta}
        return pd.DataFrame([user_as_dict])
    
    @classmethod
    def get_from_df(cls, df_users, df_personas, id=None, ocupaciones=None, fechas_alta=None, anios=None):
        """
        Este class method devuelve una lista de objetos 'Usuario' buscando por:
        # id: id --> se considera que se pasa un único id
        # ocupaciones --> lista de ocupaciones
        # fechas_alta --> [desde_año, hasta_año]
        """

        if id:
            df_users = df_users.query('id == ' + str(id))
        if ocupaciones:
            logical_disjunction = " or ".join(list(map(lambda occ: f"Occupation == {occ}", ocupaciones)))
            df_users = df_users.query(logical_disjunction)
        if fechas_alta:
            df_users = df_users.loc[(df_personas['Active Since'] >= fechas_alta[0]) & (df_personas['Active Since'] <= fechas_alta[1])]
        if anios:
            df_merged = pd.merge(df_users, df_personas, on='id')
            df_users = df_merged.loc[(df_merged['year of birth'] >= anios[0]) & (df_merged['year of birth'] <= anios[1])]
        return df_users

    def write_df(self, df_personas, df_users, overwrite = False):
        """
        Este método recibe el dataframe de users y el de personas.
        # Si la persona ya existe, valida si el user existe, si es asi lo reemplaza en base a overwrite, sino, lo crea. También actualiza persona
        # Si la persona no existía, crea tanto a la persona como al user
        """

        # creo una instancia de Persona a partir de los datos de Usuario
        persona_del_user = Persona(self.nombre_completo, self.anio_nacimiento, self.genero, self.codigo_postal)
        # invoco al write de persona, que creara a la misma si no existe, o actualizará si hiciera falta
        df_personas = persona_del_user.write_df(df_personas, overwrite=overwrite)
        # obtengo la persona antigua/nueva para quedarme con el id
        persona_existente = Persona.get_from_df(df_personas, nombre_completo=self.nombre_completo, anios=[self.anio_nacimiento, self.anio_nacimiento])

        self.id = persona_existente.iloc[0]['id']
        # reviso si el usuario ya existía para la persona, sino, lo creo, si si, actualizo en base a Overwrite
        user_existente = Usuario.get_from_df(df_users, df_personas, id = self.id)
        if user_existente.empty:
            # si no existía el user para el id de persona, lo creo
            print(f"No existía user para el id persona {self.id}, agregandolo con id {self.id}")
            df_users = pd.concat([df_users, self.class_instance_to_df_row()], ignore_index=True)
        else:
            if overwrite:
                print(f"Ya existia el user con id {self.id}, overwrite=True asi que se actualizará ocupacion y fecha alta en usuario")
                df_users.loc[df_users['id'] == self.id] = self.class_instance_to_df_row().values.tolist()[0]
            else:
                print(f"Error: Ya existia el user con id {self.id} y overwrite=False")
        return df_personas, df_users


    def remove_from_df(self, df_users):
        """
        Borra del DataFrame el objeto contenido en esta clase.
        obtengo la persona primero para conocer el id
        """
        persona_existente = Persona.get_from_df(df_personas, nombre_completo=self.nombre_completo, anios=[self.anio_nacimiento, self.anio_nacimiento])
        if persona_existente.empty:
            print(f"Error: No existe una persona con nombre_completo = {self.nombre_completo} y anio_nacimiento = {self.anio_nacimiento}, entonces tampoco existirá un user asociado")
        else:
            self.id = persona_existente.iloc[0]['id']
            user_existente = Usuario.get_from_df(df_users, df_personas, id=persona_existente.iloc[0]['id'])
            if user_existente.empty:
                print(f"Error: Si bien existe la persona con id {self.id}, no existe un usuario asociado")
            else: 
                print(f"A borrar user con  nombre_completo = {self.nombre_completo} y anio_nacimiento = {self.anio_nacimiento}, id {user_existente.iloc[0]['id']}")
                df_users = df_users[df_users['id'] != user_existente.iloc[0]['id']]
        return df_users

    @classmethod
    def get_stats(cls, df_users, anios=None):
        """
        # Este class method imprime una serie de estadísticas calculadas sobre los resultados de una consulta al DataFrame df_users. 
        # Las estadísticas se realizarán sobre las filas que cumplan con los requisitos de:
        # anios: [desde_año, hasta_año]
        # Las estadísticas son:
        # - Cantidad de usuarios por Ocupación/Año de Nacimiento.
        # - Cantidad total de usuarios.
        """
        from matplotlib import pyplot as plt

        df_users = Usuario.get_from_df(df_users, df_personas, anios=anios)

        # cantidad total de usuarios
        cantidad_users = len(df_personas)
        print(f"Cantidad de usuarios: {cantidad_users}")

        # Cantidad de usuarios por ocupación y año de nacimiento. 

        usuarios_por_ocupacion = df_users.groupby(df_users['Occupation']).size()
        plt.bar(usuarios_por_ocupacion.index, usuarios_por_ocupacion.values)
        plt.xlabel('Occupation')
        plt.ylabel('Numero de usuarios')
        plt.title(f'Numero de usuarios por ocupacion para anios={anios}')
        # hacer que crezca de a enteros
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MultipleLocator(base=1))
        plt.show()

        usuarios_por_anio_nacimiento = df_users.groupby(df_personas['year of birth']).size()
        plt.bar(usuarios_por_anio_nacimiento.index, usuarios_por_anio_nacimiento.values)
        plt.xlabel('Anio nacimiento')
        plt.ylabel('Numero de usuarios')
        plt.title(f'Numero de usuarios por anio de nacimiento para anios={anios}')
        # hacer que crezca de a enteros
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MultipleLocator(base=1))
        plt.show()
    

# python -W ignore usuario.py
if __name__ == '__main__':
    # Cargar CSV a un dataframe
    df_users = Usuario.create_df_from_csv(filename="datasets/usuarios.csv")
    df_personas = Persona.create_df_from_csv(filename="datasets/personas.csv")
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Probando nueva persona que no existía, actual count personas: {len(df_personas)}, actual count users: {len(df_users)}")
    user1 = Usuario("Fake Student", 1993, "M", 1900, "scientist", current_timestamp)
    df_personas, df_users = user1.write_df(df_personas, df_users)
    print(f"Nuevo count personas: {len(df_personas)}, nuevo count users: {len(df_users)}")
    print("--------------")
    
    
    print("Probando persona y usuario ya existentes, Overwrite False.")
    user2 = Usuario("Robert Stanley", 1974, "F", "12345", "scientist", current_timestamp)
    print("persona actual: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=user2.nombre_completo, anios=[user2.anio_nacimiento,user2.anio_nacimiento])
    print(persona_actual)
    print("usuario actual: ")
    print(Usuario.get_from_df(df_users, df_personas, id=persona_actual.iloc[0]['id']))
    df_personas, df_users = user2.write_df(df_personas, df_users)
    print(f"Nuevo count personas: {len(df_personas)}, nuevo count users: {len(df_users)}")
    print("--------------")

    print("Probando persona y usuario ya existentes, Overwrite True.")
    print("persona actual: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=user2.nombre_completo, anios=[user2.anio_nacimiento,user2.anio_nacimiento])
    print(persona_actual)
    print("usuario actual: ")
    print(Usuario.get_from_df(df_users, df_personas, id=persona_actual.iloc[0]['id']))
    df_personas, df_users = user2.write_df(df_personas, df_users, overwrite=True)
    print("nueva persona: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=user2.nombre_completo, anios=[user2.anio_nacimiento,user2.anio_nacimiento])
    print(persona_actual)
    print("nuevo usuario: ")
    print(Usuario.get_from_df(df_users, df_personas, id=persona_actual.iloc[0]['id']))
    print(f"Nuevo count personas: {len(df_personas)}, nuevo count users: {len(df_users)}")
    print("--------------")
    
    print("Agregando a John Doe para probar el siguiente caso de uso")
    persona_sin_user = Persona("John Doe", 1970, "M", 4353)
    df_personas = persona_sin_user.write_df(df_personas)
    print("--------------")

    print("Probando write con persona ya existente pero no el usuario, Overwrite True.")
    user_de_persona_sin_user = Usuario("John Doe", 1970, "M", 4353, "scientist", current_timestamp)
    print("persona actual: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=persona_sin_user.nombre_completo, anios=[persona_sin_user.anio_nacimiento,persona_sin_user.anio_nacimiento])
    print(persona_actual)
    print("usuario actual: ")
    print(Usuario.get_from_df(df_users, df_personas, id=persona_actual.iloc[0]['id']))
    df_personas, df_users = user_de_persona_sin_user.write_df(df_personas, df_users, overwrite=True)
    print("misma persona: ")
    persona_actual = Persona.get_from_df(df_personas, nombre_completo=persona_sin_user.nombre_completo, anios=[persona_sin_user.anio_nacimiento,persona_sin_user.anio_nacimiento])
    print(persona_actual)
    print("nuevo usuario: ")
    print(Usuario.get_from_df(df_users, df_personas, id=persona_actual.iloc[0]['id']))
    print(f"Nuevo count personas: {len(df_personas)}, nuevo count users: {len(df_users)}")
    print("--------------")

    print(f"Probando delete con persona no existente, actual count: {len(df_users)}")
    user3 = Usuario("Ficticious Person", 2001, "F", "44321","educator",current_timestamp)
    df_users = user3.remove_from_df(df_users)
    print(f"Nuevo count: {len(df_users)}")
    print("--------------")

    print("Agregando a Fake User para probar el siguiente caso de uso")
    persona_sin_user_2 = Persona("Fake User", 1955, "M", 6789)
    df_personas = persona_sin_user_2.write_df(df_personas)
    print("--------------")

    print(f"Probando delete con persona existente, pero sin user, actual count: {len(df_users)}")
    user4 = Usuario("Fake User", 1955, "M", 6789,"educator",current_timestamp)
    df_users = user4.remove_from_df(df_users)
    print(f"Nuevo count: {len(df_users)}")
    print("--------------")

    print(f"Probando delete con persona existente, y también user, actual count: {len(df_users)}")
    df_users = user2.remove_from_df(df_users)
    print(f"Nuevo count: {len(df_users)}")
    print("--------------")

    print("Probando get general stats")
    print(Usuario.get_stats(df_users))
    print("--------------")

    print("Probando get stats entre 1990 y 1992")
    print(Usuario.get_stats(df_users, anios=[1980,1992]))
    print("--------------")