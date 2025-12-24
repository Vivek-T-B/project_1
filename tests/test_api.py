import json
import pytest

from app import create_app, db, Item


@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()


def test_create_get_update_delete_flow(client):
    # Create
    resp = client.post('/items', json={'name': 'Toy', 'description': 'A small toy'})
    assert resp.status_code == 201
    created = resp.get_json()
    assert created['name'] == 'Toy'
    item_id = created['id']

    # Get
    resp = client.get(f'/items/{item_id}')
    assert resp.status_code == 200
    got = resp.get_json()
    assert got['id'] == item_id
    assert got['name'] == 'Toy'

    # List
    resp = client.get('/items')
    assert resp.status_code == 200
    items = resp.get_json()
    assert isinstance(items, list) and len(items) == 1

    # Update
    resp = client.put(f'/items/{item_id}', json={'name': 'Toy Updated', 'description': 'Updated desc'})
    assert resp.status_code == 200
    updated = resp.get_json()
    assert updated['name'] == 'Toy Updated'

    # Delete
    resp = client.delete(f'/items/{item_id}')
    assert resp.status_code == 200
    res = resp.get_json()
    assert res.get('result') is True

    # Confirm 404
    resp = client.get(f'/items/{item_id}')
    assert resp.status_code == 404


def test_create_requires_name(client):
    resp = client.post('/items', json={'description': 'no name'})
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data
