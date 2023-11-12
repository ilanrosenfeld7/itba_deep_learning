# itba_deep_learning
TP integrador ITBA Deep Learning Ilan Rosenfeld

### Index

1. [Notebook](#notebook)

2. [Datasets](#datasets)

3. [Clases](#clases)

4. [Main](#main)

5. [TP Integrador 2: Sistema de recomendaciones](#tp-integrador-2-sistema-de-recomendaciones)

    5.1 [Set up de componentes](#set-up-de-componentes)
        
    5.1.1 [Docker y network](#docker-y-network)

    5.1.2 [Dependencias](#dependencias)

    5.1.3 [RDBMS (PostgreSQL)](#rdbms-postgresql)

    5.1.4 [pgAdmin](#pgadmin)

    5.1.5 [ORM (sqlalchemy)](#orm-sqlalchemy)

    5.1.6 [API de recomendaciones](#api-de-recomendaciones)

    5.1.7 [DB vectorial: instalar OpenSearch](#db-vectorial-instalar-opensearch)

    5.1.8 [Validación final](#validación-final)

    5.2 [Modelo de recomendación](#modelo-de-recomendación)

    5.2.1 [Generación de Embeddings](#generación-de-embeddings)
    
    5.2.2 [Entrenamiento del modelo](#entrenamiento-del-modelo)

    5.2.3 [Batch prediction](#batch-prediction)

    5.3 [Prueba de la API](#prueba-de-la-api)

    5.4 [Adicional: K-means](#adicional-kmeans)

    

    5.4 [Prueba de la API](#prueba-de-la-api)

## Notebook

Para interactuar con el código directamente y de manera más simple, se disponibilizó un Google Colab Notebook. El mismo se encuentra en el siguiente link: https://colab.research.google.com/drive/1iBOE7OfBtzEvm-mGtN1FyDboVVr7goR5?authuser=3#scrollTo=GOmXHWAOvku0

Preview (tiene menú incluido):
![Colab menu](assets/menu_notebook.png)

## Datasets

Dentro de [datasets/](datasets/) encontrarán los 5 csv originales de las entidades (personas, peliculas, scores, trabajadores, usuarios)

## Clases

Se definieron 5 clases, una por entidad, representadas por scripts .py:
1. [persona.py](persona.py)
2. [pelicula.py](pelicula.py)
3. [trabajador.py](trabajador.py)
4. [usuario.py](usuario.py)
5. [score.py](score.py)

Cada una de ellas posee ademas un main al final para ejecutar los distintos test cases de los métodos implementados. Ejemplo, para probar los métodos de persona, se debe correr el siguiente comando:

```
$ python -W ignore persona.py
```

## Main

La clase [main.py](main.py) contiene el código necesario para cargar todos los csv a dataframes y asimismo guardar los dataframes como csv

## TP Integrador 2: Sistema de recomendaciones

![HLA](assets/HLA.png)

### Set up de componentes

El sistema de recomendaciones se forma con 4 componentes principales:
1) **RDBMS**: base de datos relacional PostgreSQL con datos de peliculas, users, rankings, trabajadores y personas
2) **pgAdmin**: interfaz de usuario para interactuar con el RDBMS
3) **Base de datos vectorial**: Opensearch para almacenar embeddings de peliculas y usuarios
4) **API de recomendaciones**: API con Python + Flask para interactuar con los componentes anteriores y generar recomendaciones en base a requests del usuario

Todos estos componentes serán instanciados mediante docker. A continuación se describe como instalar cada uno de ellos.

#### Docker y network

A modo de poder continuar, instalar y setupear docker:

1) Instalar docker: dependiendo del OS instalar docker asociadamente
2) Crear network: servirá para permitir a los diferentes contenedores comunicarse:
```
$ docker network create itba_network
```

#### Dependencias

1) Actualizar su ambiente virtual (generalmente conda) con el nuevo requirements.txt

```
$ pip install -r requirements.txt
```

#### RDBMS (PostgreSQL)

Seguir los siguientes pasos para instalar la base de datos PostgreSQL local:

1) Pullear imagen de docker
```
$ docker pull postgres
```
2) Crear volumen para mantener persistencia al apagar y prender container
```
$ docker volume create pg_data
```

3) Crear folder pg_data
```
$ mkdir pg_data
```

4) Correr postgres container:
```
$ docker run --name postgres-container \
    --network itba_network \
    -e POSTGRES_PASSWORD=itba123 \
    -d \
    -p 5432:5432 \
    -v pg_data:/var/lib/postgresql/data postgres 
```

Explicación variables:
- _--name postgres-container_: Assigns a name to the container.
- _-e POSTGRES_PASSWORD=<password>_: Sets the PostgreSQL password.
- _-d_: Runs the container in detached mode.
- _-p 5432:5432_: Maps port 5432 from the container to your host machine (you can change the port as needed).
- _-v pg_data:/var/lib/postgresql/data_: Mounts the pg_data volume to the PostgreSQL container's data directory, allowing data persistence.

Si se apaga la computadora y se cae el container, correr de nuevo el comando, y ante el error _Error response from daemon: Conflict. The container name "/postgres-container" is already in use by container "XXX"_, hacer _docker start XXX_.

5) Validar quedó el contenedor corriendo con el siguiente comando de docker
```
$ docker ps
```
Deberías ver el contenedor de postgres con STATUS: Up

#### pgAdmin

1) Pullear y levantar imagen de docker de pgAdmin

Para poder acceder a la DB desde una interfaz gráfica (si aún no se pulleó la imagen, este comando la pullea la primera vez y luego la levanta)
```
$ docker run -p 80:80 \
    --name=pg_admin_container \
    --network=itba_network \
    -e 'PGADMIN_DEFAULT_EMAIL=user@domain.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=SuperSecret' \
    -e 'PGADMIN_CONFIG_ENHANCED_COOKIE_PROTECTION=True' \
    -e 'PGADMIN_CONFIG_LOGIN_BANNER="Authorised users only!"' \
    -e 'PGADMIN_CONFIG_CONSOLE_LOG_LEVEL=10' \
    -d dpage/pgadmin4
```

Mismo caso, ante error de _container is already in use_, hacer _docker start_. 

2) Entrar en el browser a localhost:80 y se abrirá la interfaz de pgAdmin, ingresar con las credenciales mencionadas arriba.

![pgAdmin main screen](assets/pg_admin.png)

8) Dentro de pgAdmin, ir a _Servers >> Create - Server Group_. Llamarlo _itba_. Luego darle click derecho a itba, _Register > Server_. Llamarlo _itba_server_. Ir al tab _Connection_, en _Host name/address_ colocar _postgres-container_, dejar _port:5432_, como username dejar _postgres_, y como password _itba123_.

![pgAdmin connection screen](assets/pg_admin_2.png)

9) Desplegar itba_db, en Databases dar click derecho, _Create > Database_, darle _itba_db_. Guardar

#### ORM (sqlalchemy)

1) Las clases pelicula, persona, score, trabajador, usuario y score fueron actualizadas con código sqlalchemy para definirse como tablas. Correr el script que las inyecta en el postgres:
```
$ python db_tables_creation.py
```
Darle click derecho Refresh a _itba_db_ en pgAdmin y validar que las tablas se crearon en _itba_db > Schemas > public > Tables_. En [useful_queries.sql](useful_queries.sql) están los SELECT de ejemplo para validar que la data existe.

_**Nota**: si se corre más de una vez podría dar error por repetir claves primarias. Ante algún error o update, borrar tablas desde pgAdmin y volver a correr esto_

![pgAdmin tables](assets/pg_admin_movies.png)

#### API de recomendaciones

1) Crear imagen de docker de la API. Correr el siguiente comando parado en itba_deep_learning/ (donde está el Dockerfile)

```
$ docker build -t recommendations_api:latest .
```

2) Correr container de docker (usar puerto 90, el 80 lo usará pgadmin)
```
$ docker run -d --net itba_network -p 90:90 recommendations_api 
```

3) Entrar a Swagger para probar la API: a modo de mejorar la usabilidad de la API, se integró la misma con swagger. Ir en el navegador a http://127.0.0.1:90/swagger y se debería ver lo siguiente:

![swagger](assets/swagger.png)

4) Probar endpoint de health con try it out, debería devolverse un 200 OK

![swagger](assets/swagger_health.png)
![swagger](assets/swagger_health_2.png)

#### DB vectorial: instalar OpenSearch

1) Pullear imagen de docker
```
$ docker pull opensearchproject/opensearch
```

2) Crear folder vector_db (fuera del folder clonado del repo) para mantener la data y correr el contenedor con la DB
```
$ mkdir vector_db
$ cd vector_db
$ docker run -p 9200:9200 -p 9600:9600 --net itba_network -e "discovery.type=single-node" --name opensearch-node -v vector_db:/usr/share/opensearch/data -d opensearchproject/opensearch:latest
```

3) Test it's up
```
$ curl -X GET "https://localhost:9200/_cat/nodes?v" -ku admin:admin
```
![swagger](assets/opensearch_1.png)

4) Create itba_movies collection
```
$ curl -XPUT -H "Content-Type: application/json" "https://localhost:9200/itba_movies" -ku admin:admin
```

5) Validate it was created
```
$ curl -XGET "https://localhost:9200/_cat/indices?v"  -ku admin:admin
```
![swagger](assets/opensearch_2.png)

#### Validación final

Tras levantar todos los containers, así debería verse el resultado del comando $ docker ps:

![docker_ps](assets/docker_ps.png)

### Modelo de recomendación

En esta sección, se generarán los embeddings de las movies y users, se entrenará al modelo, y se generarán predicciones de manera batch

#### Generación de Embeddings

***A actualizar por Gaspar para usar su código y guardar sus embeddings***

Se deben generar los embeddings de las movies y users y persistir en la DB vectorial. En [embeddings_generator.py](./embeddings_generator.py) hay código ejemplo de import de OpenSearch, conexión con la DB vectorial e inserción de movies.

#### Entrenamiento del modelo

***A updatear por Gaspar para usar su código y entrenar modelo***

Dejar código en [model_training_and_batch_prediction.py](./model_training_and_batch_prediction.py)  y entrenar modelo

#### Batch prediction

***A correr por Gaspar para usar su modelo y generar predicciones***

Correr modelo y generar predicciones en modo batch. Guardarlas en PostgreSQL en tabla de Score (se espera el schema original, si se cambia, revisar cambios necesarios)

![swagger](assets/score_schema.png)

### Prueba de la API

Probar la API desde swagger (localhost:90/swagger) insertando user o movie id y k:

![swagger_recommendations](assets/swagger_recommendations.png)

![swagger_similar_movies](assets/swagger_similar_movies.png)

### Adicional: Kmeans

Puntos extra: Agrupar los usuarios utilizando el algoritmo de Kmeans (implementado en OpenSearch). Describir cada cluster encontrado.

