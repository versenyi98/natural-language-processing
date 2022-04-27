from dis import dis
from glob import glob
from typing import Optional, Dict, Text, Any

import numpy as np

from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

from unidecode import unidecode

import os
print(os.getcwd())

# BERT
import torch
from transformers import BertTokenizerFast, BertForSequenceClassification

tokenizer = BertTokenizerFast.from_pretrained('SZTAKI-HLT/hubert-base-cc')

model = BertForSequenceClassification.from_pretrained(
    'SZTAKI-HLT/hubert-base-cc',
    num_labels = 4,
    output_attentions=False,
    output_hidden_states=False   
)

model.load_state_dict(torch.load('../.model_storage/BERT/model_SZTAKI-HLT_hubert-base-cc_long_question.pth'))

target_names = ['Egészség', 'Szórakozás', 'Állatok', 'Számítástechnika']

prediction = None

def predict_category(question):
    encoded_question = tokenizer.encode_plus(
        question,
        max_length = 128,
        padding='max_length',
        truncation=True,
        return_token_type_ids=False
    )

    inputs = {
        'input_ids':      torch.tensor(encoded_question['input_ids']).unsqueeze(0),
        'attention_mask': torch.tensor(encoded_question['attention_mask']).unsqueeze(0),
        'labels':         torch.tensor(0).unsqueeze(0),
    }
        
    with torch.no_grad():
        outputs = model(**inputs)
        
    logits = outputs[1]

    pred = np.argmax(logits, axis=1).flatten().item()

    return target_names[pred]

# Elasticsearch
from elasticsearch import Elasticsearch

ES_QUERY_SIZE = 20
query_result = None
answer_idx = -1

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

def find_next_answer(index, question):
    global query_result
    global answer_idx

    if query_result == None:
        body = es_query(question)
        query_result = es.search(index=index, body=body)

    answer_idx += 1
    return query_result['hits']['hits'][answer_idx]['_source']['answer']

class CleanSlots(Action):
    def name(self) -> Text:
        return "clean_slots"

    def run(self, dispatcher, tracker, domain):
        global answer_idx
        global query_result

        answer_idx = -1
        query_result = None

        return [SlotSet("question", None), SlotSet("index_name", None), SlotSet("satisfied", None)]

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

        index_name = 'questions_'

        if intent == 'agree':
            global prediction
            index_name += unidecode(prediction.lower())
        elif intent == 'disagree':
            index_name += '*'

        return {"index_name": index_name}

class PredictCategory(Action):
    def name(self) -> Text:
        return "predict_category"
    
    def run(self, dispatcher, tracker, domain):
        global prediction
        prediction = predict_category(tracker.get_slot('question'))
        dispatcher.utter_message(f"Szerintem érdemes lenne csak a(z) '{prediction}' kategóriában keresni!\n")
        return []

class GiveAnswer(Action):
    def name(self) -> Text:
        return "give_answer"
    
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text=find_next_answer(tracker.get_slot('index_name'), tracker.get_slot('question')))
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
            dispatcher.utter_message(text="Örülök hogy segíthettem")
        else:
            # Finding next answer
            global answer_idx

            if answer_idx == ES_QUERY_SIZE - 1:
                satisfied = 'no'
                dispatcher.utter_message(text="Sajnálom hogy nem sikerült segíteni")
            else:
                dispatcher.utter_message(text=find_next_answer(tracker.get_slot('index_name'), tracker.get_slot('question')))

        return {"satisfied": satisfied}
