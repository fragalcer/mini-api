import logging

from django.core.signing import TimestampSigner
from django.urls import reverse
from rest_framework import serializers

from imageuploader.models import ImageUploaderUser, UserImage, TemporaryLink
from miniapi.settings import MIN_SECONDS_TEMPORARY_URL, MAX_SECONDS_TEMPORARY_URL

logger = logging.getLogger(__name__)


class ImageUploaderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUploaderUser
        fields = "__all__"


class UserImageBasicSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    thumbnail_200 = serializers.SerializerMethodField()

    class Meta:
        model = UserImage
        fields = ('id', 'user', 'image', 'thumbnail_200')
        read_only_fields = ('thumbnail_200', 'thumbnail_400')
        extra_kwargs = {'image': {'required': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in self.context and self.context['request'].method == 'GET':
            self.fields['image'] = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj and request.user.plan.value['original_image']:
            return obj.image.url

    def get_thumbnail_200(self, obj):
        request = self.context.get('request')
        if obj and request.user.plan.value['thumbnail_200']:
            return request.build_absolute_uri(obj.thumbnail_200.url)


class UserImagePremiumSerializer(UserImageBasicSerializer):
    thumbnail_400 = serializers.SerializerMethodField()

    class Meta(UserImageBasicSerializer.Meta):
        fields = ('id', 'user', 'image', 'thumbnail_200', 'thumbnail_400')

    def get_thumbnail_400(self, obj):
        request = self.context.get('request')
        if obj and request.user.plan.value['thumbnail_400']:
            return request.build_absolute_uri(obj.thumbnail_400.url)


class UserImageEnterpriseSerializer(UserImagePremiumSerializer):
    temporary_url = serializers.SerializerMethodField()
    seconds = serializers.SerializerMethodField()

    class Meta(UserImagePremiumSerializer.Meta):
        fields = ('id', 'user', 'image', 'thumbnail_200', 'thumbnail_400', 'temporary_url', 'seconds')
        read_only_fields = ('temporary_url',)

    def validate_seconds(self, seconds):
        if MIN_SECONDS_TEMPORARY_URL > seconds > MAX_SECONDS_TEMPORARY_URL:
            raise serializers.ValidationError(
                f"{seconds} is not a valid amount of time. Only between {MIN_SECONDS_TEMPORARY_URL} and "
                f"{MAX_SECONDS_TEMPORARY_URL} seconds is accepted."
            )
        return seconds

    def get_seconds(self, obj):
        if seconds := self.context.get("seconds"):
            seconds = int(seconds)
            if seconds < MIN_SECONDS_TEMPORARY_URL or seconds > MAX_SECONDS_TEMPORARY_URL:
                raise serializers.ValidationError(
                    f"{seconds} is not a valid amount of time. Only between {MIN_SECONDS_TEMPORARY_URL} and "
                    f"{MAX_SECONDS_TEMPORARY_URL} seconds is accepted."
                )
        return seconds

    def get_temporary_url(self, obj):
        if seconds := self.context.get("seconds"):
            request = self.context.get('request')
            timestamp_signer = TimestampSigner()
            temporary_link = TemporaryLink.objects.create(
                image=obj,
                key=timestamp_signer.sign_object({"image": obj.pk, "max_age": int(seconds)}),
            )
            return request.build_absolute_uri(reverse('temporary-url', args=[temporary_link.key]))
