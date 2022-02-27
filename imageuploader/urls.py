from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('user-images/', views.UserImageListCreateAPIView.as_view(), name='user-images'),
    path('temporary-url/<int:iid>/<uuid:key>/', views.TemporaryURLView.as_view(), name='expirable-image-template')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
