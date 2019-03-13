# Panda365

# Build Status

-   [![CircleCI](https://circleci.com/gh/luckybuyer/panda365.svg?style=svg&circle-token=3f9fea3e6941568ad0e61249091defd2c232dcdd)](https://circleci.com/gh/luckybuyer/panda365)

## System dependencies

-   Python 3.6
-   Database: PostgreSQL 9.6
-   Web framework: flask
-   Test framework: py.test

## Setup development environment

We keep things simple.

1.  create and activate virtualenv, upgrade pip:

        virtualenv -p `which python3` ~/.virtualenvs/panda365
        . ~/.virtualenvs/panda365/bin/activate
        pip install -U pip

2.  go to source code root and install dependencies:

        make install

3.  create database

        createdb panda365

4.  create database schema. This also creates a default admin user. username:
    "u@dev.com", password: "123456"

        $(make flask) && flask db upgrade

5.  verify everything's OK:

        make test

6.  run!

    We use flask cli interface to run commands. Before everything, the environment variable FLASK_APP must be set. You can either manually set by 

        export FLASK_APP=main.py

    or `$(make flask)`. Now you can run the dev server by `flask run`. For other management commands, see `flask --help`.

7.  install git hooks for a better dev workflow:

        make hooks

Help yourself with `make`.

## API

-   Serialization and Validation - [marshmallow-sqlalchemy](https://github.com/marshmallow-code/marshmallow-sqlalchemy) and [webargs](https://github.com/sloria/webargs)
-   Routing - good old blueprints
-   Timestamps/Datetime - [arrow](https://github.com/crsmithdev/arrow): ISO 8601 timestamp with timezone information
-   Once you start the server, API docs is available at <http://localhost:5000/v1/docs.html>.

## Admin

-   URL: <http://localhost:5000/v1/docs.html>. You can login with credentials
    of the default user: name "u@dev.com", password "123456".

## Conventions

### datetime

-   Do not use the built-in datetime/date/time modules. Use [arrow](http://crsmithdev.com/arrow/) instead. For reasons, see [why](http://crsmithdev.com/arrow/#why)

-   Always store utc in db. Always use `arrow.utcnow`.

-   The corresponding model column is :class:`sqlalchemy_utils.ArrowType`.

### tests

Almost all tests are unittest. They have minimum side effects, all interactions
with the database are sandboxed and rollback at the end of the tests.

100% coverage is required.
