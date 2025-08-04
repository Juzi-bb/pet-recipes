# 宠物数据模型
from datetime import datetime
from ..extensions import db

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 宠物名字
    species = db.Column(db.String(50), nullable=False)  # 种类（狗/猫）
    breed = db.Column(db.String(100), nullable=True)  # 品种（可选）
    weight = db.Column(db.Float, nullable=False)  # 体重
    age = db.Column(db.Integer, nullable=False)  # 年龄
    special_needs = db.Column(db.String(500))  # 特殊需求
    avatar = db.Column(db.String(100), nullable=False, default='dog1.png')  # 头像文件名
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    __tablename__ = 'pets'

    # 外键，关联到用户表的 id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 添加字符串表示方法
    def __repr__(self):
        return f'<Pet {self.name}({self.species})>'
    
    # 添加转换为字典的方法
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'weight': self.weight,
            'age': self.age,
            'special_needs': self.special_needs,
            'avatar': self.avatar,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'user_id': self.user_id
        }