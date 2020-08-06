try:
    import elasticsearch
    from elasticsearch import Elasticsearch

    import pandas as pd
    import json
    from ast import literal_eval
    from tqdm import tqdm
    import datetime
    import os
    import sys

    import os
    # import tensorflow as tf
    # import tensorflow_hub as hub
    import numpy as np
    from elasticsearch import helpers
    print("Loaded  .. . . . . . . .")
except Exception as E:
    print("Some Modules are Missing {} ".format(e))

# ----------CHANGE ME -----------
global INDEX
global ENDPOINT
global  FILENAME
FILENAME = "final_project_1.csv"
ENDPOINT = "http://localhost:9200/"
INDEX = 'final_project'
$ --------------------------------

def generator(df2):
    for c, line in enumerate(df2):
        yield {
            '_index': INDEX,
            '_type': '_doc',
            '_id': c,
            '_source': {
                "name":line.get("name", ""),
                'brand':line.get('brand', ""),
                'categories':line.get('categories', ""),
                'primaryCategories':line.get('primaryCategories', ""),
                'name_vector':line.get('name_vector', ""),
                'categories_vector':line.get('categories_vector', ""),
                'imageURLs':line.get('imageURLs', '')
            }
        }
    raise StopIteration


def imageUploader(x):
    import ast
    tem = ast.literal_eval(x)
    return tem[:5]


def changemapping(x):
    import ast
    tem = ast.literal_eval(x)
    return tem



def runner():
    df  = pd.read_csv(FILENAME)
    df = df.drop(["Unnamed: 0", "Unnamed: 0.1"], axis=1)
    df['imageURLs']  = df['imageURLs'].apply(imageUploader)
    df['name_vector']  = df['name_vector'].apply(changemapping)
    df['categories_vector']  = df['categories_vector'].apply(changemapping)
    df.fillna("No Data")

    df2 = df.to_dict('records')
    es = Elasticsearch(timeout=600,hosts=ENDPOINT)

    try:
        res = helpers.bulk(es, generator(df2))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    runner()
