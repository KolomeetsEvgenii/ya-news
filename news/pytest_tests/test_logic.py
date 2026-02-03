import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}

    client.post(detail_url, data=form_data)

    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news):
    detail_url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}

    response = author_client.post(detail_url, data=form_data)

    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1

    created_comment = Comment.objects.get()
    assert created_comment.text == form_data['text']
    assert created_comment.news == news
    assert created_comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}

    response = author_client.post(detail_url, data=bad_words_data)

    # Должна вернуться страница с формой и ошибкой валидации
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']

    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, news, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    expected_redirect_url = reverse(
        'news:detail',
        args=(news.id,)
    ) + '#comments'

    response = author_client.delete(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))

    response = not_author_client.delete(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, news, comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    expected_redirect_url = reverse(
        'news:detail',
        args=(news.id,)
    ) + '#comments'
    form_data = {'text': 'Обновлённый комментарий'}

    response = author_client.post(edit_url, data=form_data)

    assertRedirects(response, expected_redirect_url)

    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Обновлённый комментарий'}
    original_text = comment.text

    response = not_author_client.post(edit_url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text == original_text
