# itba_deep_learning
TP integrador ITBA Deep Learning Ilan Rosenfeld

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