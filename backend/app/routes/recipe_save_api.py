"""
保存食谱API路由
处理食谱的创建、更新和发布
"""

from flask import Blueprint, request, jsonify, session
from app.models.recipe_model import Recipe, RecipeStatus
from app.models.recipe_ingredient_model import RecipeIngredient
from app.models.ingredient_model import Ingredient
from app.models.pet_model import Pet
from app.utils.allergen_service import AllergenService
from app.extensions import db
from datetime import datetime

recipe_save_api_bp = Blueprint('recipe_save_api', __name__)

@recipe_save_api_bp.route('/api/recipe/save', methods=['POST'])
def save_recipe():
    """保存新食谱"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        data = request.get_json()
        recipe_name = data.get('name', '').strip()
        recipe_description = data.get('description', '').strip()
        pet_id = data.get('pet_id')
        nutrition_plan_id = data.get('nutrition_plan_id')
        ingredients_data = data.get('ingredients', [])
        is_public = data.get('is_public', False)
        
        # 验证必填字段
        if not recipe_name:
            return jsonify({'error': '请输入食谱名称'}), 400
        
        if not ingredients_data:
            return jsonify({'error': '请选择食材'}), 400
        
        # 验证宠物权限（如果指定了宠物）
        if pet_id:
            pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
            if not pet:
                return jsonify({'error': '宠物信息不存在'}), 404
        
        # 检查食谱名称是否重复
        existing_recipe = Recipe.query.filter_by(
            name=recipe_name,
            user_id=session['user_id']
        ).first()
        
        if existing_recipe:
            return jsonify({'error': '您已有同名食谱，请使用不同的名称'}), 400
        
        # 验证食材数据
        ingredient_ids = [item.get('ingredient_id') for item in ingredients_data]
        ingredients = Ingredient.query.filter(Ingredient.id.in_(ingredient_ids)).all()
        ingredient_dict = {ing.id: ing for ing in ingredients}
        
        # 检查过敏安全性
        if pet_id:
            safety_check = AllergenService.check_recipe_safety(ingredient_ids, pet_id)
            if not safety_check['is_safe']:
                return jsonify({
                    'error': '食谱包含过敏食材',
                    'allergens': safety_check['allergens'],
                    'warnings': safety_check['warnings']
                }), 400
        
        # 创建食谱
        recipe = Recipe(
            name=recipe_name,
            description=recipe_description,
            user_id=session['user_id'],
            pet_id=pet_id,
            status=RecipeStatus.PUBLISHED if is_public else RecipeStatus.DRAFT,
            is_public=is_public
        )
        
        # 添加营养方案标签
        if nutrition_plan_id:
            tags = {'nutrition_plan': nutrition_plan_id}
            recipe.tags = str(tags)
        
        db.session.add(recipe)
        db.session.flush()  # 获取recipe.id
        
        # 添加食材关联
        total_weight = 0
        for item in ingredients_data:
            ingredient_id = item.get('ingredient_id')
            weight = float(item.get('weight', 0))
            
            if weight <= 0 or ingredient_id not in ingredient_dict:
                continue
            
            total_weight += weight
            
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_id,
                weight=weight,
                preparation_note=item.get('preparation_note', '')
            )
            
            db.session.add(recipe_ingredient)
        
        # 验证食谱是否有足够的内容
        if total_weight < 50:  # 最少50g
            db.session.rollback()
            return jsonify({'error': '食谱总重量太少，请至少添加50g食材'}), 400
        
        # 计算营养成分
        recipe.calculate_nutrition()
        recipe.check_suitability()
        
        # 计算营养评分（简化版）
        recipe.nutrition_score = calculate_nutrition_score(recipe)
        recipe.balance_score = calculate_balance_score(recipe)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '食谱保存成功！' if not is_public else '食谱已发布到社区！',
            'recipe_id': recipe.id,
            'recipe_name': recipe.name
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"保存食谱失败: {e}")
        return jsonify({'error': '保存失败，请稍后重试'}), 500

@recipe_save_api_bp.route('/api/recipe/<int:recipe_id>/update', methods=['PUT'])
def update_recipe(recipe_id):
    """更新现有食谱"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        # 验证食谱权限
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=session['user_id']).first()
        if not recipe:
            return jsonify({'error': '食谱不存在或无权限'}), 404
        
        data = request.get_json()
        recipe_name = data.get('name', '').strip()
        recipe_description = data.get('description', '').strip()
        ingredients_data = data.get('ingredients', [])
        is_public = data.get('is_public', False)
        
        # 验证必填字段
        if not recipe_name:
            return jsonify({'error': '请输入食谱名称'}), 400
        
        if not ingredients_data:
            return jsonify({'error': '请选择食材'}), 400
        
        # 检查食谱名称是否与其他食谱重复
        existing_recipe = Recipe.query.filter(
            Recipe.name == recipe_name,
            Recipe.user_id == session['user_id'],
            Recipe.id != recipe_id
        ).first()
        
        if existing_recipe:
            return jsonify({'error': '您已有同名食谱，请使用不同的名称'}), 400
        
        # 更新基础信息
        recipe.name = recipe_name
        recipe.description = recipe_description
        recipe.is_public = is_public
        recipe.updated_at = datetime.utcnow()
        
        # 如果是从草稿发布到公开，更新状态
        if is_public and recipe.status == RecipeStatus.DRAFT:
            recipe.status = RecipeStatus.PUBLISHED
        
        # 删除现有食材关联
        RecipeIngredient.query.filter_by(recipe_id=recipe_id).delete()
        
        # 验证食材数据
        ingredient_ids = [item.get('ingredient_id') for item in ingredients_data]
        ingredients = Ingredient.query.filter(Ingredient.id.in_(ingredient_ids)).all()
        ingredient_dict = {ing.id: ing for ing in ingredients}
        
        # 重新添加食材关联
        total_weight = 0
        for item in ingredients_data:
            ingredient_id = item.get('ingredient_id')
            weight = float(item.get('weight', 0))
            
            if weight <= 0 or ingredient_id not in ingredient_dict:
                continue
            
            total_weight += weight
            
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_id,
                weight=weight,
                preparation_note=item.get('preparation_note', '')
            )
            
            db.session.add(recipe_ingredient)
        
        # 验证食谱内容
        if total_weight < 50:
            db.session.rollback()
            return jsonify({'error': '食谱总重量太少，请至少添加50g食材'}), 400
        
        # 重新计算营养成分
        recipe.calculate_nutrition()
        recipe.check_suitability()
        recipe.nutrition_score = calculate_nutrition_score(recipe)
        recipe.balance_score = calculate_balance_score(recipe)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '食谱更新成功！',
            'recipe_id': recipe.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"更新食谱失败: {e}")
        return jsonify({'error': '更新失败，请稍后重试'}), 500

@recipe_save_api_bp.route('/api/recipe/<int:recipe_id>/publish', methods=['POST'])
def publish_recipe(recipe_id):
    """发布食谱到社区"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        # 验证食谱权限
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=session['user_id']).first()
        if not recipe:
            return jsonify({'error': '食谱不存在或无权限'}), 404
        
        # 检查食谱是否已发布
        if recipe.is_public:
            return jsonify({'error': '食谱已经发布到社区'}), 400
        
        # 验证食谱完整性
        if recipe.total_weight < 50:
            return jsonify({'error': '食谱内容不完整，无法发布'}), 400
        
        if len(recipe.ingredients) < 2:
            return jsonify({'error': '食谱至少需要2种食材才能发布'}), 400
        
        # 更新发布状态
        recipe.is_public = True
        recipe.status = RecipeStatus.PUBLISHED
        recipe.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '食谱已成功发布到社区！'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"发布食谱失败: {e}")
        return jsonify({'error': '发布失败，请稍后重试'}), 500

@recipe_save_api_bp.route('/api/recipe/<int:recipe_id>/unpublish', methods=['POST'])
def unpublish_recipe(recipe_id):
    """取消发布食谱"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        # 验证食谱权限
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=session['user_id']).first()
        if not recipe:
            return jsonify({'error': '食谱不存在或无权限'}), 404
        
        # 检查食谱是否已发布
        if not recipe.is_public:
            return jsonify({'error': '食谱未发布'}), 400
        
        # 更新发布状态
        recipe.is_public = False
        recipe.status = RecipeStatus.DRAFT
        recipe.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '食谱已从社区撤回'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"撤回食谱失败: {e}")
        return jsonify({'error': '撤回失败，请稍后重试'}), 500

@recipe_save_api_bp.route('/api/recipe/<int:recipe_id>/delete', methods=['DELETE'])
def delete_recipe(recipe_id):
    """删除食谱"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        # 验证食谱权限
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=session['user_id']).first()
        if not recipe:
            return jsonify({'error': '食谱不存在或无权限'}), 404
        
        recipe_name = recipe.name
        
        # 删除食谱（级联删除会自动删除相关的食材关联）
        db.session.delete(recipe)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'食谱 "{recipe_name}" 已删除'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"删除食谱失败: {e}")
        return jsonify({'error': '删除失败，请稍后重试'}), 500

def calculate_nutrition_score(recipe):
    """计算营养评分（简化版）"""
    try:
        if recipe.total_weight <= 0:
            return 0
        
        score = 0
        
        # 蛋白质比例评分 (30分)
        protein_percent = (recipe.total_protein / recipe.total_weight) * 100
        if 18 <= protein_percent <= 35:
            score += 30
        elif 15 <= protein_percent < 18 or 35 < protein_percent <= 40:
            score += 20
        elif protein_percent >= 10:
            score += 10
        
        # 脂肪比例评分 (20分)
        fat_percent = (recipe.total_fat / recipe.total_weight) * 100
        if 5.5 <= fat_percent <= 20:
            score += 20
        elif 4 <= fat_percent < 5.5 or 20 < fat_percent <= 25:
            score += 15
        elif fat_percent >= 2:
            score += 10
        
        # 钙磷比评分 (20分)
        if recipe.total_phosphorus > 0:
            ca_p_ratio = recipe.total_calcium / recipe.total_phosphorus
            if 1.0 <= ca_p_ratio <= 2.0:
                score += 20
            elif 0.8 <= ca_p_ratio < 1.0 or 2.0 < ca_p_ratio <= 2.5:
                score += 15
            elif ca_p_ratio >= 0.5:
                score += 10
        
        # 食材多样性评分 (15分)
        ingredient_count = len(recipe.ingredients)
        if ingredient_count >= 5:
            score += 15
        elif ingredient_count >= 3:
            score += 10
        elif ingredient_count >= 2:
            score += 5
        
        # 营养密度评分 (15分)
        calories_per_100g = (recipe.total_calories / recipe.total_weight) * 100 if recipe.total_weight > 0 else 0
        if 250 <= calories_per_100g <= 400:
            score += 15
        elif 200 <= calories_per_100g < 250 or 400 < calories_per_100g <= 500:
            score += 10
        elif 150 <= calories_per_100g <= 600:
            score += 5
        
        return min(score, 100)  # 最高100分
        
    except Exception as e:
        print(f"计算营养评分失败: {e}")
        return 0

def calculate_balance_score(recipe):
    """计算营养平衡评分（简化版）"""
    try:
        if recipe.total_weight <= 0:
            return 0
        
        score = 0
        
        # 宏量营养素平衡 (40分)
        protein_percent = (recipe.total_protein / recipe.total_weight) * 100
        fat_percent = (recipe.total_fat / recipe.total_weight) * 100
        carb_percent = (recipe.total_carbohydrate / recipe.total_weight) * 100
        
        # 理想比例：蛋白质20-30%, 脂肪10-15%, 碳水化合物5-15%
        protein_balance = max(0, 20 - abs(25 - protein_percent)) / 20 * 15
        fat_balance = max(0, 10 - abs(12.5 - fat_percent)) / 10 * 15
        carb_balance = max(0, 15 - abs(10 - carb_percent)) / 15 * 10
        
        score += protein_balance + fat_balance + carb_balance
        
        # 矿物质平衡 (30分)
        if recipe.total_calcium > 0 and recipe.total_phosphorus > 0:
            ca_mg = recipe.total_calcium
            p_mg = recipe.total_phosphorus
            
            # 钙磷平衡
            ca_p_ratio = ca_mg / p_mg
            ca_p_score = max(0, 20 - abs(1.5 - ca_p_ratio) * 10)
            score += min(ca_p_score, 20)
            
            # 微量元素平衡（简化）
            if recipe.total_iron > 0 and recipe.total_zinc > 0:
                score += 10
        
        # 维生素平衡 (20分)
        vitamin_count = 0
        if recipe.total_vitamin_a > 0: vitamin_count += 1
        if recipe.total_vitamin_d > 0: vitamin_count += 1
        if recipe.total_vitamin_e > 0: vitamin_count += 1
        if recipe.total_thiamine > 0: vitamin_count += 1
        if recipe.total_riboflavin > 0: vitamin_count += 1
        if recipe.total_niacin > 0: vitamin_count += 1
        
        score += min(vitamin_count * 3, 20)  # 每种维生素3分，最多20分
        
        # 必需脂肪酸平衡 (10分)
        if recipe.total_omega_3 > 0 and recipe.total_omega_6 > 0:
            omega_ratio = recipe.total_omega_6 / recipe.total_omega_3
            # 理想比例约5:1到10:1
            if 5 <= omega_ratio <= 10:
                score += 10
            elif 3 <= omega_ratio < 5 or 10 < omega_ratio <= 15:
                score += 7
            elif omega_ratio <= 20:
                score += 5
        
        return min(score, 100)  # 最高100分
        
    except Exception as e:
        print(f"计算平衡评分失败: {e}")
        return 0