"""
过敏食材管理API路由
"""

from flask import Blueprint, request, jsonify, session
from app.models.pet_model import Pet
from app.models.ingredient_model import Ingredient
from app.utils.allergen_service import AllergenService
from datetime import datetime

allergen_api_bp = Blueprint('allergen_api', __name__)

@allergen_api_bp.route('/api/pet/<int:pet_id>/allergens', methods=['GET'])
def get_pet_allergens(pet_id):
    """获取宠物的过敏食材列表"""
    try:
        # 验证权限
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
        if not pet:
            return jsonify({'error': '宠物信息不存在'}), 404
        
        # 获取过敏食材
        allergens = AllergenService.get_pet_allergens(pet_id)
        
        # 获取统计信息
        stats = AllergenService.get_allergen_statistics(pet_id)
        
        return jsonify({
            'success': True,
            'allergens': allergens,
            'statistics': stats
        })
        
    except Exception as e:
        print(f"获取宠物过敏食材失败: {e}")
        return jsonify({'error': '获取过敏食材失败'}), 500

@allergen_api_bp.route('/api/pet/<int:pet_id>/allergens', methods=['POST'])
def add_pet_allergen(pet_id):
    """为宠物添加过敏食材"""
    try:
        # 验证权限
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
        if not pet:
            return jsonify({'error': '宠物信息不存在'}), 404
        
        data = request.get_json()
        ingredient_id = data.get('ingredient_id')
        severity = data.get('severity', 'mild')
        notes = data.get('notes', '')
        confirmed_date_str = data.get('confirmed_date')
        
        if not ingredient_id:
            return jsonify({'error': '请选择食材'}), 400
        
        # 验证食材存在
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            return jsonify({'error': '食材不存在'}), 404
        
        # 解析确认日期
        confirmed_date = None
        if confirmed_date_str:
            try:
                confirmed_date = datetime.fromisoformat(confirmed_date_str.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # 添加过敏食材
        success = AllergenService.add_pet_allergen(
            pet_id=pet_id,
            ingredient_id=ingredient_id,
            severity=severity,
            notes=notes,
            confirmed_date=confirmed_date
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'已添加过敏食材: {ingredient.name}'
            })
        else:
            return jsonify({'error': '添加过敏食材失败'}), 500
            
    except Exception as e:
        print(f"添加过敏食材失败: {e}")
        return jsonify({'error': '添加过敏食材失败'}), 500

@allergen_api_bp.route('/api/pet/<int:pet_id>/allergens/<int:ingredient_id>', methods=['DELETE'])
def remove_pet_allergen(pet_id, ingredient_id):
    """移除宠物的过敏食材"""
    try:
        # 验证权限
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
        if not pet:
            return jsonify({'error': '宠物信息不存在'}), 404
        
        # 移除过敏食材
        success = AllergenService.remove_pet_allergen(pet_id, ingredient_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '过敏食材已移除'
            })
        else:
            return jsonify({'error': '过敏食材不存在'}), 404
            
    except Exception as e:
        print(f"移除过敏食材失败: {e}")
        return jsonify({'error': '移除过敏食材失败'}), 500

@allergen_api_bp.route('/api/common-allergens')
def get_common_allergens():
    """获取常见过敏食材"""
    try:
        allergens_by_category = AllergenService.get_common_allergens_by_category()
        
        return jsonify({
            'success': True,
            'allergens_by_category': allergens_by_category
        })
        
    except Exception as e:
        print(f"获取常见过敏食材失败: {e}")
        return jsonify({'error': '获取常见过敏食材失败'}), 500

@allergen_api_bp.route('/api/check-recipe-safety', methods=['POST'])
def check_recipe_safety():
    """检查食谱对宠物的安全性"""
    try:
        data = request.get_json()
        ingredient_ids = data.get('ingredient_ids', [])
        pet_id = data.get('pet_id')
        
        if not ingredient_ids:
            return jsonify({'error': '请提供食材列表'}), 400
        
        # 验证宠物权限
        if pet_id and session.get('user_id'):
            pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
            if not pet:
                return jsonify({'error': '宠物信息不存在'}), 404
        
        # 检查安全性
        safety_check = AllergenService.check_recipe_safety(ingredient_ids, pet_id)
        
        return jsonify({
            'success': True,
            'safety_check': safety_check
        })
        
    except Exception as e:
        print(f"检查食谱安全性失败: {e}")
        return jsonify({'error': '检查安全性失败'}), 500