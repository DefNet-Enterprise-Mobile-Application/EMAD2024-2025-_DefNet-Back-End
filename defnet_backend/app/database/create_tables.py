from database.database import engine, Base



def create_database():
    Base.metadata.create_all(bind=engine)