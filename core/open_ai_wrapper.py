import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")


model = ChatOpenAI(model="gpt-4o-mini", api_key=OPEN_AI_API_KEY)


def get_openai_response(messages: list):
    # human_messages = [HumanMessage(msg) for msg in messages]  # not able to differentiate between messages
    response = {}
    for message in messages:
        open_ai_response = model.invoke([HumanMessage(message)])
        content = open_ai_response.to_json().get("kwargs").get("content")
        response[message] = content

    """
    : TODO:
    metadata from openAI: raise slack alert if token usage gone high or remaining tokens goes lower than specific threshold

    response_metadata={
        'token_usage': {
            'completion_tokens': 102,
            'prompt_tokens': 15,
            'total_tokens': 117,
            'completion_tokens_details': {
                'accepted_prediction_tokens': 0,
                'audio_tokens': 0,
                'reasoning_tokens': 0,
                'rejected_prediction_tokens': 0
        }
    }
    """
    return response
