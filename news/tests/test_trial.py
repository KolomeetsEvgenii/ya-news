# news/tests/test_trial.py
from unittest import skip

from django.test import TestCase

from news.models import News


class TestNews(TestCase):
    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
        )

    @skip("временно отключили тест")
    def test_successful_creation(self):
        # При помощи обычного ORM-метода посчитаем количество записей в базе.
            news_count = News.objects.count()
            # Сравним полученное число с единицей.
            self.assertEqual(news_count, 1)

    @skip("временно отключили тест")
    def test_title(self):
        # Сравним свойство объекта и ожидаемое значение.
        self.assertEqual(self.news.title, self.TITLE)


class Test(TestCase):

    @skip("временно отключили тест")
    def test_example_success(self):
        self.assertTrue(True)  # Этот тест всегда будет проходить успешно.


class YetAnotherTest(TestCase):

    @skip("временно отключили тест")
    def test_example_fails(self):
        self.assertTrue(False)  # Этот тест всегда будет проваливаться.
