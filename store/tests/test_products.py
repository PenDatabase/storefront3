from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status, test
from store.models import Collection, Product
import pytest

User = get_user_model()

@pytest.fixture
def admin_user():
    return User(is_staff=True)


@pytest.fixture
def regular_user():
    return User()


@pytest.fixture
def valid_product_data():
    """Helper to create valid product data with a collection"""
    collection = baker.make(Collection)
    product = baker.prepare(Product, collection=collection, inventory=50)
    
    # Filter out None values and ensure valid data
    data = {
        'title': product.title,
        'slug': product.slug,
        'unit_price': product.unit_price,
        'inventory': abs(product.inventory),  # Ensure positive inventory
        'collection': collection.id
    }
    
    # Only add description if it's not None
    if product.description:
        data['description'] = product.description
        
    return data


@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_is_anonymous_returns_401(self, api_client, valid_product_data):
        response = api_client.post('/store/products/', valid_product_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client, regular_user, valid_product_data):
        api_client.force_authenticate(user=regular_user)

        response = api_client.post('/store/products/', valid_product_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_and_data_is_invalid_returns_400(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        invalid_data = {
            'title': '',  # Invalid: empty title
            'unit_price': -5,  # Invalid: negative price
            'inventory': -1,  # Invalid: negative inventory
        }

        response = api_client.post('/store/products/', invalid_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
        assert 'unit_price' in response.data
        assert 'inventory' in response.data

    def test_if_user_is_admin_and_data_is_valid_returns_201(self, api_client, admin_user, valid_product_data):
        api_client.force_authenticate(user=admin_user)

        response = api_client.post('/store/products/', valid_product_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0
        assert response.data['title'] == valid_product_data['title']
        assert str(response.data['unit_price']) == str(valid_product_data['unit_price'])


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_returns_200(self, api_client: test.APIClient):
        product = baker.make(Product)
        
        response = api_client.get(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] > 0
        assert response.data['title'] == product.title
        assert response.data['unit_price'] == product.unit_price

    def test_if_product_not_exists_returns_404(self, api_client: test.APIClient):
        response = api_client.get('/store/products/0/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListProduct:
    def test_if_products_returns_products_list_and_200(self, api_client: test.APIClient):
        products = baker.make(Product, _quantity=10)
        
        response = api_client.get(f'/store/products/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10

    def test_if_no_products_returns_empty_list_and_200(self, api_client: test.APIClient):
        Product.objects.all().delete()

        response = api_client.get(f'/store/collections/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


# @pytest.mark.django_db
# class TestUpdateCollection:
#     def test_if_user_is_anonymous_cannot_update_and_returns_401(self, api_client: test.APIClient):
#         collection = baker.make(Collection)

#         response = api_client.put(f'/store/products/{collection.id}/', {'title': 'y'})

#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_if_user_is_not_admin_cannot_update_and_returns_401(self, api_client: test.APIClient):
#         collection = baker.make(Collection)
#         api_client.force_authenticate(User())

#         response = api_client.put(f'/store/products/{collection.id}/', {'title': 'y'})

#         assert response.status_code == status.HTTP_403_FORBIDDEN

#     def test_if_user_is_admin_can_update_and_returns_200(self, api_client: test.APIClient):
#         collection = baker.make(Collection)
#         api_client.force_authenticate(User(is_staff=True))

#         response = api_client.put(f'/store/products/{collection.id}/', {'title': 'y'})

#         assert response.status_code == status.HTTP_200_OK
#         assert response.data == {
#             "id": collection.id,
#             "title": "y",
#             "products_count": 0
#         }

#     def test_if_user_is_anonymous_cannot_partial_update_and_returns_401(self, api_client: test.APIClient):
#         collection = baker.make(Collection)

#         response = api_client.patch(f'/store/products/{collection.id}/', {'title': 'y'})

#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_if_user_is_not_admin_cannot_partial_update_and_returns_401(self, api_client: test.APIClient):
#         collection = baker.make(Collection)
#         api_client.force_authenticate(User())
        
#         response = api_client.put(f'/store/products/{collection.id}/', {'title': 'y'})

#         assert response.status_code == status.HTTP_403_FORBIDDEN

#     def test_if_user_is_admin_can_partial_update_and_returns_200(self, api_client: test.APIClient):
#         collection = baker.make(Collection)
#         api_client.force_authenticate(User(is_staff=True))

#         response = api_client.patch(f'/store/products/{collection.id}/', {'title': 'y'})

#         assert response.status_code == status.HTTP_200_OK
#         assert response.data == {
#             "id": collection.id,
#             "title": "y",
#             "products_count": 0
#         }


# @pytest.mark.django_db
# class TestDeleteCollection:
#     def test_if_user_is_anonymous_cannot_delete_and_returns_401(self, api_client: test.APIClient):
#         collection = baker.make(Collection)

#         response = api_client.delete(f'/store/products/{collection.id}/')

#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_if_user_is_not_admin_cannot_delete_and_returns_401(self, api_client: test.APIClient):
#         collection = baker.make(Collection)
#         api_client.force_authenticate(User())

#         response = api_client.delete(f'/store/products/{collection.id}/')

#         assert response.status_code == status.HTTP_403_FORBIDDEN

#     def test_if_user_is_admin_can_delete_and_returns_204(self, api_client: test.APIClient):
#         collection = baker.make(Collection)
#         api_client.force_authenticate(User(is_staff=True))

#         response = api_client.delete(f'/store/products/{collection.id}/')

#         assert response.status_code == status.HTTP_204_NO_CONTENT