"""
宠物过敏食材关联模型
管理宠物的过敏食材信息
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.extensions import db

class PetAllergen(db.Model):
    """宠物过敏食材关联表"""
    __tablename__ = 'pet_allergens'
    
    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey('pet.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    
    # 过敏信息
    severity = Column(db.String(20), nullable=False, default='mild')  # mild, moderate, severe
    notes = Column(Text, nullable=True)  # 过敏反应描述
    confirmed_date = Column(DateTime, nullable=True)  # 确认过敏的日期
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    pet = relationship("Pet", backref="allergens")
    ingredient = relationship("Ingredient", backref="allergic_pets")
    
    def __repr__(self):
        return f"<PetAllergen(pet_id={self.pet_id}, ingredient_id={self.ingredient_id}, severity='{self.severity}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'ingredient_category': self.ingredient.category.value if self.ingredient else None,
            'severity': self.severity,
            'notes': self.notes,
            'confirmed_date': self.confirmed_date.isoformat() if self.confirmed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
