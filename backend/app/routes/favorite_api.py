# backend/app/routes/favorite_api.py
from flask import Blueprint, request, jsonify, session
from app.extensions import db
from app.models.recipe_favorite_model import RecipeFavorite
from app.models.recipe_model import Recipe
from app.models.user_model import User
from sqlalchemy.exc import IntegrityError

favorite_api = Blueprint('favorite_api', __name__)

@favorite_api.route('/api/recipe/favorite', methods=['POST'])
def add_favorite():
    """添加收藏"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        data = request.get_json()
        recipe_id = data.get('recipe_id')
        
        if not recipe_id:
            return jsonify({
                'success': False,
                'message': 'Recipe ID cannot be empty'
            }), 400
        
        # 检查食谱是否存在
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found'
            }), 404
        
        user_id = session['user_id']
        
        # 检查是否已经收藏
        existing_favorite = RecipeFavorite.query.filter_by(
            user_id=user_id,
            recipe_id=recipe_id
        ).first()
        
        if existing_favorite:
            return jsonify({
                'success': False,
                'message': 'Recipe already in favorites'
            }), 400
        
        # 创建收藏记录
        favorite = RecipeFavorite(
            user_id=user_id,
            recipe_id=recipe_id
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        # 获取该食谱的总收藏数
        favorite_count = RecipeFavorite.query.filter_by(recipe_id=recipe_id).count()
        
        return jsonify({
            'success': True,
            'message': 'Recipe added to favorites successfully',
            'data': {
                'is_favorited': True,
                'favorite_count': favorite_count
            }
        })
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to add to favorites, please try again'
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to add to favorites: {str(e)}'
        }), 500

@favorite_api.route('/api/recipe/favorite/<int:recipe_id>', methods=['DELETE'])
def remove_favorite(recipe_id):
    """取消收藏"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        user_id = session['user_id']
        
        # 查找收藏记录
        favorite = RecipeFavorite.query.filter_by(
            user_id=user_id,
            recipe_id=recipe_id
        ).first()
        
        if not favorite:
            return jsonify({
                'success': False,
                'message': 'Favorite record not found'
            }), 404
        
        # 删除收藏记录
        db.session.delete(favorite)
        db.session.commit()
        
        # 获取该食谱的总收藏数
        favorite_count = RecipeFavorite.query.filter_by(recipe_id=recipe_id).count()
        
        return jsonify({
            'success': True,
            'message': 'Recipe removed from favorites successfully',
            'data': {
                'is_favorited': False,
                'favorite_count': favorite_count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to remove from favorites: {str(e)}'
        }), 500

@favorite_api.route('/api/user/favorites', methods=['GET'])
def get_user_favorites():
    """获取用户收藏列表"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        user_id = session['user_id']
        
        # 获取用户收藏的食谱，包含创建者信息
        favorites_query = db.session.query(RecipeFavorite, Recipe, User).join(
            Recipe, RecipeFavorite.recipe_id == Recipe.id
        ).join(
            User, Recipe.user_id == User.id
        ).filter(RecipeFavorite.user_id == user_id).order_by(
            RecipeFavorite.created_at.desc()
        )
        
        favorites_data = []
        for favorite, recipe, author in favorites_query.all():
            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'title': recipe.name,  # 前端期望的字段名
                'description': recipe.description or 'No description available',
                'author_name': author.nickname or author.username,
                'author_id': author.id,
                'favorited_at': favorite.created_at.isoformat() if favorite.created_at else None,
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                'total_calories': getattr(recipe, 'total_calories', 0),
                'total_protein': getattr(recipe, 'total_protein', 0),
                'total_fat': getattr(recipe, 'total_fat', 0),
                'total_carbohydrate': getattr(recipe, 'total_carbohydrate', 0)
            }
            favorites_data.append(recipe_data)
        
        return jsonify({
            'success': True,
            'data': {
                'favorites': favorites_data,
                'count': len(favorites_data)
            }
        })
        
    except Exception as e:
        print(f"获取收藏夹失败: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'message': f'Failed to get favorites list: {str(e)}'
        }), 500

@favorite_api.route('/api/recipe/favorite-status/<int:recipe_id>', methods=['GET'])
def get_favorite_status(recipe_id):
    """检查单个食谱收藏状态"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({
                'success': True,
                'data': {
                    'is_favorited': False,
                    'favorite_count': RecipeFavorite.query.filter_by(recipe_id=recipe_id).count()
                }
            })
        
        user_id = session['user_id']
        
        # 检查是否收藏
        is_favorited = RecipeFavorite.query.filter_by(
            user_id=user_id,
            recipe_id=recipe_id
        ).first() is not None
        
        # 获取总收藏数
        favorite_count = RecipeFavorite.query.filter_by(recipe_id=recipe_id).count()
        
        return jsonify({
            'success': True,
            'data': {
                'is_favorited': is_favorited,
                'favorite_count': favorite_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get favorite status: {str(e)}'
        }), 500