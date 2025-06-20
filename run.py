from app import create_app, db
import click

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

@app.cli.command("init-db")
def init_db():
    """Initialize the database tables."""
    db.create_all()
    click.echo("✅ Database initialized.")