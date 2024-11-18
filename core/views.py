import logging
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ValidationError

from rest_framework import status
from core.helpers import JsonHandler, PdfHandler
from core import pizza_data, pizza_v3

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


class CreateOrder(APIView):

    def create_new_order(self, data):
        from random import randint
        """
        order_details
        
        """
        # TODO this should be a model
        order = {
            "id": randint(1, 100000),
            "order_detail": data.get("order_detail"),
            "price": data.get("total_price")
        }
        # order = Order.objects.create(
        #     order_detail=data.get("order_detail"),
        #     prize=data.get("price")
        # )
        return order

    def post(self, request):
        """
        payload: [
            {
                'id': 1,
                'quantity': 2 
            },
            {
                'id': 3,
                'quantity': 5
            }
        ]
        """

        """Place an order for pizzas using /order endpoint and return total final price and an order id"""
        """
        order_id : int
        order details : input from user
        created_at : 
        waiting_time:
        prize: int
        """

        missing_pizzas = []
        total_price = 0
        response = {}
        valid_order_detail = {}
        for value in request.data:
            required_id = value.get("id")
            pizza_detail = pizza_v3.get(str(required_id))

            if not pizza_detail:
                missing_pizzas.append(str(required_id))
                continue

            price = pizza_detail.get("price") # float value
            total_price += price * value.get("quantity")
            valid_order_detail[value.get("id")] = {"quantity": value.get("quantity"), "price": price * value.get("quantity")}

        data_payload = {"order_detail": valid_order_detail, "total_price": total_price}
        order_detail = self.create_new_order(data_payload)

        # TODO: add serializer, add detail order information ( i.e pizza detail and order information and pricing of each)
        response["order_id"] = order_detail.get("id")
        response["total_price"] = order_detail.get("price")
        if missing_pizzas:
            response["error"] = {"missing pizza ids": missing_pizzas}

        return Response({"data": response})


class GetPizzaMenu(APIView):

    def get(self, request):
        name = request.query_params.get("name")
        if not name:
            raise ValidationError({"error": "invalid name"})
        """
        response: {
            "id": 1,
            "name": "Margherita",
            "size": "Medium",
            "price": 8.99,
            "toppings": ["tomato sauce", "mozzarella", "basil"]
        }
        """

        for pizza_dict in pizza_data:
            if pizza_dict.get("name").lower() == name.lower():
                return Response({"data": pizza_dict})

        return Response({"error": "no pizza found"}, status=status.HTTP_400_BAD_REQUEST)
