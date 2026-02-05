import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, many_news, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']

    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, many_comments, detail_url):
    response = client.get(detail_url)

    assert 'news' in response.context
    news_object = response.context['news']

    comments_queryset = news_object.comment_set.all()
    comment_timestamps = [comment.created for comment in comments_queryset]

    assert comment_timestamps == sorted(comment_timestamps)


def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
