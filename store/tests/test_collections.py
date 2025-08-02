# test behaviors not implementation
# tests should have a single responsibility
# the less our test know about our implementations the more accurate it is

from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status, test
from store.models import Collection
import pytest

User = get_user_model()


@pytest.fixture
def admin_user():
    return User(is_staff=True)


@pytest.fixture
def regular_user():
    return User()


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post('/store/collections/', {'title': 'Electronics'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client):
        api_client.force_authenticate(user={})

        response = api_client.post('/store/collections/', {'title': 'Electronics'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_and_data_is_invalid_returns_400(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)

        response = api_client.post('/store/collections/', {'title': ''})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_user_is_admin_and_data_is_valid_returns_201(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        
        response = api_client.post('/store/collections/', {'title': 'Electronics'})
        
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

@pytest.mark.django_db
class TestListCollections:
    def test_if_collections_returns_collections_list_and_200(self, api_client: test.APIClient):
        collections = baker.make(Collection, _quantity=10)
        
        response = api_client.get(f'/store/collections/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10

    def test_if_no_collections_returns_empty_list_and_200(self, api_client: test.APIClient):
        Collection.objects.all().delete()

        response = api_client.get(f'/store/collections/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0




@pytest.mark.django_db
class TestUpdateCollection:
    def test_if_collection_does_not_exist_returns_404(self, api_client: test.APIClient):
        api_client.force_authenticate(User(is_staff=True))

        response = api_client.put('/store/collections/999/', {'title': 'Updated Title'})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_user_is_anonymous_returns_401(self, api_client: test.APIClient):
        collection = baker.make(Collection)

        response = api_client.put(f'/store/collections/{collection.id}/', {'title': 'y'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client: test.APIClient):
        collection = baker.make(Collection)
        api_client.force_authenticate(User())

        response = api_client.put(f'/store/collections/{collection.id}/', {'title': 'y'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_and_data_is_invalid_returns_400(self, api_client: test.APIClient):
        collection = baker.make(Collection)
        api_client.force_authenticate(User(is_staff=True))

        response = api_client.put(f'/store/collections/{collection.id}/', {'bb': 'y'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_user_is_admin_and_data_is_valid_returns_200(self, api_client: test.APIClient):
        collection = baker.make(Collection)
        api_client.force_authenticate(User(is_staff=True))

        response = api_client.put(f'/store/collections/{collection.id}/', {'title': 'y'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": "y",
            "products_count": 0
        }

    def test_if_user_is_anonymous_cannot_partial_update_and_returns_401(self, api_client: test.APIClient):
        collection = baker.make(Collection)

        response = api_client.patch(f'/store/collections/{collection.id}/', {'title': 'y'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_cannot_partial_update_and_returns_403(self, api_client: test.APIClient):
        collection = baker.make(Collection)
        api_client.force_authenticate(User())
        
        response = api_client.patch(f'/store/collections/{collection.id}/', {'title': 'y'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_can_partial_update_and_returns_200(self, api_client: test.APIClient):
        collection = baker.make(Collection)
        api_client.force_authenticate(User(is_staff=True))

        response = api_client.patch(f'/store/collections/{collection.id}/', {'title': 'y'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": "y",
            "products_count": 0
        }




@pytest.mark.django_db
class TestDeleteCollection:
    def test_if_collection_does_not_exist_returns_404(self, api_client: test.APIClient):
        api_client.force_authenticate(User(is_staff=True))

        response = api_client.delete('/store/collections/999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_user_is_anonymous_cannot_delete_and_returns_401(self, api_client: test.APIClient):
        collection = baker.make(Collection)

        response = api_client.delete(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_cannot_delete_and_returns_403(self, api_client: test.APIClient):
        collection = baker.make(Collection)
        api_client.force_authenticate(User())

        response = api_client.delete(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_can_delete_and_returns_204(self, api_client: test.APIClient):
        collection = baker.make(Collection)
        api_client.force_authenticate(User(is_staff=True))

        response = api_client.delete(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT