from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import TimestampSigner
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from imageuploader.models import TemporaryLink


class ApiTestCase(TestCase):
    fixtures = ['plans/fixtures/initial_plans_fixture.yaml', ]

    def setUp(self) -> None:
        self.client = Client()
        self.api_client = APIClient()
        self.su = get_user_model().objects.create_superuser('super@example.com', 3, 'user')
        self.basic_user = get_user_model().objects.create_user('basic@example.com', 1, 'basic')
        self.premium_user = get_user_model().objects.create_user('premium@example.com', 2, 'premium')
        self.enterprise_user = get_user_model().objects.create_user('enterprise@example.com', 3, 'enterprise')
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        self.tomato_sauce_image = SimpleUploadedFile("tomato_sauce.jpg", bts.getvalue())

    def logout(self):
        self.client.post(reverse('logout'), {})

    def login_basic(self):
        self.logout()
        response = self.api_client.post(reverse('login'), {'username': 'basic@example.com', 'password': 'basic'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        return response

    def login_premium(self):
        self.logout()
        response = self.api_client.post(reverse('login'), {'username': 'premium@example.com', 'password': 'premium'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        return response

    def login_enterprise(self):
        self.logout()
        response = self.api_client.post(reverse('login'), {'username': 'enterprise@example.com', 'password': 'enterprise'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        return response

    def test_only_users_with_enterprise_account_tier_can_provide_expiration_date(self):
        self.login_basic()
        response = self.api_client.post(
            reverse('user-images'), {"image": self.tomato_sauce_image, "seconds": 300}, format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, 'Only users with Enterprise account tier can provide an expiration date.')

    def test_basic_plan(self):
        self.login_basic()
        response = self.api_client.post(
            reverse('user-images'), {"image": self.tomato_sauce_image}, format='multipart',
        )
        self.assertTrue('thumbnail_200' in response.data)
        self.assertFalse(response.data['image'])
        self.assertFalse('thumbnail_400' in response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_premium_plan(self):
        self.login_premium()
        response = self.api_client.post(
            reverse('user-images'), {"image": self.tomato_sauce_image}, format='multipart',
        )
        self.assertTrue('thumbnail_200' in response.data)
        self.assertTrue('image' in response.data)
        self.assertTrue('thumbnail_400' in response.data)
        self.assertTrue('temporary_url' not in response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_enterprise_plan(self):
        self.login_enterprise()
        response = self.api_client.post(
            reverse('user-images'), {"image": self.tomato_sauce_image, "seconds": 300}, format='multipart',
        )
        self.assertTrue('thumbnail_200' in response.data)
        self.assertTrue('image' in response.data)
        self.assertTrue('thumbnail_400' in response.data)
        self.assertTrue('temporary_url' in response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_validation_for_seconds(self):
        self.login_enterprise()
        response = self.api_client.post(
            reverse('user-images'), {"image": self.tomato_sauce_image, "seconds": 3}, format='multipart',
        )
        self.assertEqual(
            response.data[0].__str__(),
            '3 is not a valid amount of time. Only between 300 and 30000 seconds is accepted.'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expiration_for_link(self):
        self.login_enterprise()
        response_post = self.api_client.post(
            reverse('user-images'), {"image": self.tomato_sauce_image, "seconds": 300}, format='multipart',
        )
        last_temporary_link = TemporaryLink.objects.last()
        response_get = self.api_client.get(
            reverse('temporary-url', args=[last_temporary_link.key]),
            format='multipart'
        )
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        timestamp_signer = TimestampSigner()
        last_temporary_link.key = timestamp_signer.sign_object({"image": last_temporary_link.image.pk, "max_age": 0})
        last_temporary_link.save()
        response = self.api_client.get(
            reverse('temporary-url', args=[last_temporary_link.key]),
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, 'Your temporary link has expired.')
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
