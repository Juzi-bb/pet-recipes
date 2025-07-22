from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Enum
from ..extensions import db  # 使用相对导入
from datetime import datetime
import enum

class PetType(enum.Enum):
    DOG = "dog"
    CAT = "cat"

class LifeStage(enum.Enum):
    PUPPY_KITTEN = "puppy_kitten"        # 幼犬/幼猫
    ADULT = "adult"                      # 成犬/成猫
    SENIOR = "senior"                    # 老年犬/老年猫
    PREGNANT = "pregnant"                # 怀孕期
    LACTATING = "lactating"              # 哺乳期
    LARGE_BREED_PUPPY = "large_breed_puppy"  # 大型犬幼犬

class ActivityLevel(enum.Enum):
    LOW = "low"           # 低活动量
    MODERATE = "moderate"  # 中等活动量
    HIGH = "high"         # 高活动量

class NutritionRequirement(db.Model):
    __tablename__ = 'nutrition_requirements'
    
    # 基础信息
    id = Column(Integer, primary_key=True)
    pet_type = Column(Enum(PetType), nullable=False)
    life_stage = Column(Enum(LifeStage), nullable=False)
    activity_level = Column(Enum(ActivityLevel), nullable=False, default=ActivityLevel.MODERATE)
    
    # 体重范围 (kg)
    min_weight = Column(Float, nullable=False, default=0.0)
    max_weight = Column(Float, nullable=False, default=100.0)
    
    # 每日能量需求 (kcal/kg体重)
    calories_per_kg = Column(Float, nullable=False)
    
    # 基础营养素需求 (最小值, 干物质基础)
    # 宏量营养素 (%)
    protein_min = Column(Float, nullable=False)  # 蛋白质最小值
    protein_max = Column(Float, nullable=True)   # 蛋白质最大值 (如有)
    fat_min = Column(Float, nullable=False)      # 脂肪最小值
    fat_max = Column(Float, nullable=True)       # 脂肪最大值 (如有)
    carbohydrate_max = Column(Float, nullable=True)  # 碳水化合物最大值
    fiber_min = Column(Float, nullable=True)     # 纤维最小值
    fiber_max = Column(Float, nullable=True)     # 纤维最大值
    
    # 矿物质需求 (mg/kg干物质)
    calcium_min = Column(Float, nullable=False)
    calcium_max = Column(Float, nullable=True)
    phosphorus_min = Column(Float, nullable=False)
    phosphorus_max = Column(Float, nullable=True)
    potassium_min = Column(Float, nullable=False)
    sodium_min = Column(Float, nullable=False)
    sodium_max = Column(Float, nullable=True)
    chloride_min = Column(Float, nullable=False)
    magnesium_min = Column(Float, nullable=False)
    iron_min = Column(Float, nullable=False)
    iron_max = Column(Float, nullable=True)
    copper_min = Column(Float, nullable=False)
    copper_max = Column(Float, nullable=True)
    manganese_min = Column(Float, nullable=False)
    manganese_max = Column(Float, nullable=True)
    zinc_min = Column(Float, nullable=False)
    zinc_max = Column(Float, nullable=True)
    iodine_min = Column(Float, nullable=False)
    iodine_max = Column(Float, nullable=True)
    selenium_min = Column(Float, nullable=False)
    selenium_max = Column(Float, nullable=True)
    
    # 维生素需求
    # 脂溶性维生素
    vitamin_a_min = Column(Float, nullable=False)  # IU/kg
    vitamin_a_max = Column(Float, nullable=True)
    vitamin_d_min = Column(Float, nullable=False)  # IU/kg
    vitamin_d_max = Column(Float, nullable=True)
    vitamin_e_min = Column(Float, nullable=False)  # IU/kg
    vitamin_k_min = Column(Float, nullable=True)   # mg/kg
    
    # 水溶性维生素 (mg/kg)
    thiamine_min = Column(Float, nullable=False)
    riboflavin_min = Column(Float, nullable=False)
    niacin_min = Column(Float, nullable=False)
    pantothenic_acid_min = Column(Float, nullable=False)
    pyridoxine_min = Column(Float, nullable=False)
    folic_acid_min = Column(Float, nullable=False)
    vitamin_b12_min = Column(Float, nullable=False)  # μg/kg
    biotin_min = Column(Float, nullable=True)        # μg/kg
    choline_min = Column(Float, nullable=False)      # mg/kg
    
    # 必需氨基酸需求 (% of protein)
    arginine_min = Column(Float, nullable=False)
    histidine_min = Column(Float, nullable=False)
    isoleucine_min = Column(Float, nullable=False)
    leucine_min = Column(Float, nullable=False)
    lysine_min = Column(Float, nullable=False)
    methionine_min = Column(Float, nullable=False)
    phenylalanine_min = Column(Float, nullable=False)
    threonine_min = Column(Float, nullable=False)
    tryptophan_min = Column(Float, nullable=False)
    valine_min = Column(Float, nullable=False)
    
    # 猫咪特需营养素
    taurine_min = Column(Float, nullable=True)  # mg/kg (仅猫咪)
    
    # 必需脂肪酸需求 (% of dry matter)
    alpha_linolenic_acid_min = Column(Float, nullable=True)  # ALA
    epa_dha_min = Column(Float, nullable=True)              # EPA + DHA
    arachidonic_acid_min = Column(Float, nullable=True)     # 花生四烯酸 (仅猫咪)
    
    # 特殊比例要求
    calcium_phosphorus_ratio_min = Column(Float, nullable=True)  # 钙磷比最小值
    calcium_phosphorus_ratio_max = Column(Float, nullable=True)  # 钙磷比最大值
    
    # 数据来源和说明
    standard_source = Column(String(100), nullable=False, default="AAFCO")  # 标准来源
    notes = Column(Text, nullable=True)  # 特殊说明
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<NutritionRequirement(pet_type={self.pet_type}, life_stage={self.life_stage}, activity={self.activity_level})>"
    
    def calculate_daily_requirements(self, pet_weight_kg):
        """计算特定体重宠物的每日营养需求"""
        if not (self.min_weight <= pet_weight_kg <= self.max_weight):
            raise ValueError(f"宠物体重 {pet_weight_kg}kg 超出适用范围 ({self.min_weight}-{self.max_weight}kg)")
        
        # 计算每日热量需求
        daily_calories = self.calories_per_kg * pet_weight_kg
        
        # 假设食物含水量为10%，计算干物质需求
        dry_matter_needed = daily_calories / 4000  # 假设每kg干物质约4000kcal
        
        return {
            'daily_calories': daily_calories,
            'dry_matter_needed_kg': dry_matter_needed,
            'protein_min_g': (self.protein_min / 100) * dry_matter_needed * 1000,
            'fat_min_g': (self.fat_min / 100) * dry_matter_needed * 1000,
            'calcium_min_mg': self.calcium_min * dry_matter_needed,
            'phosphorus_min_mg': self.phosphorus_min * dry_matter_needed,
            'vitamin_a_min_iu': self.vitamin_a_min * dry_matter_needed,
            'vitamin_d_min_iu': self.vitamin_d_min * dry_matter_needed,
            'taurine_min_mg': self.taurine_min * dry_matter_needed if self.taurine_min else 0,
            # ... 其他营养素
        }
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'pet_type': self.pet_type.value,
            'life_stage': self.life_stage.value,
            'activity_level': self.activity_level.value,
            'weight_range': {
                'min': self.min_weight,
                'max': self.max_weight
            },
            'calories_per_kg': self.calories_per_kg,
            'macronutrients': {
                'protein': {'min': self.protein_min, 'max': self.protein_max},
                'fat': {'min': self.fat_min, 'max': self.fat_max},
                'carbohydrate': {'max': self.carbohydrate_max},
                'fiber': {'min': self.fiber_min, 'max': self.fiber_max}
            },
            'minerals': {
                'calcium': {'min': self.calcium_min, 'max': self.calcium_max},
                'phosphorus': {'min': self.phosphorus_min, 'max': self.phosphorus_max},
                'potassium': {'min': self.potassium_min},
                'sodium': {'min': self.sodium_min, 'max': self.sodium_max},
                'iron': {'min': self.iron_min, 'max': self.iron_max},
                'zinc': {'min': self.zinc_min, 'max': self.zinc_max},
                'copper': {'min': self.copper_min, 'max': self.copper_max}
            },
            'vitamins': {
                'vitamin_a': {'min': self.vitamin_a_min, 'max': self.vitamin_a_max},
                'vitamin_d': {'min': self.vitamin_d_min, 'max': self.vitamin_d_max},
                'vitamin_e': {'min': self.vitamin_e_min},
                'thiamine': {'min': self.thiamine_min},
                'riboflavin': {'min': self.riboflavin_min},
                'niacin': {'min': self.niacin_min},
                'vitamin_b12': {'min': self.vitamin_b12_min},
                'choline': {'min': self.choline_min}
            },
            'amino_acids': {
                'arginine': {'min': self.arginine_min},
                'lysine': {'min': self.lysine_min},
                'methionine': {'min': self.methionine_min},
                'taurine': {'min': self.taurine_min}
            },
            'fatty_acids': {
                'alpha_linolenic_acid': {'min': self.alpha_linolenic_acid_min},
                'epa_dha': {'min': self.epa_dha_min},
                'arachidonic_acid': {'min': self.arachidonic_acid_min}
            },
            'ratios': {
                'calcium_phosphorus': {
                    'min': self.calcium_phosphorus_ratio_min,
                    'max': self.calcium_phosphorus_ratio_max
                }
            },
            'standard_source': self.standard_source,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
    
    @classmethod
    def get_requirement_for_pet(cls, session, pet_type, life_stage, activity_level, weight_kg):
        """获取特定宠物的营养需求"""
        requirement = session.query(cls).filter(
            cls.pet_type == pet_type,
            cls.life_stage == life_stage,
            cls.activity_level == activity_level,
            cls.min_weight <= weight_kg,
            cls.max_weight >= weight_kg,
            cls.is_active == True
        ).first()
        
        if requirement:
            return requirement.calculate_daily_requirements(weight_kg)
        return None