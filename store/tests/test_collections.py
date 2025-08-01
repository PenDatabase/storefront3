# test behaviors not implementation
# tests should have a single responsibility
# the less our test know about our implementations the more accurate it is

from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework import status, test
from store.models import Collection
import pytest




@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post('/store/collections/', {'title': 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client):
        api_client.force_authenticate(user={})
        response = api_client.post('/store/collections/', {'title': 'a'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_and_data_is_invalid_returns_400(self, api_client):
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post('/store/collections/', {'title': ''})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_user_is_admin_and_data_is_valid_returns_201(self, api_client):
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post('/store/collections/', {'title': 'a'})
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client: test.APIClient):
        collection = baker.make(Collection)
        
        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": collection.title,
            "products_count": 0
        }

    def test_if_collection_not_exists_returns_404(self, api_client: test.APIClient):
        response = api_client.get('/store/collections/0/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.test
class TestListCollections:
    def test_if_collection_exists_returns_200(self, api_client: test.APIClient):
        collection = baker.make(Collection, _quantity=10)
        
        response = api_client.get(f'/store/collections/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data[]