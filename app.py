from crypt import methods
from flask import Flask, render_template, redirect, url_for, request, flash
from elasticsearch import Elasticsearch
import pprint
import os,json

from flask.helpers import flash


path_to_txt = "requirements/"

es = Elasticsearch(HOST="http://localhost", PORT=9200)
es = Elasticsearch()

app = Flask(__name__)

def indexing():

    print("-- INDEXING -- ")
    with open("all_requirements.json", "r+") as json_file:
        
        json_data = json.load(json_file)

        temp = json_data

        for file_name in [file for file in os.listdir(path_to_txt) if file.endswith('.txt')]:
                    

            with open(path_to_txt + file_name) as text_file:

                textfile_as_string = text_file.read()
                requirements = textfile_as_string.split("-----------------------------------------------------------------------------------------------------------------------------")
                
                

                for single_req in requirements:
                    t = {"requirement" :single_req}
                    if t not in json_data["data"]:
                        json_data["data"].append(t)

                

                # print(requirements)
        
        json_file.seek(0)

        json.dump(json_data, json_file, indent = 5 )
    print("-- Finished idexing --")

    
    with open("all_requirements.json", "r") as json_file:

        json_data = json.load(json_file)

        count = 0

        for requirement in json_data["data"]:
            es.index(index="requirements", id=count, body=requirement)

            count+=1


def find(query_word):
    body = {

                "query": {
                    "multi_match" : {
                        "query" : str(query_word)
                        
                    }
                },
                "highlight" : {
                    "pre_tags" : [
                        "<b style='color:orange'>"],
                    "post_tags" : [
                        "</b>"
                    ],
                    # "tags_schema" : "styled",
                    "fields":{
                        "*":{}
                    }
                }
            }

    res = es.search(index="requirements", body=body)

    pprint.pprint(res)

    res_list = []

    for result in res["hits"]["hits"]:
        res_list.append(result["highlight"]["requirement"][0])
    
    return res_list


@app.route('/', methods= ["GET"])
def home():
    res_list = find("python")

    return render_template("index.html", results = res_list)

    

indexing()



if __name__ == '__main__':


    app.run(debug=True, port = 8000)