import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']

    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, many_comments):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)

    assert 'news' in response.context
    news_object = response.context['news']

    comments_queryset = news_object.comment_set.all()
    comment_timestamps = [comment.created for comment in comments_queryset]

    expected_timestamps = sorted(comment_timestamps)
    assert comment_timestamps == expected_timestamps


def test_anonymous_client_has_no_form(client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)

    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = author_client.get(detail_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
