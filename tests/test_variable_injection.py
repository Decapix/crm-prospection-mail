from app.services.variable_injection import render_template, normalize_column_name


def test_normalize_column_name():
    assert normalize_column_name("nom") == "nom"
    assert normalize_column_name("nom du fondateur/decisionnaire") == "nom_du_fondateur_decisionnaire"
    assert normalize_column_name("email du decisionnaire") == "email_du_decisionnaire"
    assert normalize_column_name("site_web") == "site_web"
    assert normalize_column_name("linkedlin du fondateur/decisionnaire") == "linkedlin_du_fondateur_decisionnaire"


def test_render_template_simple():
    template = "Bonjour {{prenom}}, bienvenue chez {{nom}}"
    data = {"prenom": "Hugues", "nom": "123syndic"}
    result = render_template(template, data)
    assert result == "Bonjour Hugues, bienvenue chez 123syndic"


def test_render_template_with_normalized_keys():
    template = "Bonjour {{prenom}}, je vois que vous êtes chez {{nom}}"
    data = {"prenom": "Hugues", "nom": "123syndic", "site_web": "https://123syndic.com/"}
    result = render_template(template, data)
    assert result == "Bonjour Hugues, je vois que vous êtes chez 123syndic"


def test_render_template_unmatched_variable_left_as_is():
    template = "Bonjour {{prenom}}, votre code est {{code_promo}}"
    data = {"prenom": "Hugues"}
    result = render_template(template, data)
    assert result == "Bonjour Hugues, votre code est {{code_promo}}"


def test_render_template_no_variables():
    template = "Bonjour, ceci est un message sans variables."
    data = {"prenom": "Hugues"}
    result = render_template(template, data)
    assert result == "Bonjour, ceci est un message sans variables."


def test_render_template_empty_value():
    template = "Bonjour {{prenom}}"
    data = {"prenom": ""}
    result = render_template(template, data)
    assert result == "Bonjour "
