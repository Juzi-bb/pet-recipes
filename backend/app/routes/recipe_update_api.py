# recipe_update_api.py
from flask import Blueprint, request, jsonify, session
from werkzeug.exceptions import BadRequest
from app.extensions import get_db_connection
import logging

recipe_update_bp = Blueprint('recipe_update', __name__)

@recipe_update_bp.route('/api/recipe/update', methods=['POST'])
def update_recipe():
    """更新食谱"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user_id = session['user_id']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        # 验证必需字段
        required_fields = ['id', 'name', 'ingredients']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必需字段: {field}'}), 400
        
        recipe_id = data['id']
        recipe_name = data['name'].strip()
        recipe_description = data.get('description', '').strip()
        ingredients = data['ingredients']
        
        # 验证数据
        if not recipe_name:
            return jsonify({'success': False, 'message': '食谱名称不能为空'}), 400
        
        if not ingredients or len(ingredients) == 0:
            return jsonify({'success': False, 'message': '请至少添加一种食材'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查食谱是否存在且属于当前用户
        cursor.execute('''
            SELECT user_id, status FROM recipes WHERE id = ?
        ''', (recipe_id,))
        
        recipe = cursor.fetchone()
        
        if not recipe:
            conn.close()
            return jsonify({'success': False, 'message': '食谱不存在'}), 404
        
        if recipe[0] != user_id:
            conn.close()
            return jsonify({'success': False, 'message': '您没有权限编辑此食谱'}), 403
        
        try:
            # 开始事务
            cursor.execute('BEGIN TRANSACTION')
            
            # 更新食谱基本信息
            cursor.execute('''
                UPDATE recipes 
                SET name = ?, description = ?, updated_at = datetime('now')
                WHERE id = ?
            ''', (recipe_name, recipe_description, recipe_id))
            
            # 删除原有的食材关联
            cursor.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', (recipe_id,))
            
            # 验证所有食材是否存在
            ingredient_ids = [ing['ingredient_id'] for ing in ingredients]
            placeholders = ','.join(['?' for _ in ingredient_ids])
            cursor.execute(f'SELECT id FROM ingredients WHERE id IN ({placeholders})', ingredient_ids)
            existing_ingredients = [row[0] for row in cursor.fetchall()]
            
            # 检查是否有不存在的食材
            missing_ingredients = set(ingredient_ids) - set(existing_ingredients)
            if missing_ingredients:
                raise ValueError(f'食材不存在: {missing_ingredients}')
            
            # 添加新的食材关联
            for ingredient in ingredients:
                ingredient_id = ingredient['ingredient_id']
                weight = float(ingredient['weight'])
                
                if weight <= 0 or weight > 10000:
                    raise ValueError(f'食材重量必须在0-10000g之间')
                
                cursor.execute('''
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_id, weight)
                    VALUES (?, ?, ?)
                ''', (recipe_id, ingredient_id, weight))
            
            # 重新计算营养信息
            nutrition_data = calculate_recipe_nutrition_for_update(cursor, recipe_id)
            
            # 检查过敏信息
            allergy_warnings = check_recipe_allergies(cursor, recipe_id, user_id)
            
            # 提交事务
            conn.commit()
            
            logging.info(f"用户 {user_id} 成功更新食谱 {recipe_id}: {recipe_name}")
            
            return jsonify({
                'success': True,
                'message': '食谱更新成功',
                'recipe_id': recipe_id,
                'nutrition': nutrition_data,
                'allergy_warnings': allergy_warnings
            })
            
        except Exception as e:
            # 回滚事务
            cursor.execute('ROLLBACK')
            raise e
            
    except ValueError as e:
        if conn:
            conn.close()
        return jsonify({'success': False, 'message': str(e)}), 400
        
    except Exception as e:
        if conn:
            conn.close()
        logging.error(f"更新食谱出错: {e}")
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500
    
    finally:
        if conn:
            conn.close()


def calculate_recipe_nutrition_for_update(cursor, recipe_id):
    """计算食谱营养信息（用于更新）"""
    try:
        cursor.execute('''
            SELECT i.calories_per_100g, i.protein_per_100g, i.fat_per_100g, 
                i.carbs_per_100g, i.fiber_per_100g, i.calcium_per_100g, ri.weight
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        ''', (recipe_id,))
        
        ingredients_nutrition = cursor.fetchall()
        
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_fiber = 0
        total_calcium = 0
        
        for nutrition in ingredients_nutrition:
            weight_ratio = nutrition[6] / 100.0  # 转换为百克比例
            
            total_calories += (nutrition[0] or 0) * weight_ratio
            total_protein += (nutrition[1] or 0) * weight_ratio
            total_fat += (nutrition[2] or 0) * weight_ratio
            total_carbs += (nutrition[3] or 0) * weight_ratio
            total_fiber += (nutrition[4] or 0) * weight_ratio
            total_calcium += (nutrition[5] or 0) * weight_ratio
        
        return {
            'total_calories': round(total_calories, 2),
            'total_protein': round(total_protein, 2),
            'total_fat': round(total_fat, 2),
            'total_carbs': round(total_carbs, 2),
            'total_fiber': round(total_fiber, 2),
            'total_calcium': round(total_calcium, 2)
        }
        
    except Exception as e:
        logging.error(f"计算营养信息出错: {e}")
        return {
            'total_calories': 0,
            'total_protein': 0,
            'total_fat': 0,
            'total_carbs': 0,
            'total_fiber': 0,
            'total_calcium': 0
        }


def check_recipe_allergies(cursor, recipe_id, user_id):
    """检查食谱过敏信息"""
    try:
        # 获取用户宠物的过敏信息
        cursor.execute('''
            SELECT DISTINCT pa.allergy_type, pa.severity, i.name as ingredient_name
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            JOIN pet_allergies pa ON (
                (pa.allergy_type = 'ingredient' AND pa.allergen_name = i.name) OR
                (pa.allergy_type = 'category' AND pa.allergen_name = i.category)
            )
            JOIN pets p ON pa.pet_id = p.id
            WHERE ri.recipe_id = ? AND p.user_id = ?
        ''', (recipe_id, user_id))
        
        allergies = cursor.fetchall()
        
        warnings = []
        for allergy in allergies:
            warnings.append({
                'type': allergy[0],
                'severity': allergy[1],
                'ingredient': allergy[2],
                'message': f"注意：{allergy[2]} 可能引起{allergy[1]}过敏反应"
            })
        
        return warnings
        
    except Exception as e:
        logging.error(f"检查过敏信息出错: {e}")
        return []


@recipe_update_bp.route('/api/ingredients', methods=['GET'])
def get_all_ingredients():
    """获取所有食材列表（用于编辑时选择）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, calories_per_100g, protein_per_100g, 
                fat_per_100g, carbs_per_100g, fiber_per_100g, calcium_per_100g
            FROM ingredients
            ORDER BY name
        ''')
        
        ingredients = cursor.fetchall()
        conn.close()
        
        ingredients_data = []
        for ingredient in ingredients:
            ingredients_data.append({
                'id': ingredient[0],
                'name': ingredient[1],
                'category': ingredient[2],
                'calories_per_100g': ingredient[3] or 0,
                'protein_per_100g': ingredient[4] or 0,
                'fat_per_100g': ingredient[5] or 0,
                'carbs_per_100g': ingredient[6] or 0,
                'fiber_per_100g': ingredient[7] or 0,
                'calcium_per_100g': ingredient[8] or 0
            })
        
        return jsonify({'success': True, 'ingredients': ingredients_data})
        
    except Exception as e:
        logging.error(f"获取食材列表出错: {e}")
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500