from src.db.core import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_pro = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.email} - Pro: {self.is_pro}>"
