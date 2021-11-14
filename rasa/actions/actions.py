import datetime as dt
from typing import Any, Text, Dict, List
from numpy.lib.npyio import save

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, Q

import numpy as np
import hu_core_ud_lg

import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('hungarian'))

es = Elasticsearch(HOST="localhost", PORT="9200")
nlp = hu_core_ud_lg.load()
INDEX_NAME = "questions"

saved_response = None
question = None
i = 0

def stop_word_filter(text):
    return " ". join([w for w in text if not w in stop_words])

def embed(sentence):
    doc = nlp(sentence)
    lemmatized = " ".join([w.lemma_.lower() for w in doc])
    doc = nlp(lemmatized)

    helper = [doc[idx].vector for idx in range(len(doc))]
    query_vector = np.add.reduce(helper) / len(doc)

    return query_vector

def create_script_query(question):
    return  {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, doc['short_question_vector']) + 1.0",
                        "params": {"query_vector": embed(stop_word_filter(question))}
                    }
                }
            }

def search(question):
    response = es.search(
        index = INDEX_NAME,
        body = {
            "size": 10,
            "query": create_script_query(question)
        }
    )

    return response

def rasa_answer(question, i):
    global saved_response
    if saved_response == None:
        saved_response = search(question)

    if i >= len(saved_response["hits"]["hits"]):
        return "Nincs több válasz!"

    return saved_response["hits"]["hits"][i]["_source"]["answer"]

class ActionGetTime(Action):

    def name(self) -> Text:
        return "action_get_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        global question
        global saved_response
        global i

        new_question = tracker.get_slot("question")

        if question != new_question:
            i = 0
            question = new_question
            saved_response = None

        answer = rasa_answer(question, i)

        i = i + 1

        dispatcher.utter_message(text=f"{answer}")

        return []