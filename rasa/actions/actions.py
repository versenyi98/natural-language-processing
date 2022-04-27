from glob import glob
from typing import Optional, Dict, Text, Any, List

import random

from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import ElasticsearchWarning

ES_QUERY_SIZE = 20
query_result = None
answer_idx = -1

# create elasticsearch client
es = Elasticsearch("http://localhost:9200")

def es_query(question):
    return {
        "size": ES_QUERY_SIZE,
        "query": {
            "match": {
                "long_question": {
                    "query": question,
                }
            }
        }
    }

def find_next_answer(question):
    global query_result
    global answer_idx

    if query_result == None:
        body = es_query(question)
        query_result = es.search(index="questions*", body=body)

    answer_idx += 1
    return query_result['hits']['hits'][answer_idx]['_source']['answer']

class ValidateIndexName(FormValidationAction):
    def name(self) -> Text:
        return "validate_index_name_form"

    def validate_index_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        intent = tracker.latest_message['intent'].get('name')

        index_name = None

        if intent == 'agree':
            index_name = 'question_category'
        elif intent == 'disagree':
            index_name = 'question_*'

        return {"index_name": index_name}

class CleanSlots(Action):
    def name(self) -> Text:
        return "clean_slots"

    def run(self, dispatcher, tracker, domain):
        global answer_idx
        global query_result

        answer_idx = -1
        query_result = None

        return [SlotSet("question", None), SlotSet("index_name", None), SlotSet("satisfied", None)]

class PredictCategory(Action):
    def name(self) -> Text:
        return "predict_category"
    
    def run(self, dispatcher, tracker, domain):
        categories = ["Számítástechnika", "Egészség", "Állatok", "Szórakozás"]

        predicion = random.choice(categories)

        dispatcher.utter_message(f"The predicted category is '{predicion}'\n")
        return []

class GiveAnswer(Action):
    def name(self) -> Text:
        return "give_answer"
    
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text=find_next_answer(tracker.get_slot('question')))
        return []

class ValidateSatisfied(FormValidationAction):
    def name(self) -> Text:
        return "validate_satisfied_form"

    def validate_satisfied(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        intent = tracker.latest_message['intent'].get('name')

        satisfied = None

        if intent == 'agree':
            satisfied = 'yes'
        else:
            # Finding next answer
            global answer_idx

            if answer_idx == ES_QUERY_SIZE - 1:
                satisfied = 'no'
            else:
                dispatcher.utter_message(text=find_next_answer(tracker.get_slot('question')))

        return {"satisfied": satisfied}
