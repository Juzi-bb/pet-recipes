# 预设食谱初始化脚本

import os
import sys
from datetime import datetime

# 添加项目路径到系统路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入应用和数据库模型
from app import create_app, db
from app.models.user_model import User
from app.models.recipe_model import Recipe, RecipeStatus
from app.models.ingredient_model import Ingredient, IngredientCategory
from app.models.recipe_ingredient_model import RecipeIngredient

def create_system_user():
    """创建系统用户作为预设食谱的作者"""
    system_user = User.query.filter_by(username='PetNutritionSystem').first()
    
    if not system_user:
        # 创建新的系统用户
        system_user = User(
            username='PetNutritionSystem',
            nickname='System Recommendations'
        )
        system_user.set_password('system_password_2025')
        db.session.add(system_user)
        db.session.commit()
        print("✅ System user created successfully")
    else:
        print("📍 System user already exists")
    
    return system_user

def verify_ingredients_exist(ingredient_names):
    """验证所有需要的食材是否存在于数据库中"""
    print("🔍 Verifying ingredients exist in database...")
    
    missing_ingredients = []  # 缺失的食材列表
    found_ingredients = {}    # 找到的食材字典
    
    # 遍历检查每个食材
    for name in ingredient_names:
        ingredient = Ingredient.query.filter_by(name=name).first()
        if ingredient:
            found_ingredients[name] = ingredient
            print(f"  ✅ Found: {name}")
        else:
            missing_ingredients.append(name)
            print(f"  ❌ Missing: {name}")
    
    # 如果有缺失的食材，显示警告信息
    if missing_ingredients:
        print(f"\n⚠️ Warning: {len(missing_ingredients)} ingredients not found:")
        for name in missing_ingredients:
            print(f"  - {name}")
        print("\nPlease run 'python init_nutrition_data.py' first to ensure all ingredients are available.")
        return found_ingredients, missing_ingredients
    
    print(f"✅ All {len(ingredient_names)} ingredients found in database!")
    return found_ingredients, missing_ingredients

def create_preset_recipes(system_user):
    """使用数据库中现有的食材创建预设食谱"""
    
    # 定义所有食谱需要的食材清单）
    all_required_ingredients = [
        # 蛋白质来源
        'Chicken breast', 'Beef (lean)', 'Salmon', 'Chicken liver', 'Turkey', 'Duck', 
        'Chicken heart', 'Beef liver', 'Cod', 'Sardine', 'Chicken egg',
        
        # 碳水化合物来源
        'Brown rice', 'Sweet potato', 'Pumpkin', 'Oats', 'Quinoa',
        
        # 蔬菜类
        'Carrot', 'Broccoli', 'Spinach', 'Bell pepper', 'Zucchini', 'Green peas',
        
        # 水果类
        'Blueberry', 'Apple', 'Strawberry',
        
        # 营养补充剂
        'Flax seed oil', 'Fish oil', 'Eggshell powder'
    ]
    
    # 验证所需食材是否存在于数据库中
    found_ingredients, missing_ingredients = verify_ingredients_exist(all_required_ingredients)
    
    if missing_ingredients:
        print(f"\n❌ Cannot proceed: {len(missing_ingredients)} required ingredients are missing from database.")
        return False
    
    # 预设食谱数据定义
    preset_recipes = [
        # ============ 狗狗食谱 ============
        {
            'name': '🐕 Puppy Growth High-Protein Formula',  # 幼犬成长高蛋白配方
            'description': 'Specially designed high-protein formula for 2-12 month puppies to support healthy growth and development. Rich in DHA for brain development, with scientifically balanced calcium-phosphorus ratio for strong bones.',
            'suitable_for_dogs': True,
            'suitable_for_cats': False,
            'suitable_for_puppies': True,
            'ingredients': [
                {'name': 'Chicken breast', 'weight': 280},
                {'name': 'Salmon', 'weight': 150},
                {'name': 'Chicken liver', 'weight': 70},
                {'name': 'Brown rice', 'weight': 180},
                {'name': 'Sweet potato', 'weight': 120},
                {'name': 'Carrot', 'weight': 80},
                {'name': 'Spinach', 'weight': 50},
                {'name': 'Blueberry', 'weight': 40},
                {'name': 'Flax seed oil', 'weight': 8},
                {'name': 'Eggshell powder', 'weight': 2}
            ]
        },
        {
            'name': '🐕 Adult Dog Balanced Nutrition Formula',  # 成犬均衡营养配方
            'description': 'Complete and balanced nutrition for 1-7 year old adult dogs. Moderate protein content with rich fiber to maintain ideal weight and vitality. Perfect for daily feeding.',
            'suitable_for_dogs': True,
            'suitable_for_cats': False,
            'suitable_for_puppies': False,
            'ingredients': [
                {'name': 'Beef (lean)', 'weight': 220},
                {'name': 'Chicken breast', 'weight': 180},
                {'name': 'Turkey', 'weight': 100},
                {'name': 'Brown rice', 'weight': 200},
                {'name': 'Sweet potato', 'weight': 150},
                {'name': 'Broccoli', 'weight': 100},
                {'name': 'Carrot', 'weight': 80},
                {'name': 'Green peas', 'weight': 60},
                {'name': 'Apple', 'weight': 50},
                {'name': 'Flax seed oil', 'weight': 6},
                {'name': 'Eggshell powder', 'weight': 2}
            ]
        },
        {
            'name': '🐕 Senior Dog Joint Care Formula',  # 老年犬关节护理配方
            'description': 'Designed for dogs 7+ years old with joint care focus. Moderate protein with low phosphorus to protect kidneys, rich in antioxidants to slow aging process.',
            'suitable_for_dogs': True,
            'suitable_for_cats': False,
            'suitable_for_seniors': True,
            'ingredients': [
                {'name': 'Chicken breast', 'weight': 250},
                {'name': 'Salmon', 'weight': 120},
                {'name': 'Cod', 'weight': 80},
                {'name': 'Sweet potato', 'weight': 180},
                {'name': 'Pumpkin', 'weight': 100},
                {'name': 'Broccoli', 'weight': 90},
                {'name': 'Spinach', 'weight': 60},
                {'name': 'Blueberry', 'weight': 50},
                {'name': 'Fish oil', 'weight': 5},
                {'name': 'Eggshell powder', 'weight': 2}
            ]
        },
        {
            'name': '🐕 Active Dog High-Energy Formula',  # 活跃犬高能量配方
            'description': 'High-energy formula for working dogs, sporting dogs, and highly active breeds. Increased fat content for sustained energy with premium protein sources.',
            'suitable_for_dogs': True,
            'suitable_for_cats': False,
            'suitable_for_puppies': False,
            'ingredients': [
                {'name': 'Beef (lean)', 'weight': 250},
                {'name': 'Salmon', 'weight': 180},
                {'name': 'Duck', 'weight': 120},
                {'name': 'Quinoa', 'weight': 150},
                {'name': 'Sweet potato', 'weight': 120},
                {'name': 'Carrot', 'weight': 80},
                {'name': 'Bell pepper', 'weight': 60},
                {'name': 'Strawberry', 'weight': 40},
                {'name': 'Fish oil', 'weight': 8},
                {'name': 'Flax seed oil', 'weight': 5}
            ]
        },
        
        # ============ 猫咪食谱 ============
        {
            'name': '🐱 Kitten Development High-Protein Formula',  # 幼猫发育高蛋白配方
            'description': 'Specially formulated for 2-12 month kittens with high protein content. Adequate taurine levels, DHA for neural development, and high energy density for rapid growth.',
            'suitable_for_dogs': False,
            'suitable_for_cats': True,
            'suitable_for_kittens': True,
            'ingredients': [
                {'name': 'Chicken breast', 'weight': 300},
                {'name': 'Salmon', 'weight': 160},
                {'name': 'Chicken liver', 'weight': 100},
                {'name': 'Chicken heart', 'weight': 80},
                {'name': 'Sweet potato', 'weight': 60},
                {'name': 'Carrot', 'weight': 50},
                {'name': 'Spinach', 'weight': 30},
                {'name': 'Blueberry', 'weight': 25},
                {'name': 'Fish oil', 'weight': 6}
            ]
        },
        {
            'name': '🐱 Adult Cat Urinary Health Formula',  # 成猫泌尿健康配方
            'description': 'Designed for 1-7 year old adult cats with urinary health focus. Low magnesium to prevent stones, high protein low carb matching feline nature, adequate moisture for urination.',
            'suitable_for_dogs': False,
            'suitable_for_cats': True,
            'suitable_for_puppies': False,
            'ingredients': [
                {'name': 'Beef (lean)', 'weight': 260},
                {'name': 'Salmon', 'weight': 140},
                {'name': 'Chicken liver', 'weight': 90},
                {'name': 'Turkey', 'weight': 100},
                {'name': 'Sweet potato', 'weight': 50},
                {'name': 'Broccoli', 'weight': 60},
                {'name': 'Zucchini', 'weight': 40},
                {'name': 'Blueberry', 'weight': 25},
                {'name': 'Fish oil', 'weight': 5}
            ]
        },
        {
            'name': '🐱 Senior Cat Kidney Care Formula',  # 老年猫肾脏护理配方
            'description': 'Designed for cats 7+ years old with kidney care focus. Moderate protein to reduce kidney burden, low phosphorus to protect kidney function, antioxidants to slow aging.',
            'suitable_for_dogs': False,
            'suitable_for_cats': True,
            'suitable_for_seniors': True,
            'ingredients': [
                {'name': 'Chicken breast', 'weight': 280},
                {'name': 'Cod', 'weight': 120},
                {'name': 'Chicken heart', 'weight': 60},
                {'name': 'Sweet potato', 'weight': 70},
                {'name': 'Pumpkin', 'weight': 60},
                {'name': 'Carrot', 'weight': 50},
                {'name': 'Broccoli', 'weight': 40},
                {'name': 'Blueberry', 'weight': 30},
                {'name': 'Fish oil', 'weight': 4}
            ]
        },
        {
            'name': '🐱 Indoor Cat Weight Management Formula',  # 室内猫体重管理配方
            'description': 'Perfect for indoor cats with lower activity levels. Controlled calories with high fiber to promote satiety, premium protein to maintain muscle mass.',
            'suitable_for_dogs': False,
            'suitable_for_cats': True,
            'suitable_for_puppies': False,
            'ingredients': [
                {'name': 'Chicken breast', 'weight': 280},
                {'name': 'Cod', 'weight': 150},
                {'name': 'Turkey', 'weight': 100},
                {'name': 'Pumpkin', 'weight': 80},
                {'name': 'Green peas', 'weight': 70},
                {'name': 'Zucchini', 'weight': 60},
                {'name': 'Spinach', 'weight': 40},
                {'name': 'Apple', 'weight': 30},
                {'name': 'Flax seed oil', 'weight': 3}
            ]
        },
        
        # ============ 特殊膳食食谱 ============
        {
            'name': '🌟 Novel Protein Allergy-Friendly Formula',  # 新奇蛋白过敏友好配方
            'description': 'Hypoallergenic recipe using novel proteins for dogs and cats with food sensitivities. Limited ingredient formula to minimize allergic reactions.',
            'suitable_for_dogs': True,
            'suitable_for_cats': True,
            'suitable_for_puppies': False,
            'ingredients': [
                {'name': 'Duck', 'weight': 350},
                {'name': 'Quinoa', 'weight': 150},
                {'name': 'Sweet potato', 'weight': 120},
                {'name': 'Zucchini', 'weight': 80},
                {'name': 'Bell pepper', 'weight': 60},
                {'name': 'Blueberry', 'weight': 30},
                {'name': 'Flax seed oil', 'weight': 5}
            ]
        },
        {
            'name': '🌟 Digestive Support Gentle Formula',  # 消化支持温和配方
            'description': 'Easy-to-digest recipe for pets recovering from digestive issues or with sensitive stomachs. Simple ingredients with probiotics support.',
            'suitable_for_dogs': True,
            'suitable_for_cats': True,
            'suitable_for_puppies': True,
            'ingredients': [
                {'name': 'Chicken breast', 'weight': 300},
                {'name': 'Brown rice', 'weight': 200},
                {'name': 'Pumpkin', 'weight': 150},
                {'name': 'Carrot', 'weight': 80},
                {'name': 'Sweet potato', 'weight': 80},
                {'name': 'Chicken egg', 'weight': 50},
                {'name': 'Flax seed oil', 'weight': 3}
            ]
        }
    ]
    
    created_count = 0  # 成功创建的食谱计数
    
    # 遍历所有预设食谱进行创建
    for recipe_data in preset_recipes:
        # 检查食谱是否已经存在
        existing_recipe = Recipe.query.filter_by(
            name=recipe_data['name'],
            user_id=system_user.id
        ).first()
        
        if existing_recipe:
            print(f"📍 Recipe already exists: {recipe_data['name']}")
            continue
        
        # 验证此食谱的所有食材是否存在
        recipe_ingredients_missing = []
        for ingredient_data in recipe_data['ingredients']:
            if ingredient_data['name'] not in found_ingredients:
                recipe_ingredients_missing.append(ingredient_data['name'])
        
        if recipe_ingredients_missing:
            print(f"⚠️ Skipping recipe '{recipe_data['name']}' - missing ingredients: {recipe_ingredients_missing}")
            continue
        
        # 创建食谱记录
        recipe = Recipe(
            name=recipe_data['name'],
            description=recipe_data['description'],
            user_id=system_user.id,
            suitable_for_dogs=recipe_data['suitable_for_dogs'],
            suitable_for_cats=recipe_data['suitable_for_cats'],
            suitable_for_puppies=recipe_data.get('suitable_for_puppies', False),
            suitable_for_kittens=recipe_data.get('suitable_for_kittens', False),
            suitable_for_seniors=recipe_data.get('suitable_for_seniors', False),
            status=RecipeStatus.PUBLISHED,  # 设置为已发布状态
            is_public=True,                 # 设置为公开
            created_at=datetime.utcnow()    # 设置创建时间
        )
        
        db.session.add(recipe)
        db.session.flush()  # 获取食谱ID
        
        # 添加食材到食谱中
        total_weight = 0                    # 总重量
        successfully_added_ingredients = 0  # 成功添加的食材数量
        
        for ingredient_data in recipe_data['ingredients']:
            ingredient = found_ingredients.get(ingredient_data['name'])
            
            if not ingredient:
                print(f"⚠️ Warning: Ingredient '{ingredient_data['name']}' not found, skipping")
                continue
            
            # 创建食谱-食材关联记录
            recipe_ingredient = RecipeIngredient.create_from_data(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                weight=ingredient_data['weight']
            )
            
            db.session.add(recipe_ingredient)
            total_weight += ingredient_data['weight']
            successfully_added_ingredients += 1
        
        # 只有成功添加了食材才继续处理
        if successfully_added_ingredients == 0:
            print(f"❌ Failed to add any ingredients to recipe '{recipe_data['name']}', skipping")
            db.session.rollback()
            continue
        
        # 计算营养成分
        recipe.calculate_nutrition()  # 计算总营养成分
        recipe.check_suitability()    # 检查适用性
        
        # 设置初始统计数据（让食谱看起来有一定的社区互动）
        import random
        recipe.usage_count = random.randint(5, 25)           # 随机使用次数
        recipe.nutrition_score = round(random.uniform(85, 95), 1)  # 营养评分
        recipe.balance_score = round(random.uniform(88, 96), 1)    # 平衡评分
        
        created_count += 1
        print(f"✅ Created recipe: {recipe_data['name']} (Total weight: {total_weight}g, Ingredients: {successfully_added_ingredients})")
    
    # 提交数据库变更
    if created_count > 0:
        db.session.commit()
        print(f"🎉 Successfully created {created_count} preset recipes!")
    else:
        print("📍 All preset recipes already exist or could not be created")
    
    return created_count > 0

def init_preset_recipes():
    """初始化预设食谱的主函数"""
    print("🚀 Starting preset recipe initialization...")
    print("=" * 50)
    
    # 创建Flask应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 创建系统用户
            system_user = create_system_user()
            
            # 2. 创建预设食谱（仅使用现有食材）
            success = create_preset_recipes(system_user)
            
            print("=" * 50)
            if success:
                print("🎊 Preset recipe initialization completed successfully!")
            else:
                print("⚠️ Preset recipe initialization completed with warnings!")
            
            # 显示统计信息
            total_recipes = Recipe.query.filter_by(user_id=system_user.id).count()
            total_ingredients = Ingredient.query.count()
            print(f"📊 System recommended recipes: {total_recipes}")
            print(f"📊 Total ingredients in database: {total_ingredients}")
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {str(e)}")
            db.session.rollback()  # 回滚数据库事务
            import traceback
            traceback.print_exc()  # 打印详细错误信息
            return False


# 主程序入口
if __name__ == '__main__':
    success = init_preset_recipes()
    if success:
        print("\n✨ You can now start the application to view preset recipes!")
        print("Run command: cd backend && python run.py")
    else:
        print("\n💔 Initialization failed, please check error messages")