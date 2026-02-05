import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def many_comments(db, author, news):
    start_time = timezone.now()
    comments = []

    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = start_time + timedelta(days=index)
        comment.save(update_fields=('created',))
        comments.append(comment)

    return tuple(comments)


@pytest.fixture
def many_news(db):
    today = datetime.today()
    News.objects.bulk_create(
        [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index),
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )


@pytest.fixture
def author(db, django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(db, django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(db, author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий',
    )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))
