# flake8: noqa
# news/tests/test_routes.py
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')

    def test_home_page(self):
        url = reverse('news:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_page(self):
        url = reverse('news:detail', args=(self.news.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
