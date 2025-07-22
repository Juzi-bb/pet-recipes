"""
食谱功能使用示例
展示如何使用新的营养数据模型创建和管理食谱
"""

from sqlalchemy.orm import sessionmaker
from app.models.database_config import engine, get_db
from app.models.ingredient_model import Ingredient, IngredientCategory
from app.models.recipe_model import Recipe, RecipeStatus
from app.models.recipe_ingredient_model import RecipeIngredient
from app.models.nutrition_requirements_model import NutritionRequirement, PetType, LifeStage, ActivityLevel
from datetime import datetime


class RecipeService:
    """食谱服务类 - 封装食谱相关的业务逻辑"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create_recipe(self, user_id, pet_id, name, description=""):
        """创建新食谱"""
        recipe = Recipe(
            user_id=user_id,
            pet_id=pet_id,
            name=name,
            description=description,
            status=RecipeStatus.DRAFT
        )
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe
    
    def add_ingredient_to_recipe(self, recipe_id, ingredient_id, weight, preparation_note=""):
        """向食谱添加食材"""
        # 检查食材是否已存在于食谱中
        existing = self.db.query(RecipeIngredient).filter_by(
            recipe_id=recipe_id,
            ingredient_id=ingredient_id
        ).first()
        
        if existing:
            # 如果已存在，更新重量
            existing.update_weight(weight)
            existing.preparation_note = preparation_note
            recipe_ingredient = existing
        else:
            # 创建新的食材关联
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=ingredient_id,
                weight=weight,
                preparation_note=preparation_note
            )
            self.db.add(recipe_ingredient)
        
        self.db.commit()
        
        # 重新计算食谱营养
        recipe = self.db.query(Recipe).get(recipe_id)
        self.recalculate_recipe_nutrition(recipe)
        
        return recipe_ingredient
    
    def remove_ingredient_from_recipe(self, recipe_id, ingredient_id):
        """从食谱中移除食材"""
        recipe_ingredient = self.db.query(RecipeIngredient).filter_by(
            recipe_id=recipe_id,
            ingredient_id=ingredient_id
        ).first()
        
        if recipe_ingredient:
            self.db.delete(recipe_ingredient)
            self.db.commit()
            
            # 重新计算食谱营养
            recipe = self.db.query(Recipe).get(recipe_id)
            self.recalculate_recipe_nutrition(recipe)
            
            return True
        return False
    
    def recalculate_recipe_nutrition(self, recipe):
        """重新计算食谱营养成分"""
        # 加载食材关联
        recipe.calculate_nutrition()
        recipe.check_suitability()
        
        self.db.commit()
        return recipe
    
    def get_recipe_nutrition_analysis(self, recipe_id, pet_weight_kg=None, pet_type=None, life_stage=None):
        """获取食谱营养分析"""
        recipe = self.db.query(Recipe).get(recipe_id)
        if not recipe:
            return None
        
        analysis = {
            'recipe_id': recipe_id,
            'recipe_name': recipe.name,
            'total_weight': recipe.total_weight,
            'nutrition_per_100g': recipe.get_nutrition_per_100g(),
            'total_nutrition': {
                'calories': recipe.total_calories,
                'protein': recipe.total_protein,
                'fat': recipe.total_fat,
                'carbohydrate': recipe.total_carbohydrate,
                'fiber': recipe.total_fiber,
                'calcium': recipe.total_calcium,
                'phosphorus': recipe.total_phosphorus,
                'vitamin_a': recipe.total_vitamin_a,
                'vitamin_d': recipe.total_vitamin_d,
                'taurine': recipe.total_taurine,
                'omega_3': recipe.total_omega_3,
                'omega_6': recipe.total_omega_6
            },
            'suitability': {
                'dogs': recipe.suitable_for_dogs,
                'cats': recipe.suitable_for_cats,
                'puppies': recipe.suitable_for_puppies,
                'kittens': recipe.suitable_for_kittens,
                'seniors': recipe.suitable_for_seniors
            },
            'ingredients': []
        }
        
        # 添加食材详情
        for ri in recipe.ingredients:
            ingredient_info = {
                'name': ri.ingredient.name,
                'category': ri.ingredient.category.value,
                'weight': ri.weight,
                'percentage': (ri.weight / recipe.total_weight * 100) if recipe.total_weight > 0 else 0,
                'preparation_note': ri.preparation_note,
                'nutrition_contribution': ri.get_full_nutrition_contribution()
            }
            analysis['ingredients'].append(ingredient_info)
        
        # 如果提供了宠物信息，进行需求对比
        if pet_weight_kg and pet_type and life_stage:
            requirements = self.get_nutrition_requirements(pet_type, life_stage, pet_weight_kg)
            if requirements:
                analysis['requirements_comparison'] = self.compare_with_requirements(recipe, requirements)
        
        return analysis
    
    def get_nutrition_requirements(self, pet_type, life_stage, weight_kg, activity_level=ActivityLevel.MODERATE):
        """获取营养需求标准"""
        requirement = self.db.query(NutritionRequirement).filter(
            NutritionRequirement.pet_type == pet_type,
            NutritionRequirement.life_stage == life_stage,
            NutritionRequirement.activity_level == activity_level,
            NutritionRequirement.min_weight <= weight_kg,
            NutritionRequirement.max_weight >= weight_kg,
            NutritionRequirement.is_active == True
        ).first()
        
        if requirement:
            return requirement.calculate_daily_requirements(weight_kg)
        return None
    
    def compare_with_requirements(self, recipe, requirements):
        """对比食谱与营养需求"""
        if not requirements:
            return None
        
        # 计算每日所需食谱量 (基于热量需求)
        daily_food_needed = requirements['daily_calories'] / (recipe.total_calories / recipe.total_weight) if recipe.total_calories > 0 else 0
        
        # 计算实际营养摄入
        actual_nutrition = {
            'protein': recipe.total_protein * (daily_food_needed / recipe.total_weight),
            'fat': recipe.total_fat * (daily_food_needed / recipe.total_weight),
            'calcium': recipe.total_calcium * (daily_food_needed / recipe.total_weight),
            'phosphorus': recipe.total_phosphorus * (daily_food_needed / recipe.total_weight),
            'vitamin_a': recipe.total_vitamin_a * (daily_food_needed / recipe.total_weight),
            'taurine': recipe.total_taurine * (daily_food_needed / recipe.total_weight)
        }
        
        # 计算达标情况
        adequacy = {}
        for nutrient, actual_value in actual_nutrition.items():
            required_key = f"{nutrient}_min_g" if nutrient in ['protein', 'fat'] else f"{nutrient}_min_mg"
            if required_key in requirements:
                required_value = requirements[required_key]
                adequacy[nutrient] = {
                    'actual': actual_value,
                    'required': required_value,
                    'percentage': (actual_value / required_value * 100) if required_value > 0 else 0,
                    'adequate': actual_value >= required_value
                }
        
        return {
            'daily_food_needed_g': daily_food_needed,
            'actual_nutrition': actual_nutrition,
            'adequacy': adequacy
        }
    
    def get_recipe_recommendations(self, pet_type, life_stage, weight_kg, excluded_ingredients=None):
        """获取食谱推荐"""
        if excluded_ingredients is None:
            excluded_ingredients = []
        
        # 获取适合的食材
        suitable_ingredients = self.db.query(Ingredient).filter(
            Ingredient.is_active == True,
            ~Ingredient.id.in_(excluded_ingredients)
        )
        
        if pet_type == PetType.DOG:
            suitable_ingredients = suitable_ingredients.filter(Ingredient.is_safe_for_dogs == True)
        elif pet_type == PetType.CAT:
            suitable_ingredients = suitable_ingredients.filter(Ingredient.is_safe_for_cats == True)
        
        # 按类别分组
        ingredients_by_category = {}
        for ingredient in suitable_ingredients:
            category = ingredient.category.value
            if category not in ingredients_by_category:
                ingredients_by_category[category] = []
            ingredients_by_category[category].append(ingredient)
        
        # 生成推荐组合
        recommendations = []
        
        # 基础推荐：蛋白质 + 蔬菜 + 少量碳水
        if 'white_meat' in ingredients_by_category and 'vegetables' in ingredients_by_category:
            protein_source = ingredients_by_category['white_meat'][0]  # 选择鸡肉
            vegetable = ingredients_by_category['vegetables'][0]       # 选择胡萝卜
            
            base_weight = weight_kg * 20  # 每kg体重约20g食物
            
            recommendation = {
                'name': f"基础营养食谱 - {protein_source.name}配{vegetable.name}",
                'description': "均衡的蛋白质和维生素组合",
                'ingredients': [
                    {'ingredient': protein_source, 'weight': base_weight * 0.7},
                    {'ingredient': vegetable, 'weight': base_weight * 0.3}
                ],
                'estimated_nutrition': self.estimate_recipe_nutrition([
                    (protein_source, base_weight * 0.7),
                    (vegetable, base_weight * 0.3)
                ])
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def estimate_recipe_nutrition(self, ingredient_weight_pairs):
        """估算食谱营养成分"""
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_weight = 0
        
        for ingredient, weight in ingredient_weight_pairs:
            weight_ratio = weight / 100
            total_weight += weight
            total_calories += ingredient.calories * weight_ratio
            total_protein += ingredient.protein * weight_ratio
            total_fat += ingredient.fat * weight_ratio
        
        return {
            'total_weight': total_weight,
            'calories': total_calories,
            'protein': total_protein,
            'fat': total_fat,
            'calories_per_100g': (total_calories / total_weight * 100) if total_weight > 0 else 0
        }


def example_usage():
    """使用示例"""
    # 创建数据库会话
    from database_config import SessionLocal
    db = SessionLocal()
    
    try:
        # 创建服务实例
        recipe_service = RecipeService(db)
        
        # 示例1: 创建一个新食谱
        print("=== 创建新食谱 ===")
        recipe = recipe_service.create_recipe(
            user_id=1,
            pet_id=1,
            name="小型犬营养餐",
            description="适合小型犬的均衡营养食谱"
        )
        print(f"创建食谱: {recipe.name} (ID: {recipe.id})")
        
        # 示例2: 添加食材到食谱
        print("\n=== 添加食材到食谱 ===")
        
        # 获取一些食材
        chicken = db.query(Ingredient).filter_by(name="鸡胸肉").first()
        carrot = db.query(Ingredient).filter_by(name="胡萝卜").first()
        rice = db.query(Ingredient).filter_by(name="糙米").first()
        
        if chicken and carrot and rice:
            # 添加鸡胸肉 100g
            recipe_service.add_ingredient_to_recipe(
                recipe.id, chicken.id, 100, "煮熟切丁"
            )
            print(f"添加 {chicken.name} 100g")
            
            # 添加胡萝卜 50g
            recipe_service.add_ingredient_to_recipe(
                recipe.id, carrot.id, 50, "切丁煮软"
            )
            print(f"添加 {carrot.name} 50g")
            
            # 添加糙米 30g
            recipe_service.add_ingredient_to_recipe(
                recipe.id, rice.id, 30, "煮熟"
            )
            print(f"添加 {rice.name} 30g")
        
        # 示例3: 获取食谱营养分析
        print("\n=== 食谱营养分析 ===")
        analysis = recipe_service.get_recipe_nutrition_analysis(
            recipe.id,
            pet_weight_kg=5.0,  # 5kg的小型犬
            pet_type=PetType.DOG,
            life_stage=LifeStage.ADULT
        )
        
        if analysis:
            print(f"食谱名称: {analysis['recipe_name']}")
            print(f"总重量: {analysis['total_weight']}g")
            print(f"总热量: {analysis['total_nutrition']['calories']:.1f} kcal")
            print(f"蛋白质: {analysis['total_nutrition']['protein']:.1f}g")
            print(f"脂肪: {analysis['total_nutrition']['fat']:.1f}g")
            print(f"钙: {analysis['total_nutrition']['calcium']:.1f}mg")
            
            print("\n食材组成:")
            for ing in analysis['ingredients']:
                print(f"- {ing['name']}: {ing['weight']}g ({ing['percentage']:.1f}%)")
            
            # 显示营养需求对比
            if 'requirements_comparison' in analysis:
                comp = analysis['requirements_comparison']
                print(f"\n营养需求对比 (5kg成犬):")
                print(f"建议每日食量: {comp['daily_food_needed_g']:.1f}g")
                
                for nutrient, data in comp['adequacy'].items():
                    status = "✓" if data['adequate'] else "✗"
                    print(f"{status} {nutrient}: {data['actual']:.1f}/{data['required']:.1f} ({data['percentage']:.1f}%)")
        
        # 示例4: 获取食谱推荐
        print("\n=== 食谱推荐 ===")
        recommendations = recipe_service.get_recipe_recommendations(
            PetType.DOG,
            LifeStage.ADULT,
            5.0  # 5kg成犬
        )
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n推荐 {i}: {rec['name']}")
            print(f"说明: {rec['description']}")
            print("建议配方:")
            for ing_data in rec['ingredients']:
                print(f"- {ing_data['ingredient'].name}: {ing_data['weight']}g")
            
            est_nutrition = rec['estimated_nutrition']
            print(f"预估营养: {est_nutrition['calories']:.1f} kcal, "
                  f"{est_nutrition['protein']:.1f}g蛋白质, "
                  f"{est_nutrition['fat']:.1f}g脂肪")
        
        # 示例5: 修改食谱
        print("\n=== 修改食谱 ===")
        if chicken:
            # 增加鸡肉重量到150g
            recipe_service.add_ingredient_to_recipe(
                recipe.id, chicken.id, 150, "煮熟切丁"
            )
            print("将鸡胸肉重量调整为150g")
            
            # 重新分析
            updated_analysis = recipe_service.get_recipe_nutrition_analysis(recipe.id)
            print(f"更新后总热量: {updated_analysis['total_nutrition']['calories']:.1f} kcal")
        
        print("\n=== 示例完成 ===")
        
    except Exception as e:
        print(f"示例运行出错: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    example_usage()