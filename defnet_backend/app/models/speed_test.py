from sqlalchemy import Column, Integer, Float, DateTime
from database.database import Base
from datetime import datetime


class SpeedTest(Base):
    __tablename__ = "speed_test"
    
    id = Column(Integer, primary_key=True, index=True)
    download_speed = Column(Float, nullable=False)
    upload_speed = Column(Float, nullable=False)
    latency = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
