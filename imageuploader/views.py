# Create your views here.
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from imageuploader import manual_parameters as mp
from imageuploader.models import UserImage, TemporaryLink
from imageuploader.serializers import UserImageBasicSerializer, UserImageEnterpriseSerializer, \
    UserImagePremiumSerializer

logger = logging.getLogger(__name__)


class UserImageListCreateAPIView(ListCreateAPIView):
    queryset = UserImage.objects.all()
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Pass the "seconds" parameter to the serializer to validate:
        context.update({'seconds': self.request.data.get('seconds')})
        return context

    def get_serializer_class(self):
        if self.request.user.plan.name == 'Enterprise':
            return UserImageEnterpriseSerializer
        elif self.request.user.plan.name == 'Premium':
            return UserImagePremiumSerializer
        return UserImageBasicSerializer

    def get_queryset(self):
        return UserImage.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[mp.seconds])
    def post(self, request, *args, **kwargs):
        seconds = request.data.get('seconds')
        if seconds and not request.user.plan.value['temporary_link']:
            return Response(
                data="Only users with Enterprise account tier can provide an expiration date.",
                status=status.HTTP_403_FORBIDDEN
            )
        response = super().post(request, *args, **kwargs)
        if not request.user.plan.value['original_image']:
            response.data['image'] = None
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
