from tests.conftest import TestSession, client
from app.models import Template


def test_templates_list_empty():
    response = client.get("/templates")
    assert response.status_code == 200
    assert "Templates" in response.text


def test_create_template():
    response = client.post("/templates/create", data={
        "name": "Welcome Template",
        "subject_template": "Bonjour {{prenom}}",
        "body_template": "<p>Hello {{prenom}} from {{nom}}</p>",
    }, follow_redirects=False)
    assert response.status_code == 303

    db = TestSession()
    template = db.query(Template).first()
    assert template is not None
    assert template.name == "Welcome Template"
    db.close()


def test_templates_list_with_data():
    db = TestSession()
    db.add(Template(name="T1", subject_template="S", body_template="B"))
    db.commit()
    db.close()

    response = client.get("/templates")
    assert response.status_code == 200
    assert "T1" in response.text


def test_edit_template():
    db = TestSession()
    t = Template(name="T1", subject_template="S", body_template="B")
    db.add(t)
    db.commit()
    tid = t.id
    db.close()

    response = client.get(f"/templates/{tid}/edit")
    assert response.status_code == 200
    assert "T1" in response.text

    response = client.post(f"/templates/{tid}/edit", data={
        "name": "T1 Updated",
        "subject_template": "New Subject",
        "body_template": "New Body",
    }, follow_redirects=False)
    assert response.status_code == 303

    db = TestSession()
    updated = db.query(Template).get(tid)
    assert updated.name == "T1 Updated"
    db.close()
