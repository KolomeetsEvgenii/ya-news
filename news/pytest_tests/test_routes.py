import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'target_url',
    (
        lf('edit_url'),
        lf('delete_url'),
    ),
)
def test_redirects_for_anonymous_user(client, target_url, login_url):
    expected_url = f'{login_url}?next={target_url}'
    response = client.get(target_url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'client_fixture, target_url, expected_status',
    (
        (lf('client'), lf('home_url'), HTTPStatus.OK),
        (lf('client'), lf('detail_url'), HTTPStatus.OK),
        (lf('client'), lf('login_url'), HTTPStatus.OK),
        (lf('client'), lf('signup_url'), HTTPStatus.OK),

        (lf('author_client'), lf('edit_url'), HTTPStatus.OK),
        (lf('author_client'), lf('delete_url'), HTTPStatus.OK),
        (lf('not_author_client'), lf('edit_url'), HTTPStatus.NOT_FOUND),
        (lf('not_author_client'), lf('delete_url'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_for_users(
    client_fixture,
    target_url,
    expected_status
):
    response = client_fixture.get(target_url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'client_fixture',
    (
        lf('client'),
    ),
)
def test_logout_available_for_anonymous_user_has_no_side_effects(
    client_fixture,
    logout_url
):
    before = Comment.objects.count()
    response = client_fixture.post(logout_url)
    after = Comment.objects.count()

    assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)
    assert after == before
