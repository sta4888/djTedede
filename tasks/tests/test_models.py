"""
Django Todo List - Тесты моделей
================================

Проект: Task Management API
Технологии: Django 4.2.7, Django REST Framework, pytest
Методология: Test-Driven Development (TDD)

Описание тестового модуля:
-------------------------
Данный модуль содержит тесты для модели Task, которая является основной
сущностью в нашем приложении для управления задачами.

Тестовое покрытие:
-----------------
1. Создание задачи
   - Проверка всех полей
   - Проверка значений по умолчанию
   - Валидация данных

2. Обновление задачи
   - Изменение полей
   - Автоматическое обновление временных меток

3. Валидация данных
   - Проверка максимальной длины заголовка
   - Проверка необязательности описания

4. Сортировка и упорядочивание
   - Проверка порядка задач по дате создания

Используемые декораторы:
----------------------
1. @pytest.fixture
   Параметры:
   - scope: определяет время жизни фикстуры
     * "function" (по умолчанию) - создается для каждого теста
     * "class" - для всех тестов в классе
     * "module" - для всех тестов в модуле
     * "session" - для всей сессии тестирования
   - autouse: если True, фикстура будет автоматически использоваться
   - name: альтернативное имя для фикстуры
   - params: параметризация фикстуры

2. @pytest.mark.django_db
   Параметры:
   - transaction: если True, каждый тест выполняется в транзакции
   - reset_sequences: сбрасывает счетчики автоинкремента
   - databases: указывает, какие базы данных использовать

Примеры использования:
-------------------
```python
# Фикстура на уровне модуля
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Подготовка базы данных
    yield
    # Очистка после тестов

# Тест с транзакцией
@pytest.mark.django_db(transaction=True)
def test_complex_operation():
    # Тест с автоматическим откатом транзакции
    pass
```

Фикстуры:
--------
- task_data: базовые данные для создания задачи
- task: готовый объект задачи в базе данных

Примечания:
----------
- Тесты изолированы друг от друга
- Каждый тест использует чистую базу данных
- Временные метки проверяются на корректность обновления
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db.utils import DataError
from tasks.models import Task

@pytest.fixture
def task_data():
    """Фикстура, возвращающая тестовые данные для создания задачи"""
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
def test_task_creation(task_data):
    """
    Тест создания базовой задачи
    
    Проверяет:
    - Корректность сохранения всех полей задачи
    - Автоматическое создание временных меток created_at и updated_at
    """
    # Создаем новую задачу
    task = Task.objects.create(**task_data)
    
    # Проверяем, что все поля сохранены корректно
    assert task.title == task_data['title']
    assert task.description == task_data['description']
    assert task.completed == task_data['completed']
    
    # Проверяем, что временные метки были установлены
    assert task.created_at is not None
    assert task.updated_at is not None

@pytest.mark.django_db
def test_task_str_representation(task):
    """
    Тест строкового представления задачи
    
    Проверяет, что метод __str__ возвращает заголовок задачи
    """
    assert str(task) == task.title

@pytest.mark.django_db
def test_task_ordering():
    """
    Тест сортировки задач
    
    Проверяет, что задачи сортируются по дате создания в обратном порядке
    (новые задачи отображаются первыми)
    """
    # Создаем первую задачу
    task1 = Task.objects.create(
        title='Task 1',
        description='First task'
    )
    
    # Ждем немного, чтобы гарантировать разное время создания
    import time
    time.sleep(0.1)
    
    # Создаем вторую задачу
    task2 = Task.objects.create(
        title='Task 2',
        description='Second task'
    )
    
    # Получаем все задачи и проверяем их порядок
    tasks = Task.objects.all()
    assert tasks[0] == task2  # Новая задача должна быть первой
    assert tasks[1] == task1  # Старая задача должна быть второй

@pytest.mark.django_db
def test_task_completion():
    """
    Тест функционала завершения задачи
    
    Проверяет:
    - Задача по умолчанию не завершена
    - Возможность пометить задачу как завершенную
    - Обновление временной метки updated_at при завершении
    """
    # Создаем новую задачу
    task = Task.objects.create(
        title='Test Task',
        description='Test Description'
    )
    assert not task.completed  # Задача должна быть не завершена по умолчанию
    
    # Ждем немного, чтобы гарантировать разное время обновления
    import time
    time.sleep(0.1)
    
    # Отмечаем задачу как завершенную
    task.completed = True
    task.save()
    
    # Обновляем данные из базы
    task.refresh_from_db()
    assert task.completed  # Проверяем, что задача помечена как завершенная
    assert task.updated_at > task.created_at  # Проверяем, что время обновления изменилось

@pytest.mark.django_db
def test_task_update():
    """
    Тест обновления задачи
    
    Проверяет:
    - Возможность изменения полей задачи
    - Корректное обновление временной метки updated_at
    """
    # Создаем начальную задачу
    task = Task.objects.create(
        title='Original Title',
        description='Original Description'
    )
    original_updated_at = task.updated_at
    
    # Ждем немного, чтобы гарантировать разное время обновления
    import time
    time.sleep(0.1)
    
    # Обновляем задачу
    task.title = 'Updated Title'
    task.description = 'Updated Description'
    task.save()
    
    # Обновляем данные из базы
    task.refresh_from_db()
    assert task.title == 'Updated Title'
    assert task.description == 'Updated Description'
    assert task.updated_at > original_updated_at

@pytest.mark.django_db
def test_task_blank_description():
    """
    Тест создания задачи с пустым описанием
    
    Проверяет, что описание может быть пустым (null=True, blank=True)
    """
    # Создаем задачу без описания
    task = Task.objects.create(
        title='Task without description'
    )
    assert task.description is None  # Проверяем, что описание может быть пустым

@pytest.mark.django_db
def test_task_title_max_length():
    """
    Тест ограничения длины заголовка
    
    Проверяет, что нельзя создать задачу с заголовком длиннее 200 символов
    """
    # Пытаемся создать задачу с слишком длинным заголовком
    with pytest.raises(DataError):
        Task.objects.create(
            title='A' * 201,  # Создаем строку длиной 201 символ
            description='Test Description'
        )
