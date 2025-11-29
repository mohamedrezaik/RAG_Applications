from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Project(SQLAlchemyBase):
    # Set table name
    __tablename__ = "projects"

    # Set table columns
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    # Set project uuid value as uuid object not string
    project_uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4, unique=True)
    
    # Set created at and make sure you add teh timezone
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    # Set updated at and make sure you add the timezone
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())