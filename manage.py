from app import create_app, db
from app.models import User, Link

app = create_app()

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Initialized the database!")

if __name__ == '__main__':
    app.cli()