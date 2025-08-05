from ..extensions import db
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from datetime import datetime

class RecipeLike(db.Model):
    """用户点赞食谱关联表模型"""
    __tablename__ = 'recipe_likes'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 建立关系
    user = db.relationship('User', backref='liked_recipes')
    recipe = db.relationship('Recipe', backref='liked_by')
    
    # 避免重复点赞
    __table_args__ = (UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_like'),)
    
    def __repr__(self):
        return f'<RecipeLike user_id={self.user_id} recipe_id={self.recipe_id}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recipe_id': self.recipe_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }