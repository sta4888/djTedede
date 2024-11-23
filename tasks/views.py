from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    methods=['get'],
    operation_description="Get list of all tasks",
    responses={200: TaskSerializer(many=True)}
)
@swagger_auto_schema(
    methods=['post'],
    operation_description="Create a new task",
    request_body=TaskSerializer,
    responses={201: TaskSerializer}
)
@api_view(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['get'],
    operation_description="Get a specific task by ID",
    responses={200: TaskSerializer}
)
@swagger_auto_schema(
    methods=['put'],
    operation_description="Update a specific task",
    request_body=TaskSerializer,
    responses={200: TaskSerializer}
)
@swagger_auto_schema(
    methods=['delete'],
    operation_description="Delete a specific task",
    responses={204: "No Content"}
)
@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
