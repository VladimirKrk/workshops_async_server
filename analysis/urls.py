from django.urls import path
from .views import AnalyzeProductionView

urlpatterns = [
    # /analysis/analyze_workshop_production/
    path('analyze_workshop_production/', AnalyzeProductionView.as_view(), name='analyze_production'),
]