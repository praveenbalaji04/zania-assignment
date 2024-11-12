from django.urls import path

from core.views import (
    health_check,
    OpenAIAPIView,
)


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("open-ai/", OpenAIAPIView.as_view(), name="openai_api"),
]