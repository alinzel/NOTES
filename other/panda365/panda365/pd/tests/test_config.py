from flask import Flask
import pytest
from pd.config import load_config, required


@pytest.fixture
def app():
    return Flask(__name__)


def test_load_config(app):
    with pytest.raises(RuntimeError):
        load_config(app, 'Production')

    load_config(app, 'Test')
    assert app.config['ENV'] == 'test'


def test_load_envvar(app, monkeypatch):
    monkeypatch.setenv('PD_SECRET', 'blah')

    load_config(app)
    assert app.config['SECRET'] == 'blah'


def test_required_config(app):
    class Config:
        A = required

    with pytest.raises(RuntimeError):
        load_config(app, Config)

    load_config(app, Config, A='a')
    assert app.config['A'] == 'a'
