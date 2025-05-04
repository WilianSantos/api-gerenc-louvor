from django.urls import path

from .views import ScaleHistoryViewSet

urlpatterns = [
    path("scale-history/", ScaleHistoryViewSet.as_view(), name="scale-history")
]
