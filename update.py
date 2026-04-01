from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from models import User  # ajusta o import se necessário

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def update_users_bio():
    session = SessionLocal()

    try:
        session.execute(
            update(User)
            .where((User.bio == None) | (User.bio == ""))
            .values(bio="Hi! I'm new here!")
        )
        session.commit()
        print("✅ Users updated successfully!")

    except Exception as e:
        session.rollback()
        print("❌ Error:", e)

    finally:
        session.close()

if __name__ == "__main__":
    update_users_bio()