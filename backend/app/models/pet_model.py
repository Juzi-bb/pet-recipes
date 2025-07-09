# 宠物数据模型
from ..extensions import db

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # [cite: 13]
    species = db.Column(db.String(50), nullable=False) # [cite: 14]
    weight = db.Column(db.Float, nullable=False) # [cite: 15]
    age = db.Column(db.Integer, nullable=False) # [cite: 16]
    special_needs = db.Column(db.String(200)) # [cite: 17]
    
    # 外键，关联到用户表的 id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)