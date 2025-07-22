# 食谱-食材关联模型
# 处理食谱中食材的重量和营养贡献
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    
    # 基础信息
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    
    # 用量信息
    weight = Column(Float, nullable=False)  # 重量 (g)
    percentage = Column(Float, nullable=True)  # 在食谱中的百分比
    
    # 食材在食谱中的说明
    preparation_note = Column(Text, nullable=True)  # 制备说明 (如：切丁、煮熟等)
    
    # 营养贡献 (缓存字段，用于快速查询)
    contributed_calories = Column(Float, nullable=False, default=0.0)  # 贡献的热量
    contributed_protein = Column(Float, nullable=False, default=0.0)   # 贡献的蛋白质
    contributed_fat = Column(Float, nullable=False, default=0.0)       # 贡献的脂肪
    contributed_carbohydrate = Column(Float, nullable=False, default=0.0)  # 贡献的碳水化合物
    contributed_calcium = Column(Float, nullable=False, default=0.0)   # 贡献的钙
    contributed_phosphorus = Column(Float, nullable=False, default=0.0)  # 贡献的磷
    
    # 排序字段
    display_order = Column(Integer, nullable=False, default=0)  # 显示顺序
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    ingredient = relationship("Ingredient", backref="recipe_uses")
    
    # 约束：同一食谱中不能重复添加相同食材
    __table_args__ = (
        UniqueConstraint('recipe_id', 'ingredient_id', name='unique_recipe_ingredient'),
    )
    
    def __repr__(self):
        return f"<RecipeIngredient(recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id}, weight={self.weight}g)>"
    
    def calculate_nutrition_contribution(self):
        """计算该食材在食谱中的营养贡献"""
        if not self.ingredient:
            return
        
        # 计算每克的营养成分
        weight_ratio = self.weight / 100  # 转换为每100g的比例
        
        # 计算营养贡献
        self.contributed_calories = self.ingredient.calories * weight_ratio
        self.contributed_protein = self.ingredient.protein * weight_ratio
        self.contributed_fat = self.ingredient.fat * weight_ratio
        self.contributed_carbohydrate = self.ingredient.carbohydrate * weight_ratio
        self.contributed_calcium = self.ingredient.calcium * weight_ratio
        self.contributed_phosphorus = self.ingredient.phosphorus * weight_ratio
    
    def get_detailed_nutrition_contribution(self):
        """获取详细的营养贡献信息"""
        if not self.ingredient:
            return {}
        
        weight_ratio = self.weight / 100
        
        return {
            'basic': {
                'calories': self.ingredient.calories * weight_ratio,
                'protein': self.ingredient.protein * weight_ratio,
                'fat': self.ingredient.fat * weight_ratio,
                'carbohydrate': self.ingredient.carbohydrate * weight_ratio,
                'fiber': self.ingredient.fiber * weight_ratio,
                'moisture': self.ingredient.moisture * weight_ratio,
                'ash': self.ingredient.ash * weight_ratio
            },
            'minerals': {
                'calcium': self.ingredient.calcium * weight_ratio,
                'phosphorus': self.ingredient.phosphorus * weight_ratio,
                'potassium': self.ingredient.potassium * weight_ratio,
                'sodium': self.ingredient.sodium * weight_ratio,
                'chloride': self.ingredient.chloride * weight_ratio,
                'magnesium': self.ingredient.magnesium * weight_ratio,
                'iron': self.ingredient.iron * weight_ratio,
                'copper': self.ingredient.copper * weight_ratio,
                'manganese': self.ingredient.manganese * weight_ratio,
                'zinc': self.ingredient.zinc * weight_ratio,
                'iodine': self.ingredient.iodine * weight_ratio,
                'selenium': self.ingredient.selenium * weight_ratio
            },
            'vitamins': {
                'vitamin_a': self.ingredient.vitamin_a * weight_ratio,
                'vitamin_d': self.ingredient.vitamin_d * weight_ratio,
                'vitamin_e': self.ingredient.vitamin_e * weight_ratio,
                'vitamin_k': self.ingredient.vitamin_k * weight_ratio,
                'thiamine': self.ingredient.thiamine * weight_ratio,
                'riboflavin': self.ingredient.riboflavin * weight_ratio,
                'niacin': self.ingredient.niacin * weight_ratio,
                'pantothenic_acid': self.ingredient.pantothenic_acid * weight_ratio,
                'pyridoxine': self.ingredient.pyridoxine * weight_ratio,
                'folic_acid': self.ingredient.folic_acid * weight_ratio,
                'vitamin_b12': self.ingredient.vitamin_b12 * weight_ratio,
                'biotin': self.ingredient.biotin * weight_ratio,
                'choline': self.ingredient.choline * weight_ratio
            },
            'amino_acids': {
                'arginine': self.ingredient.arginine * weight_ratio,
                'histidine': self.ingredient.histidine * weight_ratio,
                'isoleucine': self.ingredient.isoleucine * weight_ratio,
                'leucine': self.ingredient.leucine * weight_ratio,
                'lysine': self.ingredient.lysine * weight_ratio,
                'methionine': self.ingredient.methionine * weight_ratio,
                'phenylalanine': self.ingredient.phenylalanine * weight_ratio,
                'threonine': self.ingredient.threonine * weight_ratio,
                'tryptophan': self.ingredient.tryptophan * weight_ratio,
                'valine': self.ingredient.valine * weight_ratio,
                'taurine': self.ingredient.taurine * weight_ratio
            },
            'fatty_acids': {
                'alpha_linolenic_acid': self.ingredient.alpha_linolenic_acid * weight_ratio,
                'eicosapentaenoic_acid': self.ingredient.eicosapentaenoic_acid * weight_ratio,
                'docosahexaenoic_acid': self.ingredient.docosahexaenoic_acid * weight_ratio,
                'arachidonic_acid': self.ingredient.arachidonic_acid * weight_ratio,
                'omega_3_fatty_acids': self.ingredient.omega_3_fatty_acids * weight_ratio,
                'omega_6_fatty_acids': self.ingredient.omega_6_fatty_acids * weight_ratio
            }
        }
    
    def update_percentage(self, total_weight):
        """更新在食谱中的重量百分比"""
        if total_weight > 0:
            self.percentage = (self.weight / total_weight) * 100
        else:
            self.percentage = 0
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'weight': self.weight,
            'percentage': self.percentage,
            'preparation_note': self.preparation_note,
            'nutrition_contribution': {
                'calories': self.contributed_calories,
                'protein': self.contributed_protein,
                'fat': self.contributed_fat,
                'carbohydrate': self.contributed_carbohydrate,
                'calcium': self.contributed_calcium,
                'phosphorus': self.contributed_phosphorus
            },
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def create_from_data(cls, recipe_id, ingredient_id, weight, preparation_note=None, display_order=0):
        """从数据创建RecipeIngredient实例"""
        recipe_ingredient = cls(
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
            weight=weight,
            preparation_note=preparation_note,
            display_order=display_order
        )
        
        # 计算营养贡献
        recipe_ingredient.calculate_nutrition_contribution()
        
        return recipe_ingredient
    
    def is_valid_weight(self):
        """检查重量是否有效"""
        return self.weight > 0 and self.weight <= 2000  # 最大2kg
    
    def get_cost_per_serving(self, ingredient_cost_per_kg=None):
        """计算每份的成本 (如果提供了食材价格)"""
        if ingredient_cost_per_kg is None:
            return None
        
        return (self.weight / 1000) * ingredient_cost_per_kg
    
    def get_preparation_instructions(self):
        """获取制备说明"""
        if self.preparation_note:
            return self.preparation_note
        
        # 根据食材类型提供默认说明
        if self.ingredient:
            if self.ingredient.category.value in ['red_meat', 'white_meat']:
                return "切块煮熟或蒸熟"
            elif self.ingredient.category.value == 'fish':
                return "去骨去皮，蒸煮至熟"
            elif self.ingredient.category.value == 'vegetables':
                return "洗净切块，蒸煮至软烂"
            elif self.ingredient.category.value == 'organs':
                return "清洗干净，煮熟切小块"
            elif self.ingredient.category.value == 'grains':
                return "煮熟至软烂"
            elif self.ingredient.category.value == 'fruits':
                return "洗净去皮去核，切小块"
        
        return "按常规方法处理"