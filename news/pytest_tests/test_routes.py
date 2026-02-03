import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('id_for_args')),
        ('users:login', None),
        ('users:signup', None),
        ('users:logout', None),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)

    if name == 'users:logout':
        response = client.post(url)
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)
        return

    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('author_client'), HTTPStatus.OK),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client,
    expected_status,
    comment,
    name
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_redirect_for_anonymous_client(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)
    assertRedirects(response, expected_url)
