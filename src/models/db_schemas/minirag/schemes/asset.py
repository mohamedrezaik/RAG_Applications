from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid


class Asset(SQLAlchemyBase):
    # Set table name
    __tablename__ = "assets"

    # Set table columns
    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    # Set asset uuid value as uuid object not string
    asset_uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4, unique=True)
    
    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_size = Column(Integer, nullable=False)
    # We will use JSONB to store the config of the asset as json it helps to be fast in reading but reduce writing speed, so it's tradeoff of what you focus on 
    asset_config = Column(JSONB, nullable=True)
    
    # Set column that links assets to projects
    asset_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    
    project = relationship("Project", back_populates="assets")
    
    # We need to index our foreignkey to make reading fast
    # Note: by default any column that is primary key or unique is indexed automatically
    __table_args__ = (
        Index("idx_asset_project_id", asset_project_id),
        Index("ix_asset_type", asset_type)
    )