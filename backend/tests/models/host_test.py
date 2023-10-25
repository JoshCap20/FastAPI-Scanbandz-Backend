from ...models.host import Host
import pytest

@pytest.mark.unit
def test_new_host():
    host = Host(
        first_name="Test",
        last_name="Host",
        phone_number="1234567890",
        email="test@gmail.com",
        password="test1234567"
    )
    assert host.first_name == "Test"
    assert host.last_name == "Host"
    assert host.phone_number == "1234567890"
    assert host.email == "test@gmail.com"
    assert host.password == "test1234567"

@pytest.mark.unit
def test_host_password_validation():
    with pytest.raises(ValueError):
        Host(
            first_name="Test",
            last_name="Host",
            phone_number="1234567890",
            email="test@gmail.com",
            password="test"
        )

@pytest.mark.unit
def test_host_phone_number_validation_invalid_digits():
    with pytest.raises(ValueError):
        Host(
            first_name="Test",
            last_name="Host",
            phone_number="123456789a",
            email="test@gmail.com",
            password="test1234567"
        )

@pytest.mark.unit
def test_host_non_us_phone_number_validation():
    with pytest.raises(ValueError):
        Host(
            first_name="Test",
            last_name="Host",
            phone_number="123456789",
            email="test@gmail.com",
            password="test1234567"
        )

@pytest.mark.unit
def test_host_non_us_phone_number_validation_extra():
    with pytest.raises(ValueError):
        Host(
            first_name="Test",
            last_name="Host",
            phone_number="123456789012",
            email="test@gmail.com",
            password="test1234567"
        )

@pytest.mark.unit
def test_host_first_name_validation():
    with pytest.raises(ValueError):
        Host(
            first_name="",
            last_name="Host",
            phone_number="1234567890",
            email="test@gmail.com",
            password="test1234567"
        )

@pytest.mark.unit
def test_host_last_name_validation():
    with pytest.raises(ValueError):
        Host(
            first_name="Test",
            last_name="",
            phone_number="1234567890",
            email="test@gmail.com",
            password="test1234567"
        )

@pytest.mark.unit
def test_invalid_email_validation():
    with pytest.raises(ValueError):
        Host(
            first_name="Test",
            last_name="Host",
            phone_number="1234567890",
            email="testgmail.com",
            password="test1234567"
        )

@pytest.mark.unit
def test_invalid_email_validation_two():
    with pytest.raises(ValueError):
        Host(
            first_name="Test",
            last_name="Host",
            phone_number="1234567890",
            email="test@gmailcom",
            password="test1234567"
        )

@pytest.mark.unit
def test_invalid_email_validation_three():
    with pytest.raises(ValueError):
        Host(
            first_name="Test",
            last_name="Host",
            phone_number="1234567890",
            email="test@@gmail.com",
            password="test1234567"
        )