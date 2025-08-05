from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Enum
from datetime import datetime
from ..extensions import db
import enum

class IngredientCategory(enum.Enum):
    RED_MEAT = "red_meat"           # 红肉
    WHITE_MEAT = "white_meat"       # 白肉
    FISH = "fish"                   # 鱼类
    ORGANS = "organs"               # 内脏
    VEGETABLES = "vegetables"       # 蔬菜
    FRUITS = "fruits"               # 水果
    GRAINS = "grains"               # 谷物
    DAIRY = "dairy"                 # 乳制品
    SUPPLEMENTS = "supplements"     # 营养补充剂
    OILS = "oils"                   # 油脂类
    DANGEROUS = "dangerous"         # 危险食材 - 新添加的分类

class Ingredient(db.Model):  # ------- 修改：继承db.Model而不是Base -------
    __tablename__ = 'ingredients'
    
    # 基础信息
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    name_en = Column(String(100), nullable=True)
    category = Column(Enum(IngredientCategory), nullable=False)

    # ------- 新增：缺失的字段 -------
    image_filename = Column(String(255), nullable=True)  # 图片文件名
    seasonality = Column(String(100), nullable=True)     # 季节性
    
    # 基本营养成分 (每100g)
    # 基础宏量营养素
    calories = Column(Float, nullable=False, default=0.0)  # 千卡
    protein = Column(Float, nullable=False, default=0.0)   # 蛋白质 (g)
    fat = Column(Float, nullable=False, default=0.0)       # 脂肪 (g)
    carbohydrate = Column(Float, nullable=False, default=0.0)  # 碳水化合物 (g)
    fiber = Column(Float, nullable=False, default=0.0)     # 纤维 (g)
    moisture = Column(Float, nullable=False, default=0.0)  # 水分 (g)
    ash = Column(Float, nullable=False, default=0.0)       # 灰分 (g)
    
    # 主要矿物质 (mg/100g) - 基于AAFCO标准
    calcium = Column(Float, nullable=False, default=0.0)     # 钙
    phosphorus = Column(Float, nullable=False, default=0.0)  # 磷
    potassium = Column(Float, nullable=False, default=0.0)   # 钾
    sodium = Column(Float, nullable=False, default=0.0)      # 钠
    chloride = Column(Float, nullable=False, default=0.0)    # 氯
    magnesium = Column(Float, nullable=False, default=0.0)   # 镁
    iron = Column(Float, nullable=False, default=0.0)        # 铁
    copper = Column(Float, nullable=False, default=0.0)      # 铜
    manganese = Column(Float, nullable=False, default=0.0)   # 锰
    zinc = Column(Float, nullable=False, default=0.0)        # 锌
    iodine = Column(Float, nullable=False, default=0.0)      # 碘
    selenium = Column(Float, nullable=False, default=0.0)    # 硒
    
    # 维生素 - 基于AAFCO标准
    # 脂溶性维生素
    vitamin_a = Column(Float, nullable=False, default=0.0)   # 维生素A (IU/100g)
    vitamin_d = Column(Float, nullable=False, default=0.0)   # 维生素D (IU/100g)
    vitamin_e = Column(Float, nullable=False, default=0.0)   # 维生素E (IU/100g)
    vitamin_k = Column(Float, nullable=False, default=0.0)   # 维生素K (mg/100g)
    
    # 水溶性维生素 (mg/100g)
    thiamine = Column(Float, nullable=False, default=0.0)    # 维生素B1 (硫胺素)
    riboflavin = Column(Float, nullable=False, default=0.0)  # 维生素B2 (核黄素)
    niacin = Column(Float, nullable=False, default=0.0)      # 维生素B3 (烟酸)
    pantothenic_acid = Column(Float, nullable=False, default=0.0)  # 维生素B5 (泛酸)
    pyridoxine = Column(Float, nullable=False, default=0.0)  # 维生素B6 (吡哆醇)
    folic_acid = Column(Float, nullable=False, default=0.0)  # 叶酸
    vitamin_b12 = Column(Float, nullable=False, default=0.0) # 维生素B12 (μg/100g)
    biotin = Column(Float, nullable=False, default=0.0)      # 生物素 (μg/100g)
    choline = Column(Float, nullable=False, default=0.0)     # 胆碱 (mg/100g)
    
    # 必需氨基酸 (mg/100g) - 基于AAFCO标准
    arginine = Column(Float, nullable=False, default=0.0)    # 精氨酸
    histidine = Column(Float, nullable=False, default=0.0)   # 组氨酸
    isoleucine = Column(Float, nullable=False, default=0.0)  # 异亮氨酸
    leucine = Column(Float, nullable=False, default=0.0)     # 亮氨酸
    lysine = Column(Float, nullable=False, default=0.0)      # 赖氨酸
    methionine = Column(Float, nullable=False, default=0.0)  # 蛋氨酸
    phenylalanine = Column(Float, nullable=False, default=0.0)  # 苯丙氨酸
    threonine = Column(Float, nullable=False, default=0.0)   # 苏氨酸
    tryptophan = Column(Float, nullable=False, default=0.0)  # 色氨酸
    valine = Column(Float, nullable=False, default=0.0)      # 缬氨酸
    
    # 猫咪特需氨基酸
    taurine = Column(Float, nullable=False, default=0.0)     # 牛磺酸 (mg/100g)
    
    # 必需脂肪酸 (g/100g) - 基于AAFCO 2016更新
    alpha_linolenic_acid = Column(Float, nullable=False, default=0.0)  # α-亚麻酸 (ALA)
    eicosapentaenoic_acid = Column(Float, nullable=False, default=0.0)  # EPA
    docosahexaenoic_acid = Column(Float, nullable=False, default=0.0)   # DHA
    arachidonic_acid = Column(Float, nullable=False, default=0.0)       # 花生四烯酸 (猫咪必需)
    
    # 其他重要营养素
    omega_3_fatty_acids = Column(Float, nullable=False, default=0.0)  # Omega-3脂肪酸总量
    omega_6_fatty_acids = Column(Float, nullable=False, default=0.0)  # Omega-6脂肪酸总量
    
    # 食材特性
    is_safe_for_dogs = Column(Boolean, nullable=False, default=True)
    is_safe_for_cats = Column(Boolean, nullable=False, default=True)
    is_common_allergen = Column(Boolean, nullable=False, default=False)
    
    # 食材处理和保存信息
    description = Column(Text, nullable=True)        # 描述
    benefits = Column(Text, nullable=True)           # 功效
    preparation_method = Column(Text, nullable=True) # 处理方式
    pro_tip = Column(Text, nullable=True)            # 温馨提示 (Good to know)
    allergy_alert = Column(Text, nullable=True)      # 过敏提示
    storage_notes = Column(Text, nullable=True)      # 储存说明
    
    # 数据来源和验证
    data_source = Column(String(200), nullable=True)  # 数据来源
    last_verified = Column(DateTime, nullable=True)   # 最后验证时间
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}', category={self.category})>"
    
    def to_dict(self):
        """转换为字典格式，方便JSON序列化"""
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'category': self.category.value if self.category else None,
            'description': self.description,
            'image_filename': self.image_filename,
            'seasonality': self.seasonality,
            'nutrition': {
                'basic': {
                    'calories': self.calories,
                    'protein': self.protein,
                    'fat': self.fat,
                    'carbohydrate': self.carbohydrate,
                    'fiber': self.fiber,
                    'moisture': self.moisture,
                    'ash': self.ash
                },
                'minerals': {
                    'calcium': self.calcium,
                    'phosphorus': self.phosphorus,
                    'potassium': self.potassium,
                    'sodium': self.sodium,
                    'chloride': self.chloride,
                    'magnesium': self.magnesium,
                    'iron': self.iron,
                    'copper': self.copper,
                    'manganese': self.manganese,
                    'zinc': self.zinc,
                    'iodine': self.iodine,
                    'selenium': self.selenium
                },
                'vitamins': {
                    'vitamin_a': self.vitamin_a,
                    'vitamin_d': self.vitamin_d,
                    'vitamin_e': self.vitamin_e,
                    'vitamin_k': self.vitamin_k,
                    'thiamine': self.thiamine,
                    'riboflavin': self.riboflavin,
                    'niacin': self.niacin,
                    'pantothenic_acid': self.pantothenic_acid,
                    'pyridoxine': self.pyridoxine,
                    'folic_acid': self.folic_acid,
                    'vitamin_b12': self.vitamin_b12,
                    'biotin': self.biotin,
                    'choline': self.choline
                },
                'amino_acids': {
                    'arginine': self.arginine,
                    'histidine': self.histidine,
                    'isoleucine': self.isoleucine,
                    'leucine': self.leucine,
                    'lysine': self.lysine,
                    'methionine': self.methionine,
                    'phenylalanine': self.phenylalanine,
                    'threonine': self.threonine,
                    'tryptophan': self.tryptophan,
                    'valine': self.valine,
                    'taurine': self.taurine
                },
                'fatty_acids': {
                    'alpha_linolenic_acid': self.alpha_linolenic_acid,
                    'eicosapentaenoic_acid': self.eicosapentaenoic_acid,
                    'docosahexaenoic_acid': self.docosahexaenoic_acid,
                    'arachidonic_acid': self.arachidonic_acid,
                    'omega_3_fatty_acids': self.omega_3_fatty_acids,
                    'omega_6_fatty_acids': self.omega_6_fatty_acids
                }
            },
            'safety': {
                'is_safe_for_dogs': self.is_safe_for_dogs,
                'is_safe_for_cats': self.is_safe_for_cats,
                'is_common_allergen': self.is_common_allergen
            },
            # 新增：食材百科相关信息
            'food_guide': {
                'benefits': self.benefits,
                'preparation_method': self.preparation_method,
                'pro_tip': self.pro_tip,
                'allergy_alert': self.allergy_alert,
                'storage_notes': self.storage_notes
            },

            # 修复字段名
            'data_source': self.data_source,
            'last_verified': self.last_verified.isoformat() if self.last_verified else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
    
    def get_nutrition_per_gram(self):
        """获取每克的营养成分"""
        return {
            'calories': self.calories / 100,
            'protein': self.protein / 100,
            'fat': self.fat / 100,
            'carbohydrate': self.carbohydrate / 100,
            'fiber': self.fiber / 100,
            'calcium': self.calcium / 100,
            'phosphorus': self.phosphorus / 100,
            # ... 其他营养素也类似处理
        }
    
    def is_suitable_for_pet(self, pet_type):
        """检查食材是否适合特定宠物"""
        if pet_type.lower() == 'dog':
            return self.is_safe_for_dogs
        elif pet_type.lower() == 'cat':
            return self.is_safe_for_cats
        return False