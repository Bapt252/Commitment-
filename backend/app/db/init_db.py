from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.core.security import get_password_hash
from app.models.user import User

# Créer les tables dans la base de données
def init_db() -> None:
    Base.metadata.create_all(bind=engine)

# Ajouter des données initiales
def create_initial_data(db: Session) -> None:
    # Créer un super utilisateur
    admin_user = db.query(User).filter(User.email == "admin@commitment.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@commitment.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

# Script principal pour initialiser la base de données
def main() -> None:
    init_db()
    db = Session(engine)
    create_initial_data(db)
    db.close()

if __name__ == "__main__":
    main()