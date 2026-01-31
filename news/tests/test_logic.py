from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News

User = get_user_model()


class TestCommentCreation(TestCase):
    COMMENT_TEXT = 'Текст комментария'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.url = reverse('news:detail', args=(cls.news.id,))
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.COMMENT_TEXT}

    def test_anonymous_user_cant_create_comment(self):
        self.client.post(self.url, data=self.form_data)
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, 0)

    def test_user_can_create_comment(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{self.url}#comments')
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, 1)
        comment = Comment.objects.get()
        self.assertEqual(comment.text, self.COMMENT_TEXT)
        self.assertEqual(comment.news, self.news)
        self.assertEqual(comment.author, self.user)
