from flask import Blueprint, request, jsonify, session
from werkzeug.exceptions import BadRequest
from app.extensions import db
from app.models.recipe_model import Recipe
from app.models.user_model import User
from app.models.ingredient_model import Ingredient
from app.models.recipe_ingredient_model import RecipeIngredient
from app.models.recipe_like_model import RecipeLike
from app.models.recipe_favorite_model import RecipeFavorite
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
        
        # 检查权限：只有公开食谱或自己的食谱可以查看
        if not recipe.is_public and recipe.user_id != current_user_id:
            return jsonify({'success': False, 'message': '没有权限查看此食谱'}), 403
        
        # 获取食谱作者信息
        author = User.query.get(recipe.user_id)
        author_info = {
            'id': author.id if author else None,
            'username': author.username if author else 'Unknown',
            'nickname': author.nickname if author else 'Unknown User'
        }

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
        
        # 【新增】获取点赞和收藏统计及当前用户状态
        try:
            # 获取点赞数量
            likes_count = RecipeLike.query.filter_by(recipe_id=recipe_id).count()
            
            # 获取收藏数量
            favorites_count = RecipeFavorite.query.filter_by(recipe_id=recipe_id).count()
            
            # 检查当前用户是否已点赞
            user_liked = RecipeLike.query.filter_by(
                user_id=current_user_id,
                recipe_id=recipe_id
            ).first() is not None
            
            # 检查当前用户是否已收藏
            user_favorited = RecipeFavorite.query.filter_by(
                user_id=current_user_id,
                recipe_id=recipe_id
            ).first() is not None
            
        except Exception as stats_error:
            print(f"⚠️ 获取统计信息出错: {stats_error}")
            likes_count = 0
            favorites_count = 0
            user_liked = False
            user_favorited = False
        
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
            'nutrition': nutrition,
            # 【新增】点赞收藏信息
            'stats': {
                'likes_count': likes_count,
                'favorites_count': favorites_count,
                'usage_count': recipe.usage_count or 0,
                'is_loved': user_liked,
                'is_favorited': user_favorited
            },
            'permissions': {
                'can_edit': recipe.user_id == current_user_id,
                'can_delete': recipe.user_id == current_user_id,
                'can_interact': True  # 登录用户都可以点赞收藏
            }
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
        
        # 使用模型查询替代原生SQL
        try:
            # 获取收藏数量
            favorites_count = RecipeFavorite.query.filter_by(user_id=user_id).count()
            
            # 获取收藏的食谱列表
            favorites_query = db.session.query(RecipeFavorite, Recipe).join(
                Recipe, RecipeFavorite.recipe_id == Recipe.id
            ).filter(RecipeFavorite.user_id == user_id).order_by(
                RecipeFavorite.created_at.desc()
            ).all()
            
        except Exception as query_error:
            print(f"⚠️ 查询收藏信息出错: {query_error}")
            favorites_count = 0
            favorites_query = []
        
        favorites_data = []
        for favorite, recipe in favorites_query:
            favorites_data.append({
                'id': recipe.id,
                'name': recipe.name,
                'description': recipe.description or '',
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                'favorited_at': favorite.created_at.isoformat() if favorite.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'count': favorites_count,
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
        existing_favorite = RecipeFavorite.query.filter_by(
            user_id=user_id, 
            recipe_id=recipe_id
        ).first()
        
        if existing_favorite:
            return jsonify({'success': False, 'message': '已经收藏过此食谱'}), 400
        
        # 添加收藏
        favorite = RecipeFavorite(user_id=user_id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()
        
        # 获取新的收藏数量
        new_count = RecipeFavorite.query.filter_by(recipe_id=recipe_id).count()
        
        return jsonify({
            'success': True, 
            'message': '收藏成功',
            'data': {
                'is_favorited': True,
                'favorites_count': new_count
            }
        })
        
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
        
        # 查找收藏记录
        favorite = RecipeFavorite.query.filter_by(
            user_id=user_id, 
            recipe_id=recipe_id
        ).first()
        
        if not favorite:
            return jsonify({'success': False, 'message': '未收藏此食谱'}), 404
        
        # 移除收藏
        db.session.delete(favorite)
        db.session.commit()
        
        # 获取新的收藏数量
        new_count = RecipeFavorite.query.filter_by(recipe_id=recipe_id).count()
        
        return jsonify({
            'success': True, 
            'message': '取消收藏成功',
            'data': {
                'is_favorited': False,
                'favorites_count': new_count
            }
        })
        
    except Exception as e:
        print(f"❌ 取消收藏出错: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}'
        }), 500