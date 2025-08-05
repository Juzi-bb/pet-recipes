# 预设食谱初始化脚本
# 请将此文件保存为 backend/init_preset_recipes.py

import os
import sys
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.user_model import User
from app.models.recipe_model import Recipe, RecipeStatus
from app.models.ingredient_model import Ingredient, IngredientCategory
from app.models.recipe_ingredient_model import RecipeIngredient

def create_system_user():
    """创建系统用户作为预设食谱的作者"""
    system_user = User.query.filter_by(username='PetNutritionSystem').first()
    
    if not system_user:
        system_user = User(
            username='PetNutritionSystem',
            nickname='系统推荐'
        )
        system_user.set_password('system_password_2025')
        db.session.add(system_user)
        db.session.commit()
        print("✅ 创建系统用户成功")
    else:
        print("📍 系统用户已存在")
    
    return system_user

def ensure_basic_ingredients():
    """确保基础食材存在"""
    basic_ingredients = [
        # 蛋白质来源
        {'name': '鸡胸肉', 'category': IngredientCategory.WHITE_MEAT, 'calories': 165, 'protein': 31.0, 'fat': 3.6, 'carbohydrate': 0.0},
        {'name': '牛肉', 'category': IngredientCategory.RED_MEAT, 'calories': 250, 'protein': 26.0, 'fat': 17.0, 'carbohydrate': 0.0},
        {'name': '三文鱼', 'category': IngredientCategory.FISH, 'calories': 208, 'protein': 25.4, 'fat': 12.4, 'carbohydrate': 0.0},
        {'name': '鸡肝', 'category': IngredientCategory.ORGANS, 'calories': 119, 'protein': 24.5, 'fat': 4.8, 'carbohydrate': 0.6},
        
        # 碳水化合物来源
        {'name': '糙米', 'category': IngredientCategory.GRAINS, 'calories': 112, 'protein': 2.6, 'fat': 0.9, 'carbohydrate': 22.0},
        {'name': '红薯', 'category': IngredientCategory.VEGETABLES, 'calories': 86, 'protein': 1.6, 'fat': 0.1, 'carbohydrate': 20.1},
        
        # 蔬菜
        {'name': '胡萝卜', 'category': IngredientCategory.VEGETABLES, 'calories': 41, 'protein': 0.9, 'fat': 0.2, 'carbohydrate': 9.6},
        {'name': '西兰花', 'category': IngredientCategory.VEGETABLES, 'calories': 34, 'protein': 2.8, 'fat': 0.4, 'carbohydrate': 7.0},
        {'name': '菠菜', 'category': IngredientCategory.VEGETABLES, 'calories': 23, 'protein': 2.9, 'fat': 0.4, 'carbohydrate': 3.6},
        
        # 水果
        {'name': '蓝莓', 'category': IngredientCategory.FRUITS, 'calories': 57, 'protein': 0.7, 'fat': 0.3, 'carbohydrate': 14.5},
        {'name': '苹果', 'category': IngredientCategory.FRUITS, 'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbohydrate': 13.8},
        
        # 健康脂肪
        {'name': '亚麻籽油', 'category': IngredientCategory.OILS, 'calories': 884, 'protein': 0.0, 'fat': 100.0, 'carbohydrate': 0.0}
    ]
    
    created_count = 0
    for ingredient_data in basic_ingredients:
        if not Ingredient.query.filter_by(name=ingredient_data['name']).first():
            ingredient = Ingredient(**ingredient_data)
            # 设置营养详细信息
            if ingredient_data['name'] == '鸡胸肉':
                ingredient.calcium = 15
                ingredient.phosphorus = 228
                ingredient.taurine = 16
                ingredient.lysine = 2200
                ingredient.methionine = 800
                ingredient.omega_3_fatty_acids = 0.1
                ingredient.omega_6_fatty_acids = 0.8
            elif ingredient_data['name'] == '三文鱼':
                ingredient.calcium = 12
                ingredient.phosphorus = 289
                ingredient.taurine = 130  # 鱼类富含牛磺酸
                ingredient.omega_3_fatty_acids = 2.3
                ingredient.omega_6_fatty_acids = 0.9
                ingredient.vitamin_d = 988
            elif ingredient_data['name'] == '鸡肝':
                ingredient.calcium = 8
                ingredient.phosphorus = 297
                ingredient.vitamin_a = 11078
                ingredient.iron = 11.9
                ingredient.taurine = 110
            elif ingredient_data['name'] == '胡萝卜':
                ingredient.calcium = 33
                ingredient.vitamin_a = 16706
                ingredient.fiber = 2.8
            elif ingredient_data['name'] == '菠菜':
                ingredient.calcium = 99
                ingredient.iron = 2.7
                ingredient.fiber = 2.2
            elif ingredient_data['name'] == '亚麻籽油':
                ingredient.omega_3_fatty_acids = 53.3
                ingredient.omega_6_fatty_acids = 12.7
            
            db.session.add(ingredient)
            created_count += 1
    
    if created_count > 0:
        db.session.commit()
        print(f"✅ 创建了 {created_count} 个基础食材")
    else:
        print("📍 基础食材已存在")

def create_preset_recipes(system_user):
    """创建预设食谱"""
    
    preset_recipes = [
        # 狗狗食谱
        {
            'name': '🐕 幼犬成长高蛋白配方',
            'description': '专为2-12个月幼犬设计的高蛋白配方，支持健康成长发育。富含DHA促进大脑发育，钙磷比例科学配比强化骨骼。',
            'suitable_for_dogs': True,
            'suitable_for_cats': False,
            'suitable_for_puppies': True,
            'ingredients': [
                {'name': '鸡胸肉', 'weight': 300},  # 主要蛋白质
                {'name': '三文鱼', 'weight': 150},   # DHA来源
                {'name': '鸡肝', 'weight': 80},     # 维生素A和铁
                {'name': '糙米', 'weight': 200},    # 碳水化合物
                {'name': '红薯', 'weight': 120},    # 易消化碳水
                {'name': '胡萝卜', 'weight': 80},   # 维生素A
                {'name': '菠菜', 'weight': 50},     # 钙和铁
                {'name': '亚麻籽油', 'weight': 10}  # Omega-3
            ]
        },
        {
            'name': '🐕 成犬均衡营养配方',
            'description': '为1-7岁成年犬提供均衡营养的全价配方。蛋白质含量适中，纤维丰富，维持理想体重和活力状态。',
            'suitable_for_dogs': True,
            'suitable_for_cats': False,
            'suitable_for_puppies': False,
            'ingredients': [
                {'name': '牛肉', 'weight': 250},      # 优质蛋白质
                {'name': '鸡胸肉', 'weight': 200},    # 易消化蛋白
                {'name': '糙米', 'weight': 250},      # 主要碳水
                {'name': '红薯', 'weight': 150},      # 膳食纤维
                {'name': '西兰花', 'weight': 100},    # 维生素C和K
                {'name': '胡萝卜', 'weight': 100},    # β-胡萝卜素
                {'name': '蓝莓', 'weight': 40},       # 抗氧化剂
                {'name': '亚麻籽油', 'weight': 8}     # 必需脂肪酸
            ]
        },
        {
            'name': '🐕 老年犬关节护理配方',
            'description': '为7岁以上老年犬设计的护理配方。蛋白质适中，低磷配方保护肾脏，富含抗氧化成分延缓衰老。',
            'suitable_for_dogs': True,
            'suitable_for_cats': False,
            'suitable_for_seniors': True,
            'ingredients': [
                {'name': '鸡胸肉', 'weight': 280},    # 优质低脂蛋白
                {'name': '三文鱼', 'weight': 100},     # Omega-3抗炎
                {'name': '红薯', 'weight': 200},      # 易消化碳水
                {'name': '糙米', 'weight': 150},      # 温和碳水
                {'name': '西兰花', 'weight': 120},    # 抗氧化
                {'name': '菠菜', 'weight': 80},       # 叶酸和铁
                {'name': '蓝莓', 'weight': 60},       # 花青素
                {'name': '亚麻籽油', 'weight': 8}     # 关节保护
            ]
        },
        
        # 猫咪食谱
        {
            'name': '🐱 幼猫发育高蛋白配方',
            'description': '专为2-12个月幼猫设计的高蛋白配方。牛磺酸含量充足，DHA促进神经发育，高能量密度满足快速成长需求。',
            'suitable_for_dogs': False,
            'suitable_for_cats': True,
            'suitable_for_kittens': True,
            'ingredients': [
                {'name': '鸡胸肉', 'weight': 320},    # 主要蛋白质
                {'name': '三文鱼', 'weight': 180},     # DHA和牛磺酸
                {'name': '鸡肝', 'weight': 120},      # 维生素A和牛磺酸
                {'name': '糙米', 'weight': 80},       # 少量碳水
                {'name': '胡萝卜', 'weight': 60},     # 维生素A
                {'name': '菠菜', 'weight': 30},       # 叶酸
                {'name': '亚麻籽油', 'weight': 8}     # 必需脂肪酸
            ]
        },
        {
            'name': '🐱 成猫泌尿健康配方',
            'description': '为1-7岁成年猫设计的泌尿健康配方。低镁配方预防结石，高蛋白低碳水符合猫咪天性，充足水分促进排尿。',
            'suitable_for_dogs': False,
            'suitable_for_cats': True,
            'suitable_for_puppies': False,
            'ingredients': [
                {'name': '牛肉', 'weight': 280},      # 优质蛋白
                {'name': '三文鱼', 'weight': 150},     # Omega-3和牛磺酸
                {'name': '鸡肝', 'weight': 100},      # 维生素A
                {'name': '红薯', 'weight': 60},       # 最小碳水
                {'name': '西兰花', 'weight': 80},     # 维生素C
                {'name': '蓝莓', 'weight': 30},       # 泌尿道健康
                {'name': '亚麻籽油', 'weight': 6}     # 毛发健康
            ]
        },
        {
            'name': '🐱 老年猫肾脏护理配方',
            'description': '为7岁以上老年猫设计的肾脏护理配方。适度蛋白质减轻肾脏负担，低磷配方保护肾功能，抗氧化成分延缓衰老。',
            'suitable_for_dogs': False,
            'suitable_for_cats': True,
            'suitable_for_seniors': True,
            'ingredients': [
                {'name': '鸡胸肉', 'weight': 300},    # 优质蛋白
                {'name': '三文鱼', 'weight': 120},     # Omega-3
                {'name': '红薯', 'weight': 80},       # 易消化碳水
                {'name': '胡萝卜', 'weight': 70},     # 抗氧化
                {'name': '西兰花', 'weight': 60},     # 维生素K
                {'name': '蓝莓', 'weight': 40},       # 花青素
                {'name': '亚麻籽油', 'weight': 5}     # 必需脂肪酸
            ]
        }
    ]
    
    created_count = 0
    
    for recipe_data in preset_recipes:
        # 检查是否已存在
        existing_recipe = Recipe.query.filter_by(
            name=recipe_data['name'],
            user_id=system_user.id
        ).first()
        
        if existing_recipe:
            print(f"📍 食谱已存在: {recipe_data['name']}")
            continue
        
        # 创建食谱
        recipe = Recipe(
            name=recipe_data['name'],
            description=recipe_data['description'],
            user_id=system_user.id,
            suitable_for_dogs=recipe_data['suitable_for_dogs'],
            suitable_for_cats=recipe_data['suitable_for_cats'],
            suitable_for_puppies=recipe_data.get('suitable_for_puppies', False),
            suitable_for_kittens=recipe_data.get('suitable_for_kittens', False),
            suitable_for_seniors=recipe_data.get('suitable_for_seniors', False),
            status=RecipeStatus.PUBLISHED,
            is_public=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(recipe)
        db.session.flush()  # 获取recipe.id
        
        # 添加食材
        total_weight = 0
        for ingredient_data in recipe_data['ingredients']:
            ingredient = Ingredient.query.filter_by(
                name=ingredient_data['name']
            ).first()
            
            if not ingredient:
                print(f"⚠️ 警告: 食材 '{ingredient_data['name']}' 不存在，跳过")
                continue
            
            recipe_ingredient = RecipeIngredient.create_from_data(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                weight=ingredient_data['weight']
            )
            
            db.session.add(recipe_ingredient)
            total_weight += ingredient_data['weight']
        
        # 计算营养成分
        recipe.calculate_nutrition()
        recipe.check_suitability()
        
        # 设置初始统计数据（让食谱看起来有一定的社区互动）
        import random
        recipe.usage_count = random.randint(5, 25)
        recipe.nutrition_score = round(random.uniform(85, 95), 1)
        recipe.balance_score = round(random.uniform(88, 96), 1)
        
        created_count += 1
        print(f"✅ 创建食谱: {recipe_data['name']} (总重量: {total_weight}g)")
    
    if created_count > 0:
        db.session.commit()
        print(f"🎉 成功创建 {created_count} 个预设食谱!")
    else:
        print("📍 所有预设食谱已存在")

def init_preset_recipes():
    """初始化预设食谱的主函数"""
    print("🚀 开始初始化预设食谱...")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 创建系统用户
            system_user = create_system_user()
            
            # 2. 确保基础食材存在
            ensure_basic_ingredients()
            
            # 3. 创建预设食谱
            create_preset_recipes(system_user)
            
            print("=" * 50)
            print("🎊 预设食谱初始化完成!")
            
            # 显示统计信息
            total_recipes = Recipe.query.filter_by(user_id=system_user.id).count()
            print(f"📊 系统推荐食谱总数: {total_recipes}")
            
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_preset_recipes()
    if success:
        print("\n✨ 现在可以启动应用查看预设食谱了!")
        print("运行命令: cd backend && python run.py")
    else:
        print("\n💔 初始化失败，请检查错误信息")