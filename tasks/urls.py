from rest_framework.routers import SimpleRouter
from django.urls import path, include
from .views import TaskViewSet

router = SimpleRouter()
router.register(r"tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    path("", include(router.urls)),
]
