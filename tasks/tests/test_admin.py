"""
Django Todo List - Тесты административного интерфейса
==================================================

Проект: Task Management API
Технологии: Django 4.2.7, Django REST Framework, pytest
Методология: Test-Driven Development (TDD)

Описание тестового модуля:
-------------------------
Данный модуль содержит тесты для административного интерфейса Django,
который используется для управления задачами через веб-интерфейс.

Тестовое покрытие:
-----------------
1. Конфигурация админки
   - Отображаемые поля (list_display)
   - Фильтры (list_filter)
   - Поля поиска (search_fields)
   - Сортировка (ordering)
   - Поля только для чтения (readonly_fields)
   - Количество элементов на странице (list_per_page)

2. Представления админки
   - Страница списка задач (changelist)
   - Страница создания задачи (add)
   - Страница редактирования задачи (change)
   - Страница удаления задачи (delete)

3. Функциональность
   - Сохранение задачи через админку
   - Валидация данных
   - Права доступа

Используемые декораторы:
----------------------
1. @pytest.fixture
   Параметры:
   - scope: время жизни фикстуры
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
   - argnames: имена параметров
   - argvalues: значения параметров
   - ids: идентификаторы тестовых случаев
   - indirect: список параметров для непрямой параметризации

4. @pytest.mark.urls
   Параметры:
   - urls: модуль с URL-конфигурацией для тестов

Примеры использования:
-------------------
```python
# Фикстура для админ-сайта
@pytest.fixture(scope="module")
def admin_site():
    return AdminSite()

# Фикстура для админ-пользователя
@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='password'
    )

# Тест с параметризацией
@pytest.mark.parametrize("field,value", [
    ("title", "Test Task"),
    ("description", "Test Description"),
])
@pytest.mark.django_db
def test_admin_field_display(admin_site, field, value):
    task = Task.objects.create(**{field: value})
    admin = TaskAdmin(Task, admin_site)
    assert getattr(task, field) == value
```

Фикстуры:
--------
- admin_site: объект AdminSite для тестов
- task_admin: настроенный объект TaskAdmin
- admin_user: суперпользователь для доступа к админке
- task: тестовая задача
- request_factory: фабрика для создания запросов

Примечания:
----------
- Тестируется как конфигурация, так и функциональность
- Проверяется доступность всех административных страниц
- Тесты требуют наличия суперпользователя
- Проверяется корректность отображения данных
"""

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse
from tasks.admin import TaskAdmin
from tasks.models import Task

@pytest.fixture
def admin_site():
    """Фикстура, создающая объект административного сайта Django"""
    return AdminSite()

@pytest.fixture
def task_admin(admin_site):
    """Фикстура, создающая объект TaskAdmin для тестирования"""
    return TaskAdmin(Task, admin_site)

@pytest.fixture
def admin_user():
    """
    Фикстура, создающая суперпользователя для тестирования админки
    
    Создает пользователя с правами администратора и следующими учетными данными:
    - username: admin
    - email: admin@example.com
    - password: adminpass123
    """
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )

@pytest.fixture
def task():
    """Фикстура, создающая тестовую задачу в базе данных"""
    return Task.objects.create(
        title='Test Task',
        description='Test Description',
        completed=False
    )

@pytest.fixture
def request_factory():
    """Фикстура, создающая фабрику HTTP-запросов для тестирования"""
    return RequestFactory()

@pytest.mark.django_db
def test_task_admin_list_display(task_admin):
    """
    Тест отображения полей в списке задач
    
    Проверяет, что в списке задач отображаются все необходимые поля:
    - заголовок (title)
    - описание (description)
    - статус выполнения (completed)
    - дата создания (created_at)
    - дата обновления (updated_at)
    """
    assert task_admin.list_display == ('title', 'description', 'completed', 'created_at', 'updated_at')

@pytest.mark.django_db
def test_task_admin_list_filter(task_admin):
    """
    Тест фильтров в административном интерфейсе
    
    Проверяет наличие фильтров по:
    - статусу выполнения (completed)
    - дате создания (created_at)
    - дате обновления (updated_at)
    """
    assert task_admin.list_filter == ('completed', 'created_at', 'updated_at')

@pytest.mark.django_db
def test_task_admin_search_fields(task_admin):
    """
    Тест полей поиска в административном интерфейсе
    
    Проверяет возможность поиска по:
    - заголовку задачи (title)
    - описанию задачи (description)
    """
    assert task_admin.search_fields == ('title', 'description')

@pytest.mark.django_db
def test_task_admin_ordering(task_admin):
    """
    Тест сортировки задач в административном интерфейсе
    
    Проверяет, что задачи отсортированы по дате создания
    в обратном порядке (новые сверху)
    """
    assert task_admin.ordering == ('-created_at',)

@pytest.mark.django_db
def test_task_admin_readonly_fields(task_admin):
    """
    Тест полей, доступных только для чтения
    
    Проверяет, что следующие поля нельзя изменять:
    - дата создания (created_at)
    - дата обновления (updated_at)
    """
    assert task_admin.readonly_fields == ('created_at', 'updated_at')

@pytest.mark.django_db
def test_task_admin_list_per_page(task_admin):
    """
    Тест количества задач на странице
    
    Проверяет, что на одной странице отображается
    не более 25 задач
    """
    assert task_admin.list_per_page == 25

@pytest.mark.django_db
def test_task_admin_change_view(admin_user, client, task):
    """
    Тест страницы редактирования задачи
    
    Проверяет:
    - Доступность страницы редактирования (HTTP 200)
    - Наличие данных задачи на странице
    """
    # Авторизуем администратора
    client.force_login(admin_user)
    
    # Получаем URL страницы редактирования
    url = reverse('admin:tasks_task_change', args=[task.pk])
    response = client.get(url)
    
    # Проверяем ответ
    assert response.status_code == 200
    assert task.title.encode() in response.content

@pytest.mark.django_db
def test_task_admin_add_view(admin_user, client):
    """
    Тест страницы создания новой задачи
    
    Проверяет доступность страницы создания
    новой задачи (HTTP 200)
    """
    # Авторизуем администратора
    client.force_login(admin_user)
    
    # Получаем URL страницы создания
    url = reverse('admin:tasks_task_add')
    response = client.get(url)
    
    # Проверяем ответ
    assert response.status_code == 200

@pytest.mark.django_db
def test_task_admin_delete_view(admin_user, client, task):
    """
    Тест страницы удаления задачи
    
    Проверяет доступность страницы подтверждения
    удаления задачи (HTTP 200)
    """
    # Авторизуем администратора
    client.force_login(admin_user)
    
    # Получаем URL страницы удаления
    url = reverse('admin:tasks_task_delete', args=[task.pk])
    response = client.get(url)
    
    # Проверяем ответ
    assert response.status_code == 200

@pytest.mark.django_db
def test_task_admin_changelist_view(admin_user, client, task):
    """
    Тест страницы со списком всех задач
    
    Проверяет:
    - Доступность страницы со списком (HTTP 200)
    - Наличие созданной задачи в списке
    """
    # Авторизуем администратора
    client.force_login(admin_user)
    
    # Получаем URL страницы со списком
    url = reverse('admin:tasks_task_changelist')
    response = client.get(url)
    
    # Проверяем ответ
    assert response.status_code == 200
    assert task.title.encode() in response.content

@pytest.mark.django_db
def test_task_admin_save_model(task_admin, request_factory):
    """
    Тест сохранения задачи через админку
    
    Проверяет:
    - Корректное сохранение новой задачи
    - Правильность сохраненных данных
    - Значение по умолчанию для поля completed
    """
    # Создаем тестовый запрос
    request = request_factory.get('/')
    
    # Создаем новый объект задачи
    obj = Task(title='New Task', description='New Description')
    
    # Сохраняем задачу через админку
    task_admin.save_model(request, obj, None, None)
    
    # Проверяем сохраненные данные
    saved_task = Task.objects.get(title='New Task')
    assert saved_task.description == 'New Description'
    assert not saved_task.completed  # По умолчанию задача не выполнена
