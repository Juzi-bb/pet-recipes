from flask import Blueprint, request, jsonify, session
from werkzeug.exceptions import BadRequest
from app.extensions import db
from app.models.recipe_model import Recipe
from app.models.user_model import User
from app.models.ingredient_model import Ingredient
from app.models.recipe_ingredient_model import RecipeIngredient
from sqlalchemy import text
import logging

recipe_detail_bp = Blueprint('recipe_detail', __name__)

@recipe_detail_bp.route('/api/recipe/<int:recipe_id>/detail', methods=['GET'])
def get_recipe_detail(recipe_id):
    """获取食谱详情"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        current_user_id = session['user_id']
        
        # 获取食谱基本信息
        recipe = Recipe.query.get(recipe_id)
        
        if not recipe:
            return jsonify({'success': False, 'message': '食谱不存在'}), 404
        
        # 获取食谱食材信息
        try:
            recipe_ingredients = db.session.query(
                RecipeIngredient.weight,
                Ingredient.name
            ).join(
                Ingredient, RecipeIngredient.ingredient_id == Ingredient.id
            ).filter(
                RecipeIngredient.recipe_id == recipe_id
            ).order_by(Ingredient.name).all()
        except Exception as ingredients_error:
            print(f"⚠️ 获取食材信息出错: {ingredients_error}")
            recipe_ingredients = []
        
        # 构建食材列表
        ingredients_list = []
        for weight, name in recipe_ingredients:
            ingredients_list.append({
                'name': name,
                'weight': weight
            })
        
        # 计算营养信息（使用Recipe模型中的方法）
        nutrition = {
            'total_calories': float(recipe.total_calories or 0),
            'total_protein': float(recipe.total_protein or 0),
            'total_fat': float(recipe.total_fat or 0),
            'total_carbs': float(recipe.total_carbohydrate or 0),
            'total_fiber': float(recipe.total_fiber or 0),
            'total_calcium': float(recipe.total_calcium or 0)
        }
        
        # 获取宠物名称（如果有关联）
        pet_name = None
        if recipe.pet_id:
            try:
                from app.models.pet_model import Pet
                pet = Pet.query.get(recipe.pet_id)
                if pet:
                    pet_name = pet.name
            except Exception as pet_error:
                print(f"⚠️ 获取宠物信息出错: {pet_error}")
        
        
        # 构建返回数据
        recipe_data = {
            'id': recipe.id,
            'name': recipe.name,
            'description': recipe.description,
            'user_id': recipe.user_id,
            'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
            'status': recipe.status.value if recipe.status else 'draft',
            'pet_name': pet_name,
            'ingredients': ingredients_list,
            'nutrition': nutrition
        }
        
        return jsonify({
            'success': True,
            'recipe': recipe_data,
            'current_user_id': current_user_id
        })
        
    except Exception as e:
        print(f"❌ 获取食谱详情出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@recipe_detail_bp.route('/api/user/favorites', methods=['GET'])
def get_user_favorites():
    """获取用户收藏夹信息"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user_id = session['user_id']
        
        # 获取收藏数量
        try:
            favorites_count = db.session.execute(
                text('SELECT COUNT(*) FROM user_recipe_favorites WHERE user_id = :user_id'),
                {'user_id': user_id}
            ).scalar()
        except Exception as count_error:
            print(f"⚠️ 获取收藏数量出错: {count_error}")
            favorites_count = 0
        
        # 获取收藏的食谱列表
        try:
            favorites_query = db.session.execute(
                text('''
                    SELECT r.id, r.name, r.description, r.created_at, f.created_at as favorited_at
                    FROM user_recipe_favorites f
                    JOIN recipes r ON f.recipe_id = r.id
                    WHERE f.user_id = :user_id
                    ORDER BY f.created_at DESC
                '''),
                {'user_id': user_id}
            ).fetchall()
        except Exception as list_error:
            print(f"⚠️ 获取收藏列表出错: {list_error}")
            favorites_query = []
        
        favorites_data = []
        for fav in favorites_query:
            favorites_data.append({
                'id': fav[0],
                'name': fav[1],
                'description': fav[2],
                'created_at': fav[3],
                'favorited_at': fav[4]
            })
        
        return jsonify({
            'success': True,
            'data': {
                'count': favorites_count or 0,
                'favorites': favorites_data
            }
        })
        
    except Exception as e:
        print(f"❌ 获取用户收藏夹出错: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@recipe_detail_bp.route('/api/recipe/favorite', methods=['POST'])
def add_recipe_favorite():
    """添加食谱到收藏夹"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user_id = session['user_id']
        data = request.get_json()
        
        if not data or 'recipe_id' not in data:
            return jsonify({'success': False, 'message': '缺少食谱ID'}), 400
        
        recipe_id = data['recipe_id']
        
        # 检查食谱是否存在
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': '食谱不存在'}), 404
        
        # 检查是否已经收藏
        existing_count = db.session.execute(
            text('SELECT COUNT(*) FROM user_recipe_favorites WHERE user_id = :user_id AND recipe_id = :recipe_id'),
            {'user_id': user_id, 'recipe_id': recipe_id}
        ).scalar()
        
        if existing_count > 0:
            return jsonify({'success': False, 'message': '已经收藏过此食谱'}), 400
        
        # 添加收藏
        db.session.execute(
            text('INSERT INTO user_recipe_favorites (user_id, recipe_id, created_at) VALUES (:user_id, :recipe_id, datetime("now"))'),
            {'user_id': user_id, 'recipe_id': recipe_id}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': '收藏成功'})
        
    except Exception as e:
        print(f"❌ 添加收藏出错: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}'
        }), 500


@recipe_detail_bp.route('/api/recipe/favorite/<int:recipe_id>', methods=['DELETE'])
def remove_recipe_favorite(recipe_id):
    """从收藏夹移除食谱"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user_id = session['user_id']
        
        # 检查是否已收藏
        existing_count = db.session.execute(
            text('SELECT COUNT(*) FROM user_recipe_favorites WHERE user_id = :user_id AND recipe_id = :recipe_id'),
            {'user_id': user_id, 'recipe_id': recipe_id}
        ).scalar()
        
        if existing_count == 0:
            return jsonify({'success': False, 'message': '未收藏此食谱'}), 404
        
        # 移除收藏
        db.session.execute(
            text('DELETE FROM user_recipe_favorites WHERE user_id = :user_id AND recipe_id = :recipe_id'),
            {'user_id': user_id, 'recipe_id': recipe_id}
        )
        db.session.commit()
        
        return jsonify({'success': True, 'message': '取消收藏成功'})
        
    except Exception as e:
        print(f"❌ 取消收藏出错: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}'
        }), 500