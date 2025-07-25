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
