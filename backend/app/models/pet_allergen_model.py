"""
宠物过敏食材管理模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..extensions import db

class AllergySeverity(enum.Enum):
    MILD = "mild"           # 轻微
    MODERATE = "moderate"   # 中度
    SEVERE = "severe"       # 严重

class PetAllergen(db.Model):
    """宠物过敏食材记录模型"""
    __tablename__ = 'pet_allergens'
    
    # 基础信息
    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    
    # 过敏详情
    severity = Column(Enum(AllergySeverity), nullable=False, default=AllergySeverity.MILD)
    notes = Column(Text, nullable=True)  # 过敏症状或备注
    confirmed_date = Column(DateTime, nullable=True)  # 确认过敏的日期
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(db.Boolean, default=True)
    
    # 关联关系
    pet = relationship("Pet", backref="allergens")
    ingredient = relationship("Ingredient", backref="allergic_pets")
    
    def __repr__(self):
        return f"<PetAllergen(pet_id={self.pet_id}, ingredient_id={self.ingredient_id}, severity={self.severity})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'severity': self.severity.value,
            'notes': self.notes,
            'confirmed_date': self.confirmed_date.isoformat() if self.confirmed_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
    
    @classmethod
    def get_pet_allergen_ids(cls, pet_id):
        """获取宠物的所有过敏食材ID"""
        allergens = cls.query.filter_by(pet_id=pet_id, is_active=True).all()
        return [allergen.ingredient_id for allergen in allergens]
    
    @classmethod
    def check_allergen_conflict(cls, pet_id, ingredient_ids):
        """检查食材列表是否与宠物过敏食材冲突"""
        allergen_ids = cls.get_pet_allergen_ids(pet_id)
        conflicts = []
        
        for ingredient_id in ingredient_ids:
            if ingredient_id in allergen_ids:
                allergen = cls.query.filter_by(
                    pet_id=pet_id, 
                    ingredient_id=ingredient_id,
                    is_active=True
                ).first()
                if allergen:
                    conflicts.append({
                        'ingredient_id': ingredient_id,
                        'ingredient_name': allergen.ingredient.name,
                        'severity': allergen.severity.value,
                        'notes': allergen.notes
                    })
        
        return conflicts