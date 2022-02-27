import logging

from rest_framework import serializers

from imageuploader.models import ImageUploaderUser, UserImage

logger = logging.getLogger(__name__)


class ImageUploaderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUploaderUser
        fields = "__all__"


class UserImageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    thumbnail_200 = serializers.SerializerMethodField()
    thumbnail_400 = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in self.context and self.context['request'].method == 'GET':
            self.fields['image'] = serializers.SerializerMethodField()

    class Meta:
        model = UserImage
        fields = ('id', 'user', 'image', 'thumbnail_200', 'thumbnail_400')
        read_only_fields = ('thumbnail_200', 'thumbnail_400')
        extra_kwargs = {'image': {'required': True}}

    def get_image(self, obj):
        request = self.context.get('request')
        if obj and request.user.plan.value['original_image']:
            return obj.image.url

    def get_thumbnail_200(self, obj):
        request = self.context.get('request')
        if obj and request.user.plan.value['thumbnail_200']:
            return request.build_absolute_uri(obj.thumbnail_200.url)

    def get_thumbnail_400(self, obj):
        request = self.context.get('request')
        if obj and request.user.plan.value['thumbnail_400']:
            return request.build_absolute_uri(obj.thumbnail_400.url)
