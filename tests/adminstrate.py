from app.database import User, Office, Operators
from .common import client

def test_update_admin_password(client):
    new_password = 'testing_password'
    response = client.post(
        '/admin_u',
        data=dict(password=new_password),
        follow_redirects=True)

    assert response.status == '200 OK'


def test_list_users(client):
    response = client.get('/users', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    for user in User.query.limit(10):
        assert f'<strong>{user.id}. {user.name}</strong>' in page_content


def test_list_operators(client):
    bundles = []

    with client.application.app_context():
        bundles += [
            (User.get(o.id), Office.get(o.office_id))
            for o in Operators.query.all()
        ]

    for user, office in bundles:
        response = client.get(f'/operators/{office.id}')
        page_content = response.data.decode('utf-8')

        assert f'<strong>{user.id}. {user.name}</strong>' in page_content


def test_add_user(client):
    name = 'test_adding_a_user'
    password = 'testing'
    role = 1
    response = client.post('/user_a', data={
        'name': name, 'password': password, 'role': role
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.query.filter_by(name=name).first() is not None


def test_add_operator(client):
    name = 'test_adding_operator'
    password = 'testing'
    role = 3
    response = client.post('/user_a', data={
        'name': name, 'password': password, 'role': role
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.query.filter_by(name=name).first() is not None


def test_update_user(client):
    with client.application.app_context():
        user = User.query.filter(User.id != 1).first()

    new_name = 'test_updating_user'
    new_password = 'password'
    response = client.post(f'/user_u/{user.id}', data={
        'name': new_name, 'password': new_password, 'role': user.role_id
    })

    with client.application.app_context():
        updated_user = User.query.filter_by(name=new_name).first()

    assert response.status == '302 FOUND'
    assert updated_user is not None


def test_delete_user(client):
    with client.application.app_context():
        user = User.query.filter(User.id != 1).first()

    response = client.get(f'/user_d/{user.id}')

    assert response.status == '302 FOUND'
    assert User.get(user.id) is None


def test_delete_all_users_and_operators(client):
    with client.application.app_context():
        users_length_before = User.query.count()
        operators_length_before = Operators.query.count()

    response = client.get(f'/user_da')

    with client.application.app_context():
        users_length_after = User.query.count()
        operators_length_after = Operators.query.count()

    assert response.status == '302 FOUND'
    assert users_length_before != users_length_after
    assert operators_length_before != operators_length_after
    assert users_length_after == 1  # NOTE: God account won't be deleted
    assert operators_length_after == 0
