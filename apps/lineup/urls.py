from django.urls import path

from .views import ScaleHistoryViewSet, SlideGeneratorView

urlpatterns = [
    path("scale-history/", ScaleHistoryViewSet.as_view(), name="scale-history"),
    path("slides-generator/", SlideGeneratorView.as_view(), name="generate-slides"),
]
