"""
营养比例配置系统
提供不同宠物类型和特殊需求的营养比例预设方案
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class NutritionProfile(Enum):
    """营养配置方案类型"""
    BASIC_DOG = "basic_dog"                 # 基础成犬配方
    BASIC_CAT = "basic_cat"                 # 基础成猫配方
    ACTIVE_DOG = "active_dog"               # 活跃成犬配方
    SENIOR_DOG = "senior_dog"               # 老年犬配方
    SENIOR_CAT = "senior_cat"               # 老年猫配方
    WEIGHT_LOSS = "weight_loss"             # 减重配方
    KIDNEY_SUPPORT = "kidney_support"       # 肾脏支持配方
    COAT_HEALTH = "coat_health"             # 美毛配方
    ALLERGY_FRIENDLY = "allergy_friendly"   # 低敏配方

@dataclass
class CategoryRatio:
    """食材分类比例"""
    red_meat: float = 0.0      # 红肉比例
    white_meat: float = 0.0    # 白肉比例
    fish: float = 0.0          # 鱼类比例
    organs: float = 0.0        # 内脏比例
    vegetables: float = 0.0    # 蔬菜比例
    fruits: float = 0.0        # 水果比例
    grains: float = 0.0        # 谷物比例
    
    def total_protein_sources(self) -> float:
        """计算蛋白质来源总比例"""
        return self.red_meat + self.white_meat + self.fish + self.organs
    
    def validate(self) -> bool:
        """验证比例总和是否为100%"""
        total = (self.red_meat + self.white_meat + self.fish + self.organs + 
                self.vegetables + self.fruits + self.grains)
        return abs(total - 1.0) < 0.01  # 允许1%的误差

@dataclass
class NutritionTarget:
    """营养目标值"""
    protein_min: float     # 蛋白质最小百分比
    protein_max: float     # 蛋白质最大百分比
    fat_min: float         # 脂肪最小百分比
    fat_max: float         # 脂肪最大百分比
    carb_max: float        # 碳水最大百分比
    calcium_phosphorus_ratio_min: float = 1.0   # 钙磷比最小值
    calcium_phosphorus_ratio_max: float = 2.0   # 钙磷比最大值
    calories_per_kg: float = 95  # 每公斤体重所需热量

@dataclass
class NutritionPlan:
    """完整营养方案"""
    name: str
    description: str
    category_ratios: CategoryRatio
    nutrition_targets: NutritionTarget
    special_notes: List[str]
    
class NutritionRatioService:
    """营养比例服务类"""
    
    # 预设营养方案
    NUTRITION_PLANS = {
        NutritionProfile.BASIC_DOG: NutritionPlan(
            name="基础成犬配方",
            description="适合健康成年犬的均衡营养配方",
            category_ratios=CategoryRatio(
                red_meat=0.35,      # 35% 红肉
                white_meat=0.25,    # 25% 白肉  
                fish=0.10,          # 10% 鱼类
                organs=0.05,        # 5% 内脏
                vegetables=0.15,    # 15% 蔬菜
                fruits=0.05,        # 5% 水果
                grains=0.05         # 5% 谷物
            ),
            nutrition_targets=NutritionTarget(
                protein_min=18.0, protein_max=30.0,
                fat_min=5.5, fat_max=15.0,
                carb_max=25.0,
                calories_per_kg=95
            ),
            special_notes=["适合1-7岁健康成犬", "维持体重和日常活动"]
        ),
        
        NutritionProfile.BASIC_CAT: NutritionPlan(
            name="基础成猫配方", 
            description="适合健康成年猫的高蛋白配方",
            category_ratios=CategoryRatio(
                red_meat=0.20,      # 20% 红肉
                white_meat=0.35,    # 35% 白肉
                fish=0.25,          # 25% 鱼类
                organs=0.10,        # 10% 内脏
                vegetables=0.08,    # 8% 蔬菜
                fruits=0.02,        # 2% 水果
                grains=0.00         # 0% 谷物（猫咪不需要谷物）
            ),
            nutrition_targets=NutritionTarget(
                protein_min=26.0, protein_max=45.0,
                fat_min=9.0, fat_max=20.0,
                carb_max=10.0,
                calories_per_kg=85
            ),
            special_notes=["猫咪为肉食动物，需要高蛋白", "必须添加牛磺酸"]
        ),
        
        NutritionProfile.ACTIVE_DOG: NutritionPlan(
            name="活跃犬配方",
            description="适合运动量大、工作犬的高能量配方", 
            category_ratios=CategoryRatio(
                red_meat=0.40,      # 40% 红肉
                white_meat=0.25,    # 25% 白肉
                fish=0.10,          # 10% 鱼类
                organs=0.05,        # 5% 内脏
                vegetables=0.12,    # 12% 蔬菜
                fruits=0.03,        # 3% 水果
                grains=0.05         # 5% 谷物
            ),
            nutrition_targets=NutritionTarget(
                protein_min=22.0, protein_max=35.0,
                fat_min=8.0, fat_max=18.0,
                carb_max=20.0,
                calories_per_kg=130  # 更高热量需求
            ),
            special_notes=["适合工作犬、运动犬", "增加脂肪和蛋白质摄入"]
        ),
        
        NutritionProfile.SENIOR_DOG: NutritionPlan(
            name="老年犬配方",
            description="适合7岁以上老年犬的易消化配方",
            category_ratios=CategoryRatio(
                red_meat=0.25,      # 25% 红肉（减少）
                white_meat=0.35,    # 35% 白肉（增加，易消化）
                fish=0.15,          # 15% 鱼类（omega-3）
                organs=0.05,        # 5% 内脏
                vegetables=0.15,    # 15% 蔬菜
                fruits=0.05,        # 5% 水果
                grains=0.00         # 0% 谷物（减少碳水）
            ),
            nutrition_targets=NutritionTarget(
                protein_min=18.0, protein_max=25.0,
                fat_min=5.5, fat_max=12.0,
                carb_max=15.0,
                calories_per_kg=80  # 降低热量
            ),
            special_notes=["易消化蛋白质", "增加omega-3脂肪酸", "减少热量摄入"]
        ),
        
        NutritionProfile.WEIGHT_LOSS: NutritionPlan(
            name="减重配方",
            description="适合需要减重的超重宠物",
            category_ratios=CategoryRatio(
                red_meat=0.15,      # 15% 红肉（减少脂肪）
                white_meat=0.45,    # 45% 白肉（高蛋白低脂）
                fish=0.15,          # 15% 鱼类
                organs=0.05,        # 5% 内脏
                vegetables=0.20,    # 20% 蔬菜（增加纤维）
                fruits=0.00,        # 0% 水果（减少糖分）
                grains=0.00         # 0% 谷物
            ),
            nutrition_targets=NutritionTarget(
                protein_min=22.0, protein_max=30.0,
                fat_min=3.0, fat_max=8.0,   # 低脂肪
                carb_max=10.0,
                calories_per_kg=70  # 低热量
            ),
            special_notes=["高蛋白低脂肪", "增加饱腹感", "严格控制热量"]
        ),
        
        NutritionProfile.KIDNEY_SUPPORT: NutritionPlan(
            name="肾脏支持配方",
            description="适合肾病宠物的低蛋白、低磷配方",
            category_ratios=CategoryRatio(
                red_meat=0.15,      # 15% 红肉（减少）
                white_meat=0.30,    # 30% 白肉
                fish=0.10,          # 10% 鱼类
                organs=0.00,        # 0% 内脏（高磷）
                vegetables=0.30,    # 30% 蔬菜
                fruits=0.10,        # 10% 水果
                grains=0.05         # 5% 谷物
            ),
            nutrition_targets=NutritionTarget(
                protein_min=14.0, protein_max=18.0,  # 低蛋白
                fat_min=5.5, fat_max=12.0,
                carb_max=30.0,
                calories_per_kg=85
            ),
            special_notes=["限制蛋白质和磷", "需要兽医监督", "优质蛋白质"]
        ),
        
        NutritionProfile.COAT_HEALTH: NutritionPlan(
            name="美毛配方",
            description="促进毛发健康和光泽的配方",
            category_ratios=CategoryRatio(
                red_meat=0.25,      # 25% 红肉
                white_meat=0.20,    # 20% 白肉
                fish=0.30,          # 30% 鱼类（omega-3）
                organs=0.05,        # 5% 内脏
                vegetables=0.15,    # 15% 蔬菜
                fruits=0.05,        # 5% 水果
                grains=0.00         # 0% 谷物
            ),
            nutrition_targets=NutritionTarget(
                protein_min=22.0, protein_max=30.0,
                fat_min=8.0, fat_max=15.0,
                carb_max=20.0,
                calories_per_kg=95
            ),
            special_notes=["富含omega-3脂肪酸", "高质量蛋白质", "维生素E和锌"]
        )
    }
    
    @classmethod
    def get_plan(cls, profile: NutritionProfile) -> NutritionPlan:
        """获取指定的营养方案"""
        return cls.NUTRITION_PLANS.get(profile)
    
    @classmethod
    def get_suitable_plans(cls, pet_species: str, age: int, special_needs: List[str]) -> List[NutritionProfile]:
        """根据宠物信息推荐合适的营养方案"""
        suitable_plans = []
        
        # 基础方案
        if pet_species.lower() == 'dog':
            if age >= 7:
                suitable_plans.append(NutritionProfile.SENIOR_DOG)
            else:
                suitable_plans.append(NutritionProfile.BASIC_DOG)
                suitable_plans.append(NutritionProfile.ACTIVE_DOG)
        elif pet_species.lower() == 'cat':
            suitable_plans.append(NutritionProfile.BASIC_CAT)
        
        # 特殊需求方案
        if special_needs:
            for need in special_needs:
                need_lower = need.lower()
                if '肥胖' in need_lower or '减重' in need_lower:
                    suitable_plans.append(NutritionProfile.WEIGHT_LOSS)
                elif '肾' in need_lower:
                    suitable_plans.append(NutritionProfile.KIDNEY_SUPPORT)
                elif '美毛' in need_lower or '毛发' in need_lower:
                    suitable_plans.append(NutritionProfile.COAT_HEALTH)
                elif '过敏' in need_lower:
                    suitable_plans.append(NutritionProfile.ALLERGY_FRIENDLY)
        
        return list(set(suitable_plans))  # 去重
    
    @classmethod
    def calculate_ingredient_weights(cls, plan: NutritionPlan, total_weight: float, 
                                    selected_ingredients: Dict) -> Dict[int, float]:
        """
        根据营养方案和总重量计算各食材的推荐重量
        
        Args:
            plan: 营养方案
            total_weight: 总食物重量(g)
            selected_ingredients: {ingredient_id: ingredient_obj} 已选择的食材
            
        Returns:
            {ingredient_id: weight} 推荐重量分配
        """
        weights = {}
        ratios = plan.category_ratios
        
        # 按类别分组食材
        ingredients_by_category = {}
        for ing_id, ingredient in selected_ingredients.items():
            category = ingredient.category.value
            if category not in ingredients_by_category:
                ingredients_by_category[category] = []
            ingredients_by_category[category].append((ing_id, ingredient))
        
        # 分配重量
        for category, ratio in [
            ('red_meat', ratios.red_meat),
            ('white_meat', ratios.white_meat), 
            ('fish', ratios.fish),
            ('organs', ratios.organs),
            ('vegetables', ratios.vegetables),
            ('fruits', ratios.fruits),
            ('grains', ratios.grains)
        ]:
            if category in ingredients_by_category and ratio > 0:
                category_weight = total_weight * ratio
                category_ingredients = ingredients_by_category[category]
                weight_per_ingredient = category_weight / len(category_ingredients)
                
                for ing_id, _ in category_ingredients:
                    weights[ing_id] = weight_per_ingredient
        
        return weights

def get_nutrition_profile_choices():
    """获取可选的营养方案列表（用于前端下拉框）"""
    return [
        (profile.value, plan.name) 
        for profile, plan in NutritionRatioService.NUTRITION_PLANS.items()
    ]