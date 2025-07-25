"""
食谱推荐API路由
提供智能食谱推荐功能
"""

from flask import Blueprint, request, jsonify, session, render_template
from app.models.ingredient_model import Ingredient
from app.models.pet_model import Pet
from app.models.recipe_model import Recipe
from app.utils.recipe_recommendation_service import RecipeRecommendationService
from app.extensions import db

recommendation_api_bp = Blueprint('recommendation_api', __name__)

@recommendation_api_bp.route('/api/recommendations', methods=['POST'])
def get_recipe_recommendations():
    """获取食谱推荐"""
    try:
        data = request.get_json()
        ingredient_ids = data.get('ingredient_ids', [])
        pet_id = data.get('pet_id')
        exclude_allergens = data.get('exclude_allergens', [])
        limit = data.get('limit', 2)
        
        if not ingredient_ids:
            return jsonify({'error': '请选择食材'}), 400
        
        # 验证用户权限（如果有pet_id）
        if pet_id and session.get('user_id'):
            pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
            if not pet:
                return jsonify({'error': '宠物信息不存在'}), 404
        
        # 创建推荐服务
        recommendation_service = RecipeRecommendationService()
        
        # 获取推荐
        recommendations = recommendation_service.get_recommendations(
            selected_ingredient_ids=ingredient_ids,
            pet_id=pet_id,
            exclude_allergens=exclude_allergens,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total_count': len(recommendations)
        })
        
    except Exception as e:
        print(f"推荐API错误: {e}")
        return jsonify({'error': '获取推荐失败，请稍后重试'}), 500

@recommendation_api_bp.route('/recipe/recommendations')
def recipe_recommendations_page():
    """食谱推荐页面"""
    # 从URL参数获取选择的食材ID
    ingredient_ids_str = request.args.get('ingredients', '')
    pet_id = request.args.get('pet_id')
    
    # 解析食材ID
    ingredient_ids = []
    if ingredient_ids_str:
        try:
            ingredient_ids = [int(id_str) for id_str in ingredient_ids_str.split(',') if id_str.strip()]
        except ValueError:
            ingredient_ids = []
    
    # 获取食材信息
    selected_ingredients = []
    if ingredient_ids:
        selected_ingredients = Ingredient.query.filter(Ingredient.id.in_(ingredient_ids)).all()
    
    # 获取宠物信息
    pet = None
    if pet_id and session.get('user_id'):
        pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
    
    # 如果有选择的食材，立即获取推荐
    recommendations = []
    if ingredient_ids:
        recommendation_service = RecipeRecommendationService()
        recommendations = recommendation_service.get_recommendations(
            selected_ingredient_ids=ingredient_ids,
            pet_id=int(pet_id) if pet_id else None,
            limit=3  # 页面显示更多推荐
        )
    
    return render_template('recipe_recommendations.html',
                        selected_ingredients=selected_ingredients,
                        pet=pet,
                        recommendations=recommendations)

@recommendation_api_bp.route('/api/recipe/<int:recipe_id>/details')
def get_recipe_details(recipe_id):
    """获取食谱详细信息"""
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': '食谱不存在'}), 404
        
        # 检查访问权限
        if not recipe.is_public and recipe.user_id != session.get('user_id'):
            return jsonify({'error': '无权访问此食谱'}), 403
        
        # 获取食材详情
        ingredients_details = []
        for ri in recipe.ingredients:
            ingredients_details.append({
                'id': ri.ingredient.id,
                'name': ri.ingredient.name,
                'category': ri.ingredient.category.value,
                'weight': ri.weight,
                'preparation_note': ri.preparation_note,
                'nutrition_contribution': {
                    'calories': ri.contributed_calories,
                    'protein': ri.contributed_protein,
                    'fat': ri.contributed_fat,
                    'carbohydrate': ri.contributed_carbohydrate
                }
            })
        
        # 计算营养比例
        nutrition_ratios = {}
        if recipe.total_weight > 0:
            nutrition_ratios = {
                'protein_percent': round((recipe.total_protein / recipe.total_weight) * 100, 1),
                'fat_percent': round((recipe.total_fat / recipe.total_weight) * 100, 1),
                'carb_percent': round((recipe.total_carbohydrate / recipe.total_weight) * 100, 1),
                'fiber_percent': round((recipe.total_fiber / recipe.total_weight) * 100, 1),
                'calories_per_100g': round((recipe.total_calories / recipe.total_weight) * 100, 1)
            }
        
        recipe_details = {
            'id': recipe.id,
            'name': recipe.name,
            'description': recipe.description,
            'total_weight': recipe.total_weight,
            'total_nutrition': {
                'calories': recipe.total_calories,
                'protein': recipe.total_protein,
                'fat': recipe.total_fat,
                'carbohydrate': recipe.total_carbohydrate,
                'fiber': recipe.total_fiber,
                'calcium': recipe.total_calcium,
                'phosphorus': recipe.total_phosphorus,
                'calcium_phosphorus_ratio': recipe.total_calcium / recipe.total_phosphorus if recipe.total_phosphorus > 0 else 0
            },
            'nutrition_ratios': nutrition_ratios,
            'ingredients': ingredients_details,
            'suitability': {
                'dogs': recipe.suitable_for_dogs,
                'cats': recipe.suitable_for_cats,
                'puppies': recipe.suitable_for_puppies,
                'kittens': recipe.suitable_for_kittens,
                'seniors': recipe.suitable_for_seniors
            },
            'nutrition_score': recipe.nutrition_score,
            'balance_score': recipe.balance_score,
            'usage_count': recipe.usage_count,
            'rating_avg': recipe.rating_avg,
            'created_at': recipe.created_at.isoformat() if recipe.created_at else None
        }
        
        return jsonify({
            'success': True,
            'recipe': recipe_details
        })
        
    except Exception as e:
        print(f"获取食谱详情错误: {e}")
        return jsonify({'error': '获取食谱详情失败'}), 500

@recommendation_api_bp.route('/api/recipe/<int:recipe_id>/copy', methods=['POST'])
def copy_recipe_to_user(recipe_id):
    """复制推荐食谱到用户账户"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        original_recipe = Recipe.query.get(recipe_id)
        if not original_recipe:
            return jsonify({'error': '食谱不存在'}), 404
        
        data = request.get_json()
        new_name = data.get('name', f"{original_recipe.name} (副本)")
        pet_id = data.get('pet_id')
        
        # 验证宠物权限
        if pet_id:
            pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
            if not pet:
                return jsonify({'error': '宠物信息不存在'}), 404
        
        # 创建新食谱
        new_recipe = Recipe(
            name=new_name,
            description=f"基于 '{original_recipe.name}' 创建的个人食谱",
            user_id=session['user_id'],
            pet_id=pet_id,
            status='draft',
            is_public=False
        )
        
        db.session.add(new_recipe)
        db.session.flush()  # 获取新食谱ID
        
        # 复制食材关联
        from app.models.recipe_ingredient_model import RecipeIngredient
        
        for original_ri in original_recipe.ingredients:
            new_ri = RecipeIngredient(
                recipe_id=new_recipe.id,
                ingredient_id=original_ri.ingredient_id,
                weight=original_ri.weight,
                preparation_note=original_ri.preparation_note
            )
            db.session.add(new_ri)
        
        # 重新计算营养成分
        new_recipe.calculate_nutrition()
        new_recipe.check_suitability()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '食谱已复制到您的账户',
            'recipe_id': new_recipe.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"复制食谱错误: {e}")
        return jsonify({'error': '复制食谱失败'}), 500

@recommendation_api_bp.route('/api/similar-recipes/<int:recipe_id>')
def get_similar_recipes(recipe_id):
    """获取相似食谱"""
    try:
        base_recipe = Recipe.query.get(recipe_id)
        if not base_recipe:
            return jsonify({'error': '食谱不存在'}), 404
        
        # 获取基础食谱的食材ID
        ingredient_ids = [ri.ingredient_id for ri in base_recipe.ingredients]
        
        if not ingredient_ids:
            return jsonify({'recommendations': []})
        
        # 使用推荐服务查找相似食谱
        recommendation_service = RecipeRecommendationService()
        similar_recipes = recommendation_service.get_recommendations(
            selected_ingredient_ids=ingredient_ids,
            limit=4  # 返回4个相似食谱
        )
        
        # 过滤掉原食谱本身
        similar_recipes = [rec for rec in similar_recipes if rec['recipe_id'] != recipe_id]
        
        return jsonify({
            'success': True,
            'similar_recipes': similar_recipes[:3]  # 最多返回3个
        })
        
    except Exception as e:
        print(f"获取相似食谱错误: {e}")
        return jsonify({'error': '获取相似食谱失败'}), 500