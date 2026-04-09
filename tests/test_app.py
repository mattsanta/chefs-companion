import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_recipes(client):
    """Test that we can get the list of popular recipes via API."""
    rv = client.get('/recipes/popular')
    assert rv.status_code == 200
    data = rv.get_json()
    assert any(recipe['name'] == "Spaghetti Carbonara" for recipe in data)

def test_get_recipe_details(client):
    """Test that we can get details for a specific recipe."""
    rv = client.get('/recipe/Spaghetti%20Carbonara')
    assert rv.status_code == 200
    assert b"Pancetta" in rv.data

def test_get_nonexistent_recipe(client):
    """Test that requesting a nonexistent recipe returns 404."""
    rv = client.get('/recipe/Nonexistent')
    assert rv.status_code == 404
