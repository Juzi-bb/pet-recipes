# backend/app/routes/community_api.py
from flask import Blueprint, request, jsonify, session, current_app
from app.extensions import db
from app.models.recipe_model import Recipe, RecipeStatus
from app.models.recipe_like_model import RecipeLike
from app.models.recipe_favorite_model import RecipeFavorite
from app.models.user_model import User
from app.models.pet_model import Pet
from sqlalchemy import func, desc, asc, or_, text
from sqlalchemy.exc import IntegrityError
import math
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

community_api = Blueprint('community_api', __name__)

@community_api.route('/api/community/recipes', methods=['GET'])
def get_community_recipes():
    """获取社区公开食谱列表"""
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        
        # 获取筛选参数
        search = request.args.get('search', '').strip()[:100]  # 限制搜索长度
        sort_by = request.args.get('sort', 'hot')
        author = request.args.get('author', '').strip()[:50]   # 限制作者搜索长度

        # 验证排序参数
        valid_sorts = ['hot', 'newest', 'oldest', 'likes', 'name']
        if sort_by not in valid_sorts:
            sort_by = 'hot'

        # 基础查询：只获取公开的食谱
        query = db.session.query(Recipe).filter(
            Recipe.is_public == True,
            Recipe.status == RecipeStatus.PUBLISHED,
            Recipe.is_active == True
        )
        
        # 搜索过滤
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Recipe.name.like(search_pattern),
                    Recipe.description.like(search_pattern)
                )
            )
        
        # 作者过滤
        if author:
            author_pattern = f'%{author}%'
            query = query.join(User, Recipe.user_id == User.id).filter(
                or_(
                    User.username.like(author_pattern),
                    User.nickname.like(author_pattern)
                )
            )
        
        # 排序处理
        if sort_by == 'hot':
            # 使用预计算的hot_score或简化的热度算法
            query = query.order_by(
                desc(func.coalesce(Recipe.likes_count, 0) +
                     func.coalesce(Recipe.usage_count, 0)),
                desc(Recipe.created_at)
            )
        elif sort_by == 'newest':
            query = query.order_by(desc(Recipe.created_at))
        elif sort_by == 'oldest':
            query = query.order_by(asc(Recipe.created_at))
        elif sort_by == 'likes':
            query = query.order_by(
                desc(func.coalesce(Recipe.likes_count, 0)),
                desc(Recipe.created_at)
            )
        elif sort_by == 'name':
            query = query.order_by(asc(Recipe.name))
        
        # 分页处理
        total = query.count()
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        
        # 确保页码在有效范围内
        page = min(page, total_pages)
        
        recipes = query.offset((page - 1) * per_page).limit(per_page).all()

        # 获取当前用户ID（用于判断点赞和收藏状态）
        current_user_id = session.get('user_id')
        
        # 预加载所有需要的数据以减少数据库查询
        recipe_ids = [recipe.id for recipe in recipes]

        # 批量获取点赞和收藏数据
        likes_data = {}
        favorites_data = {}
        user_likes = set()
        user_favorites = set()
        
        if recipe_ids:
            # 获取点赞数据
            likes_count_query = db.session.query(
                RecipeLike.recipe_id,
                func.count(RecipeLike.id).label('count')
            ).filter(RecipeLike.recipe_id.in_(recipe_ids)).group_by(RecipeLike.recipe_id).all()
            
            likes_data = {row.recipe_id: row.count for row in likes_count_query}
            
            # 获取收藏数据
            favorites_count_query = db.session.query(
                RecipeFavorite.recipe_id,
                func.count(RecipeFavorite.id).label('count')
            ).filter(RecipeFavorite.recipe_id.in_(recipe_ids)).group_by(RecipeFavorite.recipe_id).all()
            
            favorites_data = {row.recipe_id: row.count for row in favorites_count_query}
            
            # 获取当前用户的点赞和收藏状态
            if current_user_id:
                user_likes_query = db.session.query(RecipeLike.recipe_id).filter(
                    RecipeLike.user_id == current_user_id,
                    RecipeLike.recipe_id.in_(recipe_ids)
                ).all()
                user_likes = {row.recipe_id for row in user_likes_query}
                
                user_favorites_query = db.session.query(RecipeFavorite.recipe_id).filter(
                    RecipeFavorite.user_id == current_user_id,
                    RecipeFavorite.recipe_id.in_(recipe_ids)
                ).all()
                user_favorites = {row.recipe_id for row in user_favorites_query}
        
        # 批量获取作者信息
        user_ids = list(set(recipe.user_id for recipe in recipes))
        users_data = {}
        if user_ids:
            users_query = db.session.query(User).filter(User.id.in_(user_ids)).all()
            users_data = {user.id: user for user in users_query}

        # 构建返回数据
        recipes_data = []
        for recipe in recipes:
            author_info = users_data.get(recipe.user_id)
            
            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'description': recipe.description or '',
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                'author': {
                    'id': author_info.id if author_info else None,
                    'username': author_info.username if author_info else 'Unknown',
                    'nickname': author_info.nickname if author_info else 'Unknown User'
                },
                'stats': {
                    'likes_count': likes_data.get(recipe.id, 0),
                    'favorites_count': favorites_data.get(recipe.id, 0),
                    'usage_count': recipe.usage_count or 0,
                    'is_loved': recipe.id in user_likes,
                    'is_favorited': recipe.id in user_favorites
                },
                'nutrition': {
                    'calories': round(recipe.total_calories or 0, 1),
                    'protein': round(recipe.total_protein or 0, 1),
                    'fat': round(recipe.total_fat or 0, 1),
                    'carbohydrate': round(recipe.total_carbohydrate or 0, 1)
                },
                'scores': {
                    'nutrition_score': recipe.nutrition_score,
                    'balance_score': recipe.balance_score
                },
                'suitability': {
                    'dogs': recipe.suitable_for_dogs,
                    'cats': recipe.suitable_for_cats,
                    'puppies': recipe.suitable_for_puppies,
                    'kittens': recipe.suitable_for_kittens,
                    'seniors': recipe.suitable_for_seniors
                }
            }
            
            recipes_data.append(recipe_data)
        
        return jsonify({
            'success': True,
            'data': {
                'recipes': recipes_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_prev': page > 1,
                    'has_next': page < total_pages
                },
                'filters': {
                    'search': search,
                    'sort': sort_by,
                    'author': author
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取社区食谱失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Failed to load community recipes. Please try again later.',
            'debug': str(e) if current_app.debug else None
        }), 500
    
@community_api.route('/api/community/recipe/<int:recipe_id>/like', methods=['POST'])
def like_recipe(recipe_id):
    """点赞食谱"""
    try:
        # 验证输入
        if recipe_id <= 0:
            return jsonify({
                'success': False,
                'message': 'Invalid recipe ID'
            }), 400
        
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        user_id = session['user_id']
        
        # 使用事务确保数据一致性
        try:
            with db.session.begin():
                # 检查食谱是否存在
                recipe = Recipe.query.get(recipe_id)
                if not recipe:
                    return jsonify({
                        'success': False,
                        'message': 'Recipe not found'
                    }), 404
                
                # 检查是否已经点赞
                existing_like = RecipeLike.query.filter_by(
                    user_id=user_id,
                    recipe_id=recipe_id
                ).first()
                
                if existing_like:
                    return jsonify({
                        'success': False,
                        'message': 'Already liked this recipe'
                    }), 400
                
                # 创建点赞记录
                like = RecipeLike(
                    user_id=user_id,
                    recipe_id=recipe_id
                )
                
                db.session.add(like)
                
                # 更新食谱的点赞计数缓存
                recipe.likes_count = RecipeLike.query.filter_by(recipe_id=recipe_id).count() + 1
        
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'Already liked this recipe'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Recipe liked successfully',
            'data': {
                'is_loved': True,
                'likes_count': recipe.likes_count
            }
        })
        
    except Exception as e:
        logger.error(f"点赞食谱失败: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to like recipe, please try again'
        }), 500

@community_api.route('/api/community/recipe/<int:recipe_id>/unlike', methods=['DELETE'])
def unlike_recipe(recipe_id):
    """取消点赞食谱"""
    try:
        # 验证输入
        if recipe_id <= 0:
            return jsonify({
                'success': False,
                'message': 'Invalid recipe ID'
            }), 400
        
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        user_id = session['user_id']
        
        # 使用事务确保数据一致性
        with db.session.begin():
            # 查找点赞记录
            like = RecipeLike.query.filter_by(
                user_id=user_id,
                recipe_id=recipe_id
            ).first()
            
            if not like:
                return jsonify({
                    'success': False,
                    'message': 'Like record not found'
                }), 404
            
            # 删除点赞记录
            db.session.delete(like)
            
            # 更新食谱的点赞计数缓存
            recipe = Recipe.query.get(recipe_id)
            if recipe:
                recipe.likes_count = max(0, RecipeLike.query.filter_by(recipe_id=recipe_id).count() - 1)
        
        return jsonify({
            'success': True,
            'message': 'Recipe unliked successfully',
            'data': {
                'is_loved': False,
                'likes_count': recipe.likes_count if recipe else 0
            }
        })
        
    except Exception as e:
        logger.error(f"取消点赞食谱失败: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to unlike recipe, please try again'
        }), 500

@community_api.route('/api/community/stats', methods=['GET'])
def get_community_stats():
    """获取社区统计信息"""
    try:
        # 使用原生SQL提高性能
        stats_query = db.session.execute(text('''
            SELECT 
                (SELECT COUNT(*) FROM recipes WHERE is_public = 1 AND status = 'published' AND is_active = 1) as total_recipes,
                (SELECT COUNT(DISTINCT user_id) FROM recipes WHERE is_public = 1 AND status = 'published' AND is_active = 1) as active_users,
                (SELECT COUNT(*) FROM recipe_likes) as total_likes,
                (SELECT COUNT(*) FROM recipe_favorites) as total_favorites
        ''')).fetchone()
        
        return jsonify({
            'success': True,
            'data': {
                'total_recipes': stats_query[0] or 0,
                'active_users': stats_query[1] or 0,
                'total_likes': stats_query[2] or 0,
                'total_favorites': stats_query[3] or 0
            }
        })
        
    except Exception as e:
        logger.error(f"获取社区统计失败: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to load community stats',
            'data': {
                'total_recipes': 0,
                'active_users': 0,
                'total_likes': 0,
                'total_favorites': 0
            }
        })

@community_api.route('/api/community/trending', methods=['GET'])
def get_trending_recipes():
    """获取热门食谱（首页推荐）"""
    try:
        limit = min(20, max(1, int(request.args.get('limit', 6))))  # 限制范围1-20
        
        # 简化热度计算，提高性能
        trending_recipes = db.session.query(Recipe)\
            .filter(
                Recipe.is_public == True,
                Recipe.status == RecipeStatus.PUBLISHED,
                Recipe.is_active == True
            )\
            .order_by(
                desc(func.coalesce(Recipe.likes_count, 0) + 
                     func.coalesce(Recipe.usage_count, 0)),
                desc(Recipe.created_at)
            )\
            .limit(limit).all()
        
        # 获取作者信息
        user_ids = [recipe.user_id for recipe in trending_recipes]
        users_query = db.session.query(User).filter(User.id.in_(user_ids)).all()
        users_data = {user.id: user for user in users_query}
        
        # 获取统计数据
        recipe_ids = [recipe.id for recipe in trending_recipes]
        likes_data = {}
        favorites_data = {}
        
        if recipe_ids:
            likes_count_query = db.session.query(
                RecipeLike.recipe_id,
                func.count(RecipeLike.id).label('count')
            ).filter(RecipeLike.recipe_id.in_(recipe_ids)).group_by(RecipeLike.recipe_id).all()
            likes_data = {row.recipe_id: row.count for row in likes_count_query}
            
            favorites_count_query = db.session.query(
                RecipeFavorite.recipe_id,
                func.count(RecipeFavorite.id).label('count')
            ).filter(RecipeFavorite.recipe_id.in_(recipe_ids)).group_by(RecipeFavorite.recipe_id).all()
            favorites_data = {row.recipe_id: row.count for row in favorites_count_query}
        
        # 构建返回数据
        trending_data = []
        for recipe in trending_recipes:
            author_info = users_data.get(recipe.user_id)
            
            trending_data.append({
                'id': recipe.id,
                'name': recipe.name,
                'description': recipe.description or '',
                'author': {
                    'username': author_info.username if author_info else 'Unknown',
                    'nickname': author_info.nickname if author_info else 'Unknown User'
                },
                'stats': {
                    'likes_count': likes_data.get(recipe.id, 0),
                    'favorites_count': favorites_data.get(recipe.id, 0),
                    'usage_count': recipe.usage_count or 0
                },
                'nutrition': {
                    'calories': round(recipe.total_calories or 0, 1),
                    'protein': round(recipe.total_protein or 0, 1),
                    'fat': round(recipe.total_fat or 0, 1)
                },
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'trending_recipes': trending_data
            }
        })
        
    except Exception as e:
        logger.error(f"获取热门食谱失败: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to load trending recipes',
            'data': {
                'trending_recipes': []
            }
        })