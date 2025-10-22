from app import create_app
from app.string_model import db, String
app = create_app()

#create table
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=False)
