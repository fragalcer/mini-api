# Create your views here.
import logging
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from imageuploader import manual_parameters as mp
from imageuploader.models import UserImage, TemporaryLink
from imageuploader.serializers import UserImageSerializer

logger = logging.getLogger(__name__)


class UserImageListCreateAPIView(LoginRequiredMixin, ListCreateAPIView):
    serializer_class = UserImageSerializer
    queryset = UserImage.objects.all()
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return UserImage.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[mp.seconds])
    def post(self, request, *args, **kwargs):
        seconds = request.data.get('seconds')
        if seconds:
            seconds = int(seconds)
            if seconds < 300 or seconds > 30000:
                return Response(
                    data=f"{seconds} is not a valid amount of time. Only between 300 and 30000 seconds is accepted.",
                    status=status.HTTP_400_BAD_REQUEST
                )
        response = super().post(request, *args, **kwargs)
        if not request.user.plan.value['original_image']:
            response.data.update({
                "image": None
            })
        response.data.update({
            "temporary_url": None
        })
        if seconds:
            if not request.user.plan.value['temporary_link']:
                return Response(
                    data="Only users with Enterprise account tier can provide an expiration date.",
                    status=status.HTTP_403_FORBIDDEN
                )
            image = UserImage.objects.get(id=response.data["id"])
            temporary_link = TemporaryLink.objects.create(
                image=image,
                expiry_date=timezone.now() + timedelta(seconds=seconds)
            )
            response.data.update({
                "temporary_url": f"{request.build_absolute_uri(reverse('expirable-image-template', args=[response.data['id'], temporary_link.key]))}"
            })
        return response


class TemporaryURLView(APIView):

    def get(self, request, *args, **kwargs):
        temporary_link = get_object_or_404(TemporaryLink, key=self.kwargs['key'])
        if temporary_link.is_expired:
            return Response(
                data="Your temporary link has expired.",
                status=status.HTTP_403_FORBIDDEN
            )
        return HttpResponse(temporary_link.image.image, content_type="image/png")
