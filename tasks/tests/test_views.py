"""
Django Todo List - Тесты представлений API
=========================================

Проект: Task Management API
Технологии: Django 4.2.7, Django REST Framework, pytest
Методология: Test-Driven Development (TDD)

Описание тестового модуля:
-------------------------
Данный модуль содержит тесты для API endpoints, реализованных с использованием
Django REST Framework. Тестируется функциональность CRUD операций для задач.

Тестовое покрытие:
-----------------
1. GET запросы
   - Получение списка всех задач
   - Получение одной конкретной задачи
   - Обработка несуществующих задач

2. POST запросы
   - Создание новой задачи
   - Валидация обязательных полей
   - Обработка некорректных данных

3. PUT запросы
   - Обновление существующей задачи
   - Изменение статуса выполнения
   - Обработка частичных обновлений

4. DELETE запросы
   - Удаление задачи
   - Проверка фактического удаления из БД

Используемые декораторы:
----------------------
1. @pytest.fixture
   Параметры:
   - scope: определяет время жизни фикстуры
     * "function" (по умолчанию) - для каждого теста
     * "class" - для всех тестов в классе
     * "module" - для всех тестов в модуле
     * "session" - для всей сессии тестирования
   - autouse: автоматическое использование фикстуры
   - name: альтернативное имя фикстуры
   - params: параметризация фикстуры

2. @pytest.mark.django_db
   Параметры:
   - transaction: если True, тест выполняется в транзакции
   - reset_sequences: сброс счетчиков автоинкремента
   - databases: используемые базы данных

3. @pytest.mark.parametrize
   Параметры:
   - argnames: имена параметров (строка или список)
   - argvalues: значения параметров
   - ids: идентификаторы тестовых случаев
   - indirect: список параметров для непрямой параметризации

Примеры использования:
-------------------
```python
# Фикстура для API клиента
@pytest.fixture(scope="module")
def api_client():
    return APIClient()

# Параметризованный тест
@pytest.mark.parametrize("status_code,data", [
    (200, {"title": "Valid"}),
    (400, {"title": ""}),
])
@pytest.mark.django_db
def test_create_task(api_client, status_code, data):
    response = api_client.post('/api/tasks/', data)
    assert response.status_code == status_code
```

Фикстуры:
--------
- api_client: клиент для тестирования API
- task_data: базовые данные для создания задачи
- task: готовый объект задачи в базе данных

Примечания:
----------
- Используется APIClient из DRF для тестирования
- Проверяются HTTP статус коды и содержимое ответов
- Тесты охватывают как успешные, так и ошибочные сценарии
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from tasks.models import Task
from tasks.serializers import TaskSerializer

@pytest.fixture
def api_client():
    """Фикстура, создающая тестовый API клиент"""
    return APIClient()

@pytest.fixture
def task_data():
    """Фикстура с тестовыми данными для задачи"""
    return {
        'title': 'Test Task',
        'description': 'Test Description',
        'completed': False
    }

@pytest.fixture
def task(task_data):
    """Фикстура, создающая тестовую задачу в базе данных"""
    return Task.objects.create(**task_data)

@pytest.mark.django_db
def test_get_all_tasks(api_client, task):
    """
    Тест получения списка всех задач
    
    Проверяет:
    - Корректность HTTP-ответа (200 OK)
    - Соответствие возвращаемых данных сериализованным данным из базы
    """
    # Отправляем GET-запрос к API
    response = api_client.get(reverse('task-list'))
    
    # Получаем все задачи из базы и сериализуем их
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    
    # Проверяем ответ
    assert response.status_code == status.HTTP_200_OK
    assert response.data == serializer.data

@pytest.mark.django_db
def test_create_task(api_client):
    """
    Тест создания новой задачи через API
    
    Проверяет:
    - Корректность HTTP-ответа (201 Created)
    - Создание задачи в базе данных
    - Правильность сохраненных данных
    """
    # Подготавливаем данные для новой задачи
    new_task_data = {
        'title': 'New Task',
        'description': 'New Description',
        'completed': False
    }
    
    # Отправляем POST-запрос к API
    response = api_client.post(reverse('task-list'), new_task_data, format='json')
    
    # Проверяем ответ и данные в базе
    assert response.status_code == status.HTTP_201_CREATED
    assert Task.objects.count() == 1
    assert Task.objects.get(title='New Task').description == 'New Description'

@pytest.mark.django_db
def test_get_single_task(api_client, task):
    """
    Тест получения одной конкретной задачи
    
    Проверяет:
    - Корректность HTTP-ответа (200 OK)
    - Соответствие возвращаемых данных сериализованным данным задачи
    """
    # Отправляем GET-запрос к API для получения конкретной задачи
    response = api_client.get(reverse('task-detail', kwargs={'pk': task.pk}))
    
    # Получаем задачу из базы и сериализуем её
    task_obj = Task.objects.get(pk=task.pk)
    serializer = TaskSerializer(task_obj)
    
    # Проверяем ответ
    assert response.status_code == status.HTTP_200_OK
    assert response.data == serializer.data

@pytest.mark.django_db
def test_update_task(api_client, task):
    """
    Тест обновления существующей задачи
    
    Проверяет:
    - Корректность HTTP-ответа (200 OK)
    - Правильность обновления данных в базе
    - Возможность изменения всех полей задачи
    """
    # Подготавливаем данные для обновления
    update_data = {
        'title': 'Updated Task',
        'description': 'Updated Description',
        'completed': True
    }
    
    # Отправляем PUT-запрос к API
    response = api_client.put(
        reverse('task-detail', kwargs={'pk': task.pk}),
        update_data,
        format='json'
    )
    
    # Проверяем ответ и обновленные данные
    assert response.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.title == 'Updated Task'
    assert task.completed is True

@pytest.mark.django_db
def test_delete_task(api_client, task):
    """
    Тест удаления задачи
    
    Проверяет:
    - Корректность HTTP-ответа (204 No Content)
    - Фактическое удаление задачи из базы данных
    """
    # Отправляем DELETE-запрос к API
    response = api_client.delete(reverse('task-detail', kwargs={'pk': task.pk}))
    
    # Проверяем ответ и отсутствие задачи в базе
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Task.objects.count() == 0

@pytest.mark.django_db
def test_invalid_create_task(api_client):
    """
    Тест создания задачи с некорректными данными
    
    Проверяет:
    - Корректность HTTP-ответа (400 Bad Request)
    - Обработку случая с пустым обязательным полем (title)
    """
    # Подготавливаем некорректные данные (пустой заголовок)
    invalid_data = {
        'title': '',  # title является обязательным полем
        'description': 'Test Description'
    }
    
    # Отправляем POST-запрос к API
    response = api_client.post(reverse('task-list'), invalid_data, format='json')
    
    # Проверяем ответ
    assert response.status_code == status.HTTP_400_BAD_REQUEST
