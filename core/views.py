import logging
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ValidationError

from core.helpers import JsonHandler, PdfHandler

from pypdf import PdfReader
from openpyxl import Workbook


logger = logging.getLogger(__name__)


#  better to add throttle to avoid DDoS
@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


class OpenAIAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        """
        payload:
        {
            "input_file": file,  refer questions.json /   zania.pdf for file format
            "response_type": str (supported type - excel)
        }

        output: {
            "data": {
                <question>: <open-ai-answer>,
                <question>: <open-ai-answer>,
        }
        """

        input_file = request.FILES.get("input_file")
        response_type = request.data.get("response_type")
        content_type = input_file.content_type

        logger.info("[OpenAI_API] received file with content type: %s", content_type)

        if content_type == "application/pdf":
            try:
                pdf_file = PdfReader(input_file)
            except Exception as e:
                logger.info("[OpenAI_API] error in reading pdf file. possibly corrupted file %s", str(e))
                raise ValidationError({"error": "error in reading pdf file. possibly corrupted file"})

            response = PdfHandler.parse(pdf_file)

        elif content_type == "application/json":
            response = JsonHandler.parse(input_file.read())

        else:
            raise ValidationError({"error": "Invalid file type"})

        if response_type == "excel":
            filename = "output.xlsx"
            book = Workbook()
            work_sheet = book.active
            for question, answer in response.items():
                work_sheet.append([question, answer])
            book.save(filename)

            return FileResponse(
                open(filename, "rb"),
                as_attachment=True,
                filename=filename,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        """
        sample API response
        {
            "data": {
                "What is the capital of France?": "The capital of France is Paris.",
                "What is the capital of Germany?": "The capital of Germany is Berlin.",
                "What is the capital of Spain": "The capital of Spain is Madrid."
            }
        }
        """

        # :TODO: add serializer for response.
        return Response({"data": response})
