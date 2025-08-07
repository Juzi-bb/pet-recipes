"""
食材百科API路由
提供食材查询、分类浏览、详情查看等功能
"""

from flask import Blueprint, request, jsonify, session
from app.models.ingredient_model import Ingredient, IngredientCategory
from app.extensions import db
from sqlalchemy import or_, and_, func
import traceback

ingredient_encyclopedia_bp = Blueprint('ingredient_encyclopedia', __name__)

def get_category_icon(category_value):
    """获取分类图标"""
    icons = {
        'red_meat': 'fas fa-drumstick-bite',
        'white_meat': 'fas fa-egg',
        'fish': 'fas fa-fish',
        'organs': 'fas fa-heart',
        'vegetables': 'fas fa-carrot',
        'fruits': 'fas fa-apple-alt',
        'grains': 'fas fa-seedling',
        'dairy': 'fas fa-cheese',
        'supplements': 'fas fa-pills',
        'dangerous': 'fas fa-exclamation-triangle'  # 危险食材图标
    }
    return icons.get(category_value, 'fas fa-utensils')

@ingredient_encyclopedia_bp.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """获取食材列表 - 支持分类筛选和搜索"""
    try:
        # 获取查询参数
        category = request.args.get('category', 'all')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        safe_for = request.args.get('safe_for', 'all')  # all, dogs, cats
        exclude_dangerous = request.args.get('exclude_dangerous', 'false').lower() == 'true'
        
        # 构建基础查询
        query = Ingredient.query.filter_by(is_active=True)

        # 排除危险食材（用于创建食谱）
        if exclude_dangerous:
            query = query.filter(Ingredient.category != IngredientCategory.DANGEROUS)
        
        # 分类筛选 - 修复分类名称映射
        if category != 'all':
            # 创建分类名称到枚举值的映射
            category_mapping = {
                'Red Meat': 'red_meat',
                'White Meat': 'white_meat', 
                'Fish': 'fish',
                'Organs': 'organs',
                'Vegetables': 'vegetables',
                'Fruits': 'fruits',
                'Grains': 'grains',
                'Dairy': 'dairy',
                'Supplements': 'supplements',
                'Dangerous Foods': 'dangerous'
            }
            
            # 如果传入的是显示名称，转换为枚举值
            if category in category_mapping:
                category_value = category_mapping[category]
            else:
                category_value = category.lower().replace(' ', '_')
            
            print(f"转换后的分类值: '{category_value}'")  # 调试日志
            
            try:
                category_enum = IngredientCategory(category_value)
                query = query.filter_by(category=category_enum)
                print(f"成功设置分类筛选: {category_enum}")  # 调试日志
            except ValueError as ve:
                print(f"无效的分类值: {category_value}, 错误: {ve}")
                return jsonify({'error': f'Invalid category: {category}'}), 400
        
        # 安全性筛选
        if safe_for == 'dogs':
            query = query.filter_by(is_safe_for_dogs=True)
        elif safe_for == 'cats':
            query = query.filter_by(is_safe_for_cats=True)
        
        # 搜索筛选
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                or_(
                    Ingredient.name.ilike(search_term),
                    Ingredient.name_en.ilike(search_term),
                    Ingredient.description.ilike(search_term)
                )
            )
        
        # 排序
        query = query.order_by(Ingredient.name)
        
        # 分页
        if per_page > 0:
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            ingredients = pagination.items
            total = pagination.total
            has_next = pagination.has_next
            has_prev = pagination.has_prev
        else:
            ingredients = query.all()
            total = len(ingredients)
            has_next = False
            has_prev = False
        
        # 转换为字典格式
        ingredients_data = []
        for ingredient in ingredients:
            # 获取基础数据
            ingredient_dict = ingredient.to_dict()
            
            # 展平营养数据到顶层（保持与详情页一致）
            nutrition = ingredient_dict.get('nutrition', {})
            basic_nutrition = nutrition.get('basic', {})
            minerals = nutrition.get('minerals', {})
            vitamins = nutrition.get('vitamins', {})

            # 获取food_guide信息
            food_guide = ingredient_dict.get('food_guide', {})
            
            # 获取safety信息
            safety = ingredient_dict.get('safety', {})
            
            ingredient_data = {
                'id': ingredient_dict['id'],
                'name': ingredient_dict['name'],
                'name_en': ingredient_dict['name_en'],
                'category': ingredient_dict['category'],
                'image_filename': ingredient_dict['image_filename'],
                'description': ingredient_dict['description'],
                'seasonality': ingredient_dict['seasonality'],
                'benefits': food_guide.get('benefits'),  # 从food_guide中获取
                # 展平的营养数据
                'calories': basic_nutrition.get('calories', 0),
                'protein': basic_nutrition.get('protein', 0),
                'fat': basic_nutrition.get('fat', 0),
                'carbohydrate': basic_nutrition.get('carbohydrate', 0),
                'fiber': basic_nutrition.get('fiber', 0),
                'calcium': minerals.get('calcium', 0),
                'phosphorus': minerals.get('phosphorus', 0),
                'potassium': minerals.get('potassium', 0),
                'sodium': minerals.get('sodium', 0),
                'vitamin_a': vitamins.get('vitamin_a', 0),
                'vitamin_c': vitamins.get('vitamin_c', 0),
                'vitamin_e': vitamins.get('vitamin_e', 0),
                'vitamin_k': vitamins.get('vitamin_k', 0),
                # 安全性信息
                'is_safe_for_dogs': safety.get('is_safe_for_dogs', True),
                'is_safe_for_cats': safety.get('is_safe_for_cats', True),
                'is_common_allergen': safety.get('is_common_allergen', False)
            }
            ingredients_data.append(ingredient_data)
        
        return jsonify({
            'success': True,
            'ingredients': ingredients_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'has_next': has_next,
                'has_prev': has_prev,
                'pages': (total + per_page - 1) // per_page if per_page > 0 else 1
            }
        })
        
    except Exception as e:
        print(f"❌ Failed to get ingredients list: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to get ingredients list: {str(e)}'}), 500

@ingredient_encyclopedia_bp.route('/api/ingredients/<int:ingredient_id>', methods=['GET'])
def get_ingredient_detail(ingredient_id):
    """获取食材详细信息"""
    try:
        ingredient = Ingredient.query.filter_by(id=ingredient_id, is_active=True).first()
        
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        # 获取完整的营养信息
        ingredient_data = ingredient.to_dict()

        # 将嵌套的营养数据展平到顶层，供前端使用
        nutrition = ingredient_data.get('nutrition', {})
        food_guide = ingredient_data.get('food_guide', {})
        safety = ingredient_data.get('safety', {})

        # 基础营养成分
        basic_nutrition = nutrition.get('basic', {})
        ingredient_data.update({
            'calories': basic_nutrition.get('calories', 0),
            'protein': basic_nutrition.get('protein', 0),
            'fat': basic_nutrition.get('fat', 0),
            'carbohydrate': basic_nutrition.get('carbohydrate', 0),
            'fiber': basic_nutrition.get('fiber', 0)
        })
        
        # 矿物质
        minerals = nutrition.get('minerals', {})
        ingredient_data.update({
            'calcium': minerals.get('calcium', 0),
            'phosphorus': minerals.get('phosphorus', 0),
            'potassium': minerals.get('potassium', 0),
            'sodium': minerals.get('sodium', 0),
            'iron': minerals.get('iron', 0),
            'zinc': minerals.get('zinc', 0),
            'magnesium': minerals.get('magnesium', 0),
            'copper': minerals.get('copper', 0),
            'manganese': minerals.get('manganese', 0),
            'selenium': minerals.get('selenium', 0)
        })
        
        # 维生素
        vitamins = nutrition.get('vitamins', {})
        ingredient_data.update({
            'vitamin_a': vitamins.get('vitamin_a', 0),
            'vitamin_d': vitamins.get('vitamin_d', 0),
            'vitamin_e': vitamins.get('vitamin_e', 0),
            'vitamin_k': vitamins.get('vitamin_k', 0),
            'vitamin_c': vitamins.get('vitamin_c', 0),  # 如果没有vitamin_c，默认为0
            'thiamine': vitamins.get('thiamine', 0),
            'riboflavin': vitamins.get('riboflavin', 0),
            'niacin': vitamins.get('niacin', 0),
            'vitamin_b12': vitamins.get('vitamin_b12', 0)
        })

        # 将food_guide和safety信息也展平到顶层
        ingredient_data.update({
            'benefits': food_guide.get('benefits'),
            'is_safe_for_dogs': safety.get('is_safe_for_dogs', True),
            'is_safe_for_cats': safety.get('is_safe_for_cats', True),
            'is_common_allergen': safety.get('is_common_allergen', False)
        })
        
        # 添加食材百科特有的信息
        food_guide = ingredient_data.get('food_guide', {})
        ingredient_data['encyclopedia_info'] = {
            'preparation_method': food_guide.get('preparation_method'),
            'pro_tip': food_guide.get('pro_tip'),
            'allergy_alert': food_guide.get('allergy_alert'),
            'storage_notes': food_guide.get('storage_notes'),
            'data_source': ingredient_data.get('data_source'),
            'last_verified': ingredient_data.get('last_verified')
        }
        
        # 获取推荐搭配（相同分类的其他食材）
        recommended_ingredients = Ingredient.query.filter(
            and_(
                Ingredient.category == ingredient.category,
                Ingredient.id != ingredient.id,
                Ingredient.is_active == True
            )
        ).limit(6).all()
        
        recommended_data = []
        for rec_ingredient in recommended_ingredients:
            recommended_data.append({
                'id': rec_ingredient.id,
                'name': rec_ingredient.name,
                'image_filename': rec_ingredient.image_filename,
                'calories': rec_ingredient.calories,
                'protein': rec_ingredient.protein
            })
        
        ingredient_data['recommended_ingredients'] = recommended_data
        
        return jsonify({
            'success': True,
            'ingredient': ingredient_data
        })
        
    except Exception as e:
        print(f"❌ Failed to get ingredient details: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to get ingredient details: {str(e)}'}), 500

@ingredient_encyclopedia_bp.route('/api/ingredients/categories', methods=['GET'])
def get_categories():
    """获取食材分类列表及每个分类的食材数量"""
    try:
        # 新增参数：是否排除危险食材
        exclude_dangerous = request.args.get('exclude_dangerous', 'false').lower() == 'true'

        # 定义分类名称映射 - 修改为英文
        category_names = {
            'red_meat': 'Red Meat',
            'white_meat': 'White Meat',
            'fish': 'Fish',
            'organs': 'Organs',
            'vegetables': 'Vegetables',
            'fruits': 'Fruits',
            'grains': 'Grains',
            'dairy': 'Dairy',
            'supplements': 'Supplements',
            'dangerous': 'Dangerous Foods'  # 新添加危险食材分类
        }

        # 定义自定义排序顺序
        if exclude_dangerous:
            # 创建食谱时的分类顺序（排除危险食材）
            custom_order = [
                'red_meat', 'white_meat', 'fish', 'organs',
                'vegetables', 'fruits', 'grains', 'dairy', 'supplements'
            ]
        else:
            # 食材百科的分类顺序（包含危险食材）
            custom_order = [
                'red_meat', 'white_meat', 'fish', 'organs',
                'vegetables', 'fruits', 'grains', 'dairy',
                'supplements', 'dangerous'
            ]
        
        # 构建查询条件
        if exclude_dangerous:
            # 排除危险食材分类
            category_counts = db.session.query(
                Ingredient.category,
                func.count(Ingredient.id).label('count')
            ).filter(
                and_(
                    Ingredient.is_active == True,
                    Ingredient.category != IngredientCategory.DANGEROUS
                )
            ).group_by(Ingredient.category).all()
        else:
            # 包含所有分类
            category_counts = db.session.query(
                Ingredient.category,
                func.count(Ingredient.id).label('count')
            ).filter_by(is_active=True).group_by(Ingredient.category).all()
        
        # 转换为字典以便查找
        count_dict = {category.value: count for category, count in category_counts}
        
        # 按自定义顺序构建分类数据
        categories_data = []
        for category_id in custom_order:
            if category_id in count_dict:  # 只添加数据库中存在的分类
                categories_data.append({
                    'id': category_id,
                    'value': category_id,
                    'name': category_names.get(category_id, category_id),
                    'count': count_dict[category_id],
                    'icon': get_category_icon(category_id)
                })
        
        # 统计各分类的食材数量
        category_counts = db.session.query(
            Ingredient.category,
            func.count(Ingredient.id).label('count')
        ).filter_by(is_active=True).group_by(Ingredient.category).all()
        
        # 添加任何不在自定义顺序中但存在于数据库中的分类
        for category, count in category_counts:
            if category.value not in custom_order:
                categories_data.append({
                    'id': category.value,
                    'value': category.value,
                    'name': category_names.get(category.value, category.value),
                    'count': count,
                    'icon': get_category_icon(category.value)
                })
        
        return jsonify({
            'success': True,
            'categories': categories_data,
            'total_ingredients': sum(item['count'] for item in categories_data)
        })
        
    except Exception as e:
        print(f"❌ Failed to get category information: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to get category information: {str(e)}'}), 500

@ingredient_encyclopedia_bp.route('/api/ingredients/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """获取搜索建议"""
    try:
        query_term = request.args.get('q', '').strip()
        
        if len(query_term) < 2:
            return jsonify({'suggestions': []})
        
        # 搜索食材名称
        suggestions = Ingredient.query.filter(
            and_(
                or_(
                    Ingredient.name.ilike(f'%{query_term}%'),
                    Ingredient.name_en.ilike(f'%{query_term}%')
                ),
                Ingredient.is_active == True
            )
        ).limit(10).all()
        
        suggestions_data = []
        for ingredient in suggestions:
            suggestions_data.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'name_en': ingredient.name_en,
                'category': ingredient.category.value,
                'image_filename': ingredient.image_filename
            })
        
        return jsonify({
            'success': True,
            'suggestions': suggestions_data
        })
        
    except Exception as e:
        print(f"❌ Failed to get search suggestions: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to get search suggestions: {str(e)}'}), 500

@ingredient_encyclopedia_bp.route('/api/ingredients/stats', methods=['GET'])
def get_ingredient_stats():
    """获取食材统计信息"""
    try:
        # 总体统计
        total_ingredients = Ingredient.query.filter_by(is_active=True).count()
        safe_for_dogs = Ingredient.query.filter_by(is_active=True, is_safe_for_dogs=True).count()
        safe_for_cats = Ingredient.query.filter_by(is_active=True, is_safe_for_cats=True).count()
        common_allergens = Ingredient.query.filter_by(is_active=True, is_common_allergen=True).count()
        
        # 按季节统计 - 保持中文季节名称，因为这是数据库中的值
        seasonal_stats = {}
        for season in ['春季', '夏季', '秋季', '冬季', '全年']:
            count = Ingredient.query.filter(
                and_(
                    Ingredient.is_active == True,
                    Ingredient.seasonality.like(f'%{season}%')
                )
            ).count()
            seasonal_stats[season] = count
        
        return jsonify({
            'success': True,
            'stats': {
                'total_ingredients': total_ingredients,
                'safe_for_dogs': safe_for_dogs,
                'safe_for_cats': safe_for_cats,
                'common_allergens': common_allergens,
                'seasonal_distribution': seasonal_stats
            }
        })
        
    except Exception as e:
        print(f"❌ Failed to get statistics: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500