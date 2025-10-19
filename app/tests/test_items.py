import pytest
from httpx import AsyncClient, Response
from fastapi import status


@pytest.mark.asyncio
async def test_create_item(ac: AsyncClient):
    """
    Тест создания нового Item.
    """
    item_data = {
        "name": "Test Item",
        "description": "This is a test item.",
        "price": 19.99
    }
    response: Response = await ac.post("/api/v1/item/", json=item_data)

    assert response.status_code == status.HTTP_201_CREATED
    created_item = response.json()
    assert created_item["name"] == item_data["name"]
    assert created_item["description"] == item_data["description"]
    assert created_item["price"] == item_data["price"]
    assert "id" in created_item
    assert "created_at" in created_item
    assert "updated_at" in created_item


@pytest.mark.asyncio
async def test_get_items_empty(ac: AsyncClient):
    """
    Тест получения списка Item, когда база данных пуста.
    """
    response: Response = await ac.get("/api/v1/item/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_item_not_found(ac: AsyncClient):
    """
    Тест получения несуществующего Item.
    """
    response: Response = await ac.get("/api/v1/item/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}

# --- Далее можно добавить больше тестов ---

@pytest.mark.asyncio
async def test_create_and_get_item(ac: AsyncClient):
    """
    Тест создания и последующего получения Item по ID.
    """
    item_data = {
        "name": "Another Test Item",
        "description": "Description for another test item.",
        "price": 29.99
    }
    create_response = await ac.post("/api/v1/item/", json=item_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_item = create_response.json()

    get_response = await ac.get(f"/api/v1/item/{created_item['id']}")
    assert get_response.status_code == status.HTTP_200_OK
    retrieved_item = get_response.json()
    assert retrieved_item["id"] == created_item["id"]
    assert retrieved_item["name"] == item_data["name"]


@pytest.mark.asyncio
async def test_update_item(ac: AsyncClient):
    """
    Тест обновления существующего Item.
    """
    # 1. Создаем Item
    item_data = {"name": "Item to update", "description": "Old desc", "price": 10.0}
    create_response = await ac.post("/api/v1/item/", json=item_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    item_id = create_response.json()["id"]

    # 2. Обновляем Item
    update_data = {"name": "Updated Item Name", "price": 15.50}
    update_response = await ac.patch(f"/api/v1/item/{item_id}", json=update_data)
    assert update_response.status_code == status.HTTP_200_OK
    updated_item = update_response.json()

    assert updated_item["id"] == item_id
    assert updated_item["name"] == update_data["name"]
    assert updated_item["description"] == item_data["description"] # Описание не меняли
    assert updated_item["price"] == update_data["price"]

    # 3. Проверяем, что изменения сохранились
    get_response = await ac.get(f"/api/v1/item/{item_id}")
    assert get_response.status_code == status.HTTP_200_OK
    final_item = get_response.json()
    assert final_item["name"] == update_data["name"]


@pytest.mark.asyncio
async def test_delete_item(ac: AsyncClient):
    """
    Тест удаления Item.
    """
    # 1. Создаем Item
    item_data = {"name": "Item to delete", "price": 5.0}
    create_response = await ac.post("/api/v1/item/", json=item_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    item_id = create_response.json()["id"]

    # 2. Удаляем Item
    delete_response = await ac.delete(f"/api/v1/item/{item_id}")
    assert delete_response.status_code == status.HTTP_200_OK
    deleted_item = delete_response.json()
    assert deleted_item["id"] == item_id

    # 3. Проверяем, что Item больше не существует
    get_response = await ac.get(f"/api/v1/item/{item_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_item_conflict(ac: AsyncClient):
    """
    Тест создания Item с именем, которое уже существует.
    Ожидаем ошибку 409 Conflict.
    """
    item_data = {
        "name": "Unique Test Item",
        "description": "This item should be unique.",
        "price": 99.99
    }
    # 1. Создаем первый Item - он должен создаться успешно
    response1 = await ac.post("/api/v1/item/", json=item_data)
    assert response1.status_code == status.HTTP_201_CREATED

    # 2. Пытаемся создать второй Item с тем же 'name'
    response2 = await ac.post("/api/v1/item/", json=item_data)

    # 3. Проверяем, что получили ошибку 409 Conflict
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert response2.json() == {"detail": "Conflict"}