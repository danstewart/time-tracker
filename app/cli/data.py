import click
from flask import Blueprint

v = Blueprint("data", __name__)


@v.cli.command("seed-test-db")
def seed_test_db():
    from app import db
    from app.models import User

    click.echo("Seeding test database...")

    test_user = User(email="test@example.com")
    db.session.add(test_user)

    test_user.set_password("test")
    test_user.verify()

    click.echo("Completed database seeding.")
