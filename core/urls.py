from django.urls import path

from core.views import (
    health_check,
    OpenAIAPIView,
    GetPizzaMenu,
    CreateOrder,
)


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("open-ai/", OpenAIAPIView.as_view(), name="openai_api"),
    path("menu/", GetPizzaMenu.as_view(), name="pizza_menu"),
    path("order/", CreateOrder.as_view(), name="create-new-order"),
]