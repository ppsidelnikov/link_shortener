def test_register(client):
    response = client.post(
        "/register",
        json={
            'email': 'test@mail.ru',
            'password': 'abcabc'
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == 'test@mail.ru'


def test_login(client):
    response = client.post(
        "/login",
        data={
            "username": 'test@mail.ru',
            "password": 'abcabc'
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_link(client):
    json = {
        "username": 'test@mail.ru',
        "password": 'abcabc',
    }
    response = client.post(
        "/login",
        data=json
    )
    
    token = response.json()['access_token']

    response = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com", "custom_alias": 'shortlink'},
        headers={'Authorization' : f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert "short_code" in response.json()

def test_update_link(client):
    login_response = client.post(
        "/login",
        data={
            "username": 'test@mail.ru',
            "password": 'abcabc'
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    response = client.put(
        "/links/shortlink",
        json={"new_url": "https://newexample.com"},
        headers={'Authorization' : f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json()["original_url"] == "https://newexample.com/"

def test_delete_link(client):
    login_response = client.post(
        "/login",
        data={
            "username": 'test@mail.ru',
            "password": 'abcabc'
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    short_code = 'shortlink'
    
    response = client.delete(f"/links/{short_code}", headers={'Authorization' : f'Bearer {token}'})
    assert response.status_code == 204    
