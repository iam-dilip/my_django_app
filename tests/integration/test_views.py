import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_hello_world_view_success(client):
    # Assuming your 'hello_app' has a URL named 'hello_world'
    # e.g., path('hello/', views.hello_world, name='hello_world')
    url = reverse('hello_world') # Replace 'hello_world' with the actual name of your URL pattern
    response = client.get(url)

    assert response.status_code == 200
    assert "Welcome to My Simple Django App!" in response.content.decode() # Check for expected text
    assert "Messages" in response.content.decode() # Check for messages section

@pytest.mark.django_db
def test_hello_world_view_with_messages(client):
    from hello_app.models import Message
    Message.objects.create(text="Test Message 1")
    Message.objects.create(text="Test Message 2")

    url = reverse('hello_world')
    response = client.get(url)

    assert response.status_code == 200
    assert "Test Message 1" in response.content.decode()
    assert "Test Message 2" in response.content.decode()
    assert Message.objects.count() == 2
