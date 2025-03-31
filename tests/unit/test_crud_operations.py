from app.crud.crud_link import create_link, get_link_by_short_code, update_link, delete_link
from app.schemas.link import LinkCreate
from sqlalchemy.orm import Session
from unittest.mock import Mock

def test_create_link():
    db = Mock(spec=Session)
    link_data = LinkCreate(original_url="https://example.com")
    
    result = create_link(db, link_data)
    
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

def test_get_link_by_short_code():
    db = Mock(spec=Session)
    short_code = "abc123"
    
    db.query().filter().first.return_value = None
    
    result = get_link_by_short_code(db, short_code)
    assert result is None

def test_update_link():
    db = Mock(spec=Session)
    short_code = "abc123"
    new_url = "https://newexample.com"
    owner_id = 1
    
    db.query().filter().first.return_value = None
    
    result = update_link(db, short_code, new_url, owner_id)
    assert result is None

# def test_delete_link():
#     db = Mock(spec=Session)
#     short_code = "abc123"
#     owner_id = 1
    
#     db.query().filter().first.return_value = None
    
#     result = delete_link(db, short_code, owner_id)
#     assert not result

