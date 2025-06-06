import pytest
from hello_app.models import Message

@pytest.mark.django_db
def test_message_creation():
    message = Message.objects.create(text="Hello, Unit Test!")
    assert message.text == "Hello, Unit Test!"
    assert message.id is not None
    assert Message.objects.count() == 1

@pytest.mark.django_db
def test_message_string_representation():
    message = Message.objects.create(text="Another message")
    assert str(message) == "Another message"
