from app.crud.crud_link import generate_short_code

def test_generate_short_code():
    # Проверяем, что код генерируется и имеет правильную длину
    code = generate_short_code()
    assert len(code) == 6
    assert code.isalnum()  # Проверяем, что код состоит из букв и цифр

