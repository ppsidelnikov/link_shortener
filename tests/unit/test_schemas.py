from app.schemas.link import LinkCreate
from pydantic import ValidationError
import pytest

def test_link_create_valid():

    data = {"original_url": "https://example.com", "expires_in_minutes": 60}
    link = LinkCreate(**data)
    assert str(link.original_url) == "https://example.com/"
    assert link.expires_in_minutes == 60

def test_link_create_invalid():
    # Неверный URL
    with pytest.raises(ValueError):
        LinkCreate(original_url="invalid-url", expires_in_minutes=60)
    
    # Отрицательное время жизни
    with pytest.raises(ValueError):
        LinkCreate(original_url="https://example.com", expires_in_minutes=-10)
