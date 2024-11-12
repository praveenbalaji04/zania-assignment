import json
import logging

from core.open_ai_wrapper import get_openai_response

logger = logging.getLogger(__name__)


class JsonHandler:

    @classmethod
    def parse(cls, json_data):
        loaded_data = json.loads(json_data)
        logger.info("[JSON Handler] - questions to OpenAI: %s", loaded_data)
        response = get_openai_response(loaded_data)
        return response


class PdfHandler:

    @classmethod
    def parse(cls, pdf_file):
        first_page = pdf_file.pages[0]  # assuming questions are in first page
        page_contents = first_page.extract_text()

        questions = page_contents.split("\n")
        questions = [valid_question.strip() for valid_question in questions if len(valid_question) > 0]
        logger.info("[PDF Handler] - questions to OpenAI: %s", questions)
        response = get_openai_response(questions)
        return response
