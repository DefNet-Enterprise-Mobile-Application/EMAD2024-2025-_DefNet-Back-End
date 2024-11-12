from defnet_backend.app.database.database import engine, Base

Base.metadata.create_all(bind=engine)