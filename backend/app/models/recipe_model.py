from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class RecipeStatus(enum.Enum):
    DRAFT = "draft"           # 草稿
    PUBLISHED = "published"   # 已发布
    ARCHIVED = "archived"     # 已归档

class Recipe(Base):
    __tablename__ = 'recipes'
    
    # 基础信息
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 关联信息
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=True)  # 可选：为特定宠物创建
    
    # 食谱营养信息 (总量)
    total_weight = Column(Float, nullable=False, default=0.0)  # 总重量 (g)
    total_calories = Column(Float, nullable=False, default=0.0)  # 总热量 (kcal)
    total_protein = Column(Float, nullable=False, default=0.0)   # 总蛋白质 (g)
    total_fat = Column(Float, nullable=False, default=0.0)       # 总脂肪 (g)
    total_carbohydrate = Column(Float, nullable=False, default=0.0)  # 总碳水化合物 (g)
    total_fiber = Column(Float, nullable=False, default=0.0)     # 总纤维 (g)
    
    # 主要矿物质总量 (mg)
    total_calcium = Column(Float, nullable=False, default=0.0)
    total_phosphorus = Column(Float, nullable=False, default=0.0)
    total_potassium = Column(Float, nullable=False, default=0.0)
    total_sodium = Column(Float, nullable=False, default=0.0)
    total_magnesium = Column(Float, nullable=False, default=0.0)
    total_iron = Column(Float, nullable=False, default=0.0)
    total_zinc = Column(Float, nullable=False, default=0.0)
    
    # 主要维生素总量
    total_vitamin_a = Column(Float, nullable=False, default=0.0)  # IU
    total_vitamin_d = Column(Float, nullable=False, default=0.0)  # IU
    total_vitamin_e = Column(Float, nullable=False, default=0.0)  # IU
    total_thiamine = Column(Float, nullable=False, default=0.0)   # mg
    total_riboflavin = Column(Float, nullable=False, default=0.0) # mg
    total_niacin = Column(Float, nullable=False, default=0.0)     # mg
    total_vitamin_b12 = Column(Float, nullable=False, default=0.0) # μg
    total_choline = Column(Float, nullable=False, default=0.0)    # mg
    
    # 必需氨基酸总量 (mg)
    total_arginine = Column(Float, nullable=False, default=0.0)
    total_lysine = Column(Float, nullable=False, default=0.0)
    total_methionine = Column(Float, nullable=False, default=0.0)
    total_taurine = Column(Float, nullable=False, default=0.0)    # 猫咪特需
    
    # 必需脂肪酸总量 (g)
    total_omega_3 = Column(Float, nullable=False, default=0.0)
    total_omega_6 = Column(Float, nullable=False, default=0.0)
    
    # 食谱分析和评估
    nutrition_score = Column(Float, nullable=True)  # 营养评分 (0-100)
    balance_score = Column(Float, nullable=True)    # 平衡评分 (0-100)
    
    # 适用性标记
    suitable_for_dogs = Column(Boolean, nullable=False, default=True)
    suitable_for_cats = Column(Boolean, nullable=False, default=True)
    suitable_for_puppies = Column(Boolean, nullable=False, default=False)
    suitable_for_kittens = Column(Boolean, nullable=False, default=False)
    suitable_for_seniors = Column(Boolean, nullable=False, default=False)
    
    # 食谱状态和标签
    status = Column(Enum(RecipeStatus), nullable=False, default=RecipeStatus.DRAFT)
    is_public = Column(Boolean, nullable=False, default=False)  # 是否公开分享
    tags = Column(Text, nullable=True)  # JSON格式的标签
    
    # 使用统计
    usage_count = Column(Integer, nullable=False, default=0)    # 使用次数
    rating_avg = Column(Float, nullable=True)                  # 平均评分
    rating_count = Column(Integer, nullable=False, default=0)  # 评分次数
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # 关联关系
    user = relationship("User", backref="recipes")
    pet = relationship("Pet", backref="recipes")
    ingredients = relationship("RecipeIngredient", backref="recipe", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    def calculate_nutrition(self):
        """根据食材重量计算总营养成分"""
        # 重置所有营养成分
        self.total_weight = 0.0
        self.total_calories = 0.0
        self.total_protein = 0.0
        self.total_fat = 0.0
        self.total_carbohydrate = 0.0
        self.total_fiber = 0.0
        
        # 矿物质
        self.total_calcium = 0.0
        self.total_phosphorus = 0.0
        self.total_potassium = 0.0
        self.total_sodium = 0.0
        self.total_magnesium = 0.0
        self.total_iron = 0.0
        self.total_zinc = 0.0
        
        # 维生素
        self.total_vitamin_a = 0.0
        self.total_vitamin_d = 0.0
        self.total_vitamin_e = 0.0
        self.total_thiamine = 0.0
        self.total_riboflavin = 0.0
        self.total_niacin = 0.0
        self.total_vitamin_b12 = 0.0
        self.total_choline = 0.0
        
        # 氨基酸
        self.total_arginine = 0.0
        self.total_lysine = 0.0
        self.total_methionine = 0.0
        self.total_taurine = 0.0
        
        # 脂肪酸
        self.total_omega_3 = 0.0
        self.total_omega_6 = 0.0
        
        # 遍历所有食材计算营养成分
        for recipe_ingredient in self.ingredients:
            ingredient = recipe_ingredient.ingredient
            weight_ratio = recipe_ingredient.weight / 100  # 转换为每100g的比例
            
            # 累加基础营养
            self.total_weight += recipe_ingredient.weight
            self.total_calories += ingredient.calories * weight_ratio
            self.total_protein += ingredient.protein * weight_ratio
            self.total_fat += ingredient.fat * weight_ratio
            self.total_carbohydrate += ingredient.carbohydrate * weight_ratio
            self.total_fiber += ingredient.fiber * weight_ratio
            
            # 累加矿物质
            self.total_calcium += ingredient.calcium * weight_ratio
            self.total_phosphorus += ingredient.phosphorus * weight_ratio
            self.total_potassium += ingredient.potassium * weight_ratio
            self.total_sodium += ingredient.sodium * weight_ratio
            self.total_magnesium += ingredient.magnesium * weight_ratio
            self.total_iron += ingredient.iron * weight_ratio
            self.total_zinc += ingredient.zinc * weight_ratio
            
            # 累加维生素
            self.total_vitamin_a += ingredient.vitamin_a * weight_ratio
            self.total_vitamin_d += ingredient.vitamin_d * weight_ratio
            self.total_vitamin_e += ingredient.vitamin_e * weight_ratio
            self.total_thiamine += ingredient.thiamine * weight_ratio
            self.total_riboflavin += ingredient.riboflavin * weight_ratio
            self.total_niacin += ingredient.niacin * weight_ratio
            self.total_vitamin_b12 += ingredient.vitamin_b12 * weight_ratio
            self.total_choline += ingredient.choline * weight_ratio
            
            # 累加氨基酸
            self.total_arginine += ingredient.arginine * weight_ratio
            self.total_lysine += ingredient.lysine * weight_ratio
            self.total_methionine += ingredient.methionine * weight_ratio
            self.total_taurine += ingredient.taurine * weight_ratio
            
            # 累加脂肪酸
            self.total_omega_3 += ingredient.omega_3_fatty_acids * weight_ratio
            self.total_omega_6 += ingredient.omega_6_fatty_acids * weight_ratio
    
    def check_suitability(self):
        """检查食谱对不同宠物的适用性"""
        # 检查所有食材是否对特定宠物安全
        for recipe_ingredient in self.ingredients:
            ingredient = recipe_ingredient.ingredient
            if not ingredient.is_safe_for_dogs:
                self.suitable_for_dogs = False
            if not ingredient.is_safe_for_cats:
                self.suitable_for_cats = False
    
    def get_nutrition_per_100g(self):
        """获取每100g的营养成分"""
        if self.total_weight == 0:
            return {}
        
        ratio = 100 / self.total_weight
        return {
            'calories': self.total_calories * ratio,
            'protein': self.total_protein * ratio,
            'fat': self.total_fat * ratio,
            'carbohydrate': self.total_carbohydrate * ratio,
            'fiber': self.total_fiber * ratio,
            'calcium': self.total_calcium * ratio,
            'phosphorus': self.total_phosphorus * ratio,
            'vitamin_a': self.total_vitamin_a * ratio,
            'vitamin_d': self.total_vitamin_d * ratio,
            'taurine': self.total_taurine * ratio,
            # ... 其他营养素
        }
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'pet_id': self.pet_id,
            'total_weight': self.total_weight,
            'nutrition': {
                'calories': self.total_calories,
                'protein': self.total_protein,
                'fat': self.total_fat,
                'carbohydrate': self.total_carbohydrate,
                'fiber': self.total_fiber,
                'calcium': self.total_calcium,
                'phosphorus': self.total_phosphorus,
                'vitamin_a': self.total_vitamin_a,
                'taurine': self.total_taurine,
                'omega_3': self.total_omega_3,
                'omega_6': self.total_omega_6
            },
            'suitability': {
                'dogs': self.suitable_for_dogs,
                'cats': self.suitable_for_cats,
                'puppies': self.suitable_for_puppies,
                'kittens': self.suitable_for_kittens,
                'seniors': self.suitable_for_seniors
            },
            'status': self.status.value,
            'is_public': self.is_public,
            'nutrition_score': self.nutrition_score,
            'balance_score': self.balance_score,
            'usage_count': self.usage_count,
            'rating_avg': self.rating_avg,
            'rating_count': self.rating_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'ingredients': [ri.to_dict() for ri in self.ingredients]
        }