from company_blog import app, db
from company_blog.models import User

with app.app_context():
    # db.drop_all()
    db.create_all()
    user1 = User("admin_user@test.com","Admin User","123","1")
    db.session.add(user1)
    db.session.commit()