# 食谱相关路由
# 处理食谱创建、营养分析等功能
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from app.models.ingredient_model import Ingredient, IngredientCategory
from app.models.recipe_model import Recipe, RecipeStatus
from app.models.recipe_ingredient_model import RecipeIngredient
from app.models.nutrition_requirements_model import NutritionRequirement, PetType, LifeStage, ActivityLevel
from app.models.pet_model import Pet
from app.extensions import db
from sqlalchemy import func
import json

recipe_bp = Blueprint('recipe_bp', __name__)

@recipe_bp.route('/create_recipe')
def create_recipe():
    """渲染创建食谱页面"""
    if 'user_id' not in session:
        flash('Please log in to create a recipe')
        return redirect(url_for('user_bp.login_page'))
    
    # 获取用户的宠物
    user_pets = Pet.query.filter_by(user_id=session['user_id']).all()
    if not user_pets:
        flash('Please add a pet before creating a recipe')
        return redirect(url_for('main.add_pet'))
    
    return render_template('create_recipe.html', pets=user_pets)

@recipe_bp.route('/api/ingredients')
def get_ingredients():
    """获取食材列表API"""
    try:
        category = request.args.get('category')
        search = request.args.get('search', '')
    
        query = db.session.query(Ingredient).filter(Ingredient.is_active == True)
    
        # 分类过滤
        if category:
            try:
                category_enum = IngredientCategory(category)
                query = query.filter(Ingredient.category == category_enum)
            except ValueError:
                pass
    
        # 搜索过滤
        if search:
            query = query.filter(
                db.or_(
                    Ingredient.name.contains(search),
                    Ingredient.name_en.contains(search)
                )
            )
    
        # 安全性过滤 - 只返回安全的食材
        query = query.filter(
            db.and_(
                Ingredient.is_safe_for_dogs == True,
                Ingredient.is_safe_for_cats == True
            )
        )
        
        ingredients = query.all()
        
        # 确保返回完整的营养信息
        result = []
        for ing in ingredients:
            ingredient_data = {
                'id': ing.id,
                'name': ing.name,
                'name_en': ing.name_en,
                'category': ing.category.value,
                'image_filename': ing.image_filename,
                'seasonality': ing.seasonality,
                'calories': float(ing.calories) if ing.calories else 0,
                'protein': float(ing.protein) if ing.protein else 0,
                'fat': float(ing.fat) if ing.fat else 0,
                'carbohydrate': float(ing.carbohydrate) if ing.carbohydrate else 0,
                'is_common_allergen': ing.is_common_allergen,
                'nutrition_summary': f"Protein {ing.protein or 0}g, Fat {ing.fat or 0}g, Carbs {ing.carbohydrate or 0}g (per 100g)"
            }
            result.append(ingredient_data)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Failed to load ingredients: {str(e)}")  # 用于调试
        return jsonify({'error': 'Failed to load ingredients'}), 500

@recipe_bp.route('/api/categories')
def get_categories():
    """获取食材分类列表"""
    categories = []
    for category in IngredientCategory:
        # 统计该分类下安全食材的数量
        count = db.session.query(Ingredient).filter(
            Ingredient.category == category,
            Ingredient.is_active == True,
            Ingredient.is_safe_for_dogs == True,
            Ingredient.is_safe_for_cats == True
        ).count()
        
        if count > 0:  # 只返回有食材的分类
            categories.append({
                'value': category.value,
                'name': get_category_name(category),
                'count': count,
                'icon': get_category_icon(category)
            })
    
    return jsonify(categories)

@recipe_bp.route('/api/calculate_nutrition', methods=['POST'])
def calculate_nutrition():
    """计算食谱营养成分"""
    if 'user_id' not in session:
        return jsonify({'error': '请先登录'}), 401
    
    data = request.get_json()
    ingredients_data = data.get('ingredients', [])
    pet_id = data.get('pet_id')
        
    if not ingredients_data:
        return jsonify({'error': '请选择食材'}), 400
    
    # 获取宠物信息
    pet = None
    if pet_id:
        from app.models.pet_model import Pet
        pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
        
    # 计算总营养成分
    total_nutrition = {
        'total_weight': 0.0,
        'calories': 0.0,
        'protein': 0.0,
        'fat': 0.0,
        'carbohydrate': 0.0,
        'fiber': 0.0,
        'calcium': 0.0,
        'phosphorus': 0.0,
        'vitamin_a': 0.0,
        'vitamin_d': 0.0,
        'taurine': 0.0,
        'omega_3': 0.0,
        'omega_6': 0.0
    }
    
    ingredient_details = []
    
    for item in ingredients_data:
        ingredient_id = item.get('ingredient_id')
        weight = float(item.get('weight', 0))
        
        ingredient = db.session.query(Ingredient).get(ingredient_id)
        if not ingredient:
            continue
        
        # 计算该食材的营养贡献 (weight 为克数)
        weight_ratio = weight / 100  # 转换为每100g的比例
        
        ingredient_nutrition = {
            'ingredient_id': ingredient.id,
            'name': ingredient.name,
            'weight': weight,
            'calories': ingredient.calories * weight_ratio,
            'protein': ingredient.protein * weight_ratio,
            'fat': ingredient.fat * weight_ratio,
            'carbohydrate': ingredient.carbohydrate * weight_ratio,
            'fiber': ingredient.fiber * weight_ratio,
            'calcium': ingredient.calcium * weight_ratio,
            'phosphorus': ingredient.phosphorus * weight_ratio,
            'vitamin_a': ingredient.vitamin_a * weight_ratio,
            'vitamin_d': ingredient.vitamin_d * weight_ratio,
            'taurine': ingredient.taurine * weight_ratio,
            'omega_3': ingredient.omega_3_fatty_acids * weight_ratio,
            'omega_6': ingredient.omega_6_fatty_acids * weight_ratio
        }
        
        ingredient_details.append(ingredient_nutrition)
    
        # 累加到总营养
        total_nutrition['total_weight'] += weight
        total_nutrition['calories'] += ingredient_nutrition['calories']
        total_nutrition['protein'] += ingredient_nutrition['protein']
        total_nutrition['fat'] += ingredient_nutrition['fat']
        total_nutrition['carbohydrate'] += ingredient_nutrition['carbohydrate']
        total_nutrition['fiber'] += ingredient_nutrition['fiber']
        total_nutrition['calcium'] += ingredient_nutrition['calcium']
        total_nutrition['phosphorus'] += ingredient_nutrition['phosphorus']
        total_nutrition['vitamin_a'] += ingredient_nutrition['vitamin_a']
        total_nutrition['vitamin_d'] += ingredient_nutrition['vitamin_d']
        total_nutrition['taurine'] += ingredient_nutrition['taurine']
        total_nutrition['omega_3'] += ingredient_nutrition['omega_3']
        total_nutrition['omega_6'] += ingredient_nutrition['omega_6']
    
        # 计算营养比例 (每100g干物质基础)
        if total_nutrition['total_weight'] > 0:
            nutrition_ratios = {
                'protein_percent': (total_nutrition['protein'] / total_nutrition['total_weight']) * 100,
                'fat_percent': (total_nutrition['fat'] / total_nutrition['total_weight']) * 100,
                'carbohydrate_percent': (total_nutrition['carbohydrate'] / total_nutrition['total_weight']) * 100,
                'fiber_percent': (total_nutrition['fiber'] / total_nutrition['total_weight']) * 100
            }
        else:
            nutrition_ratios = {'protein_percent': 0, 'fat_percent': 0, 'carbohydrate_percent': 0, 'fiber_percent': 0}
        
        # 营养需求对比
        nutrition_analysis = {'status': 'unknown', 'warnings': [], 'recommendations': []}
        
        if pet:
            # 获取营养需求标准
            from app.models.nutrition_requirements_model import NutritionRequirement, PetType, LifeStage, ActivityLevel
            pet_type = PetType.DOG if pet.species.lower() == 'dog' else PetType.CAT
            life_stage = determine_life_stage(pet.age, pet.species)
            
            requirement = NutritionRequirement.query.filter_by(
                pet_type=pet_type,
                life_stage=life_stage,
                activity_level=ActivityLevel.MODERATE
            ).filter(
                NutritionRequirement.min_weight <= pet.weight,
                NutritionRequirement.max_weight >= pet.weight
            ).first()
            
            if requirement:
                # 分析营养状况
                analysis = analyze_nutrition_status(nutrition_ratios, requirement, total_nutrition, pet.weight)
                nutrition_analysis.update(analysis)
    
        return jsonify({
            'total_nutrition': total_nutrition,
            'nutrition_ratios': nutrition_ratios,
            'ingredient_details': ingredient_details,
            'nutrition_analysis': nutrition_analysis
        })

@recipe_bp.route('/api/suggest_weights', methods=['POST'])
def suggest_weights():
    """根据宠物信息推荐食材重量"""
    if 'user_id' not in session:
        return jsonify({'error': '请先登录'}), 401
    
    data = request.get_json()
    ingredient_ids = data.get('ingredient_ids', [])
    pet_id = data.get('pet_id')
    
    if not ingredient_ids or not pet_id:
        return jsonify({'error': '参数不完整'}), 400
    
    # 获取宠物信息
    pet = db.session.query(Pet).filter_by(id=pet_id, user_id=session['user_id']).first()
    if not pet:
        return jsonify({'error': '宠物信息不存在'}), 404
    
    # 计算每日食物总量 (基于体重的简单估算)
    daily_food_amount = calculate_daily_food_amount(pet.weight, pet.species, pet.age)
    
    # 获取选中的食材
    ingredients = db.session.query(Ingredient).filter(Ingredient.id.in_(ingredient_ids)).all()
    
    # 简单的重量分配策略
    suggestions = []
    ingredient_count = len(ingredients)
    
    if ingredient_count > 0:
        # 基础分配策略
        meat_ratio = 0.6  # 肉类占60%
        veg_ratio = 0.3   # 蔬菜占30%
        grain_ratio = 0.1 # 谷物占10%
        
        meat_ingredients = [ing for ing in ingredients if ing.category in [IngredientCategory.RED_MEAT, IngredientCategory.WHITE_MEAT, IngredientCategory.FISH, IngredientCategory.ORGANS]]
        veg_ingredients = [ing for ing in ingredients if ing.category == IngredientCategory.VEGETABLES]
        grain_ingredients = [ing for ing in ingredients if ing.category == IngredientCategory.GRAINS]
        fruit_ingredients = [ing for ing in ingredients if ing.category == IngredientCategory.FRUITS]
        
        for ingredient in ingredients:
            if ingredient in meat_ingredients and len(meat_ingredients) > 0:
                suggested_weight = (daily_food_amount * meat_ratio) / len(meat_ingredients)
            elif ingredient in veg_ingredients and len(veg_ingredients) > 0:
                suggested_weight = (daily_food_amount * veg_ratio) / len(veg_ingredients)
            elif ingredient in grain_ingredients and len(grain_ingredients) > 0:
                suggested_weight = (daily_food_amount * grain_ratio) / len(grain_ingredients)
            elif ingredient in fruit_ingredients and len(fruit_ingredients) > 0:
                suggested_weight = min(20, daily_food_amount * 0.05)  # 水果限制在20g以内
            else:
                suggested_weight = daily_food_amount / ingredient_count
            
            # 设置合理范围
            min_weight = max(5, suggested_weight * 0.5)
            max_weight = min(500, suggested_weight * 2)
            suggested_weight = max(min_weight, min(max_weight, suggested_weight))
            
            suggestions.append({
                'ingredient_id': ingredient.id,
                'suggested_weight': round(suggested_weight),
                'min_weight': round(min_weight),
                'max_weight': round(max_weight),
                'unit': 'g'
            })
    
    return jsonify({
        'pet_info': {
            'name': pet.name,
            'weight': pet.weight,
            'daily_food_amount': daily_food_amount
        },
        'suggestions': suggestions
    })

@recipe_bp.route('/api/save_recipe', methods=['POST'])
def save_recipe():
    """保存食谱"""
    if 'user_id' not in session:
        return jsonify({'error': '请先登录'}), 401
    
    data = request.get_json()
    recipe_name = data.get('name', '').strip()
    recipe_description = data.get('description', '').strip()
    pet_id = data.get('pet_id')
    ingredients_data = data.get('ingredients', [])
    is_draft = data.get('is_draft', True)
    
    if not recipe_name:
        return jsonify({'error': '请输入食谱名称'}), 400
    
    if not ingredients_data:
        return jsonify({'error': '请选择食材'}), 400
    
    try:
        # 创建食谱
        recipe = Recipe(
            name=recipe_name,
            description=recipe_description,
            user_id=session['user_id'],
            pet_id=pet_id,
            status=RecipeStatus.DRAFT if is_draft else RecipeStatus.PUBLISHED
        )
        
        db.session.add(recipe)
        db.session.flush()  # 获取recipe.id
        
        # 添加食材
        for item in ingredients_data:
            ingredient_id = item.get('ingredient_id')
            weight = float(item.get('weight', 0))
            
            if weight <= 0:
                continue
                
            ingredient = db.session.query(Ingredient).get(ingredient_id)
            if not ingredient:
                continue
            
            # 计算营养贡献
            weight_ratio = weight / 100
            
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_id,
                weight=weight,
                contributed_calories=ingredient.calories * weight_ratio,
                contributed_protein=ingredient.protein * weight_ratio,
                contributed_fat=ingredient.fat * weight_ratio,
                contributed_carbohydrate=ingredient.carbohydrate * weight_ratio,
                contributed_calcium=ingredient.calcium * weight_ratio,
                contributed_phosphorus=ingredient.phosphorus * weight_ratio
            )
            
            db.session.add(recipe_ingredient)
        
        # 计算食谱总营养
        recipe.calculate_nutrition()
        recipe.check_suitability()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Recipe saved as a draft' if is_draft else 'Recipe published successfully',
            'recipe_id': recipe.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Save failed: {str(e)}'}), 500

# 辅助函数
def get_category_name(category):
    """获取分类英文名称"""
    if isinstance(category, str):
        category = IngredientCategory(category)
    
    category_names = {
        IngredientCategory.RED_MEAT: 'Red Meat',
        IngredientCategory.WHITE_MEAT: 'White Meat',
        IngredientCategory.FISH: 'Fish',
        IngredientCategory.ORGANS: 'Organs',
        IngredientCategory.VEGETABLES: 'Vegetables',
        IngredientCategory.FRUITS: 'Fruits',
        IngredientCategory.GRAINS: 'Grains',
        IngredientCategory.DAIRY: 'Dairy',
        IngredientCategory.SUPPLEMENTS: 'Supplements',
        IngredientCategory.OILS: 'Oils'
    }
    return category_names.get(category, category.value if hasattr(category, 'value') else str(category))

def get_category_icon(category):
    """获取分类图标"""
    if isinstance(category, str):
        category = IngredientCategory(category)

    category_icons = {
        IngredientCategory.RED_MEAT: 'fas fa-drumstick-bite',
        IngredientCategory.WHITE_MEAT: 'fas fa-drumstick-bite',
        IngredientCategory.FISH: 'fas fa-fish',
        IngredientCategory.ORGANS: 'fas fa-heart',
        IngredientCategory.VEGETABLES: 'fas fa-carrot',
        IngredientCategory.FRUITS: 'fas fa-apple-alt',
        IngredientCategory.GRAINS: 'fas fa-seedling',
        IngredientCategory.DAIRY: 'fas fa-cheese',
        IngredientCategory.SUPPLEMENTS: 'fas fa-pills',
        IngredientCategory.OILS: 'fas fa-tint'
    }
    return category_icons.get(category, 'fas fa-utensils')

def determine_life_stage(age, species):
    """根据年龄和品种确定生命阶段"""
    if species.lower() == 'dog':
        if age < 1:
            return LifeStage.PUPPY_KITTEN
        elif age >= 7:
            return LifeStage.SENIOR
        else:
            return LifeStage.ADULT
    else:  # cat
        if age < 1:
            return LifeStage.PUPPY_KITTEN
        elif age >= 7:
            return LifeStage.SENIOR
        else:
            return LifeStage.ADULT

def calculate_daily_food_amount(weight, species, age):
    """计算每日食物总量 (克)"""
    # 基础代谢率计算 (简化版)
    if species.lower() == 'dog':
        if age < 1:  # 幼犬
            daily_amount = weight * 50
        elif age >= 7:  # 老年犬
            daily_amount = weight * 25
        else:  # 成年犬
            daily_amount = weight * 30
    else:  # cat
        if age < 1:  # 幼猫
            daily_amount = weight * 60
        elif age >= 7:  # 老年猫
            daily_amount = weight * 35
        else:  # 成年猫
            daily_amount = weight * 40
    
    # 设置合理范围
    return max(50, min(2000, daily_amount))

def analyze_nutrition_status(nutrition_ratios, requirement, total_nutrition, pet_weight):
    """分析营养状况"""
    warnings = []
    recommendations = []
    status = 'good'
    
    # 检查蛋白质
    if nutrition_ratios['protein_percent'] < requirement.protein_min:
        warnings.append(f"蛋白质含量偏低 ({nutrition_ratios['protein_percent']:.1f}%，建议≥{requirement.protein_min}%)")
        recommendations.append("增加肉类、鱼类或蛋类食材")
        status = 'warning'
    
    # 检查脂肪
    if nutrition_ratios['fat_percent'] < requirement.fat_min:
        warnings.append(f"脂肪含量偏低 ({nutrition_ratios['fat_percent']:.1f}%，建议≥{requirement.fat_min}%)")
        recommendations.append("适量添加鱼油或增加脂肪含量高的食材")
        status = 'warning'
    elif requirement.fat_max and nutrition_ratios['fat_percent'] > requirement.fat_max:
        warnings.append(f"脂肪含量偏高 ({nutrition_ratios['fat_percent']:.1f}%，建议≤{requirement.fat_max}%)")
        recommendations.append("减少高脂肪食材的用量")
        status = 'warning'
    
    # 检查钙磷比
    if total_nutrition['calcium'] > 0 and total_nutrition['phosphorus'] > 0:
        ca_p_ratio = total_nutrition['calcium'] / total_nutrition['phosphorus']
        if requirement.calcium_phosphorus_ratio_min and ca_p_ratio < requirement.calcium_phosphorus_ratio_min:
            warnings.append(f"钙磷比偏低 ({ca_p_ratio:.2f}，建议≥{requirement.calcium_phosphorus_ratio_min})")
            recommendations.append("增加钙质丰富的食材如骨粉或钙补充剂")
            status = 'warning'
        elif requirement.calcium_phosphorus_ratio_max and ca_p_ratio > requirement.calcium_phosphorus_ratio_max:
            warnings.append(f"钙磷比偏高 ({ca_p_ratio:.2f}，建议≤{requirement.calcium_phosphorus_ratio_max})")
            recommendations.append("调整钙磷比例")
            status = 'warning'
    
    # 检查牛磺酸 (猫咪)
    if requirement.taurine_min and total_nutrition['taurine'] < requirement.taurine_min:
        warnings.append("牛磺酸含量不足，对猫咪心脏健康重要")
        recommendations.append("增加心脏、肝脏等内脏类食材")
        status = 'warning'
    
    # 检查总热量
    daily_calories_needed = requirement.calories_per_kg * pet_weight
    if total_nutrition['calories'] < daily_calories_needed * 0.8:
        warnings.append("总热量可能不足")
        recommendations.append("增加食材分量或添加高热量食材")
        status = 'warning'
    elif total_nutrition['calories'] > daily_calories_needed * 1.3:
        warnings.append("总热量可能过高")
        recommendations.append("减少食材分量或选择低热量食材")
        status = 'warning'
    
    if not warnings:
        status = 'good'
        recommendations.append("营养配比良好，可以给宠物食用")
    
    return {
        'status': status,
        'warnings': warnings,
        'recommendations': recommendations,
        'daily_calories_needed': daily_calories_needed,
        'calcium_phosphorus_ratio': total_nutrition['calcium'] / total_nutrition['phosphorus'] if total_nutrition['phosphorus'] > 0 else 0
    }