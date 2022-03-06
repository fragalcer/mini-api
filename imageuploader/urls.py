from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('user-images/', views.UserImageListCreateAPIView.as_view(), name='user-images'),
    path('temporary-url/<path:key>/', views.TemporaryURLView.as_view(), name='temporary-url')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
