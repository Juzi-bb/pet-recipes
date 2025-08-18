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
            # 安全处理可能为 None 的营养字段
            calories = float(ing.calories) if ing.calories is not None else 0.0
            protein = float(ing.protein) if ing.protein is not None else 0.0
            fat = float(ing.fat) if ing.fat is not None else 0.0
            carbohydrate = float(ing.carbohydrate) if ing.carbohydrate is not None else 0.0
            fiber = float(ing.fiber) if ing.fiber is not None else 0.0
            calcium = float(ing.calcium) if ing.calcium is not None else 0.0
            phosphorus = float(ing.phosphorus) if ing.phosphorus is not None else 0.0
            
            # 生成营养摘要文本 - 前端期望的字段
            nutrition_summary = f"Calories: {calories:.0f}kcal/100g | Protein: {protein:.1f}g | Fat: {fat:.1f}g | Carbs: {carbohydrate:.1f}g"
            
            # 如果有钙磷信息，添加到摘要中
            if calcium > 0 or phosphorus > 0:
                nutrition_summary += f" | Ca: {calcium:.0f}mg | P: {phosphorus:.0f}mg"
                        
            ingredient_data = {
                'id': ing.id,
                'name': ing.name,
                'name_en': ing.name_en,
                'category': ing.category.value,
                'image_filename': ing.image_filename,
                'seasonality': ing.seasonality,
                # 基础营养信息
                'calories': calories,
                'protein': protein,
                'fat': fat,
                'carbohydrate': carbohydrate,
                'fiber': fiber,
                'moisture': float(ing.moisture) if ing.moisture is not None else 0.0,
                'ash': float(ing.ash) if ing.ash is not None else 0.0,

                # 矿物质
                'calcium': calcium,
                'phosphorus': phosphorus,
                'potassium': float(ing.potassium) if ing.potassium is not None else 0.0,
                'sodium': float(ing.sodium) if ing.sodium is not None else 0.0,
                'magnesium': float(ing.magnesium) if ing.magnesium is not None else 0.0,
                'iron': float(ing.iron) if ing.iron is not None else 0.0,
                'zinc': float(ing.zinc) if ing.zinc is not None else 0.0,
                
                # 维生素
                'vitamin_a': float(ing.vitamin_a) if ing.vitamin_a is not None else 0.0,
                'vitamin_d': float(ing.vitamin_d) if ing.vitamin_d is not None else 0.0,
                'vitamin_e': float(ing.vitamin_e) if ing.vitamin_e is not None else 0.0,
                'taurine': float(ing.taurine) if ing.taurine is not None else 0.0,
                
                # 脂肪酸
                'omega_3_fatty_acids': float(ing.omega_3_fatty_acids) if ing.omega_3_fatty_acids is not None else 0.0,
                'omega_6_fatty_acids': float(ing.omega_6_fatty_acids) if ing.omega_6_fatty_acids is not None else 0.0,
                
                # 安全性信息
                'is_safe_for_dogs': bool(ing.is_safe_for_dogs),
                'is_safe_for_cats': bool(ing.is_safe_for_cats),
                'is_common_allergen': bool(ing.is_common_allergen),
                
                # 前端显示字段 - 关键修复
                'nutrition_summary': nutrition_summary,
                
                # 食材指南信息
                'description': ing.description,
                'benefits': ing.benefits,
                'preparation_method': ing.preparation_method,
                'pro_tip': ing.pro_tip,
                'allergy_alert': ing.allergy_alert,
                'storage_notes': ing.storage_notes
            }
            result.append(ingredient_data)
        
        # 按名称排序
        result.sort(key=lambda x: x['name'])
        
        return jsonify({
            'success': True,
            'ingredients': result,
            'total_count': len(result)
        })
        
    except Exception as e:
        print(f"Failed to load ingredients: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to load ingredients', 'details': str(e)}), 500

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
