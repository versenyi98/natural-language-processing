from typing import Optional, Dict, Text, Any, List

import random

from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

def find_next_answer():
    return "<< Next Answer >>"

class ValidateQuestionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_question_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain + ["question"]

    async def extract_question(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict
    ) -> Dict[Text, Any]:
        text_of_last_user_message = tracker.latest_message.get("text")
        return {"question": text_of_last_user_message}

class ValidateIndexName(FormValidationAction):
    def name(self) -> Text:
        return "validate_index_name_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain + ["index_name"]

    async def extract_index_name(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict
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
        dispatcher.utter_message(text=find_next_answer())
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
            satisfied = slot_value
        else:
            dispatcher.utter_message(text=find_next_answer())

        return {"satisfied": satisfied}
