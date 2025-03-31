def test_redirect(client):
    response = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com", 'custom_alias' : 'shortlink2'}
    )
    short_code = 'shortlink2'
    
    response = client.get(f"/links/{short_code}", follow_redirects=False)
    assert response.status_code == 302
