from db.database import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
class GiaiPhapAmThanh(Base):
    __tablename__ = "frontend_giaiphapamthanh"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    content = Column(Text)
    image_url = Column(String(200))
    author_id = Column(Integer, ForeignKey("frontend_user.id"))
    status = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())