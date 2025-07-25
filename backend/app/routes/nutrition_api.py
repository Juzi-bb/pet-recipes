"""
营养计算API路由
提供实时营养计算和比例推荐功能
"""

from flask import Blueprint, request, jsonify, session
from app.models.ingredient_model import Ingredient
from app.models.pet_model import Pet
from app.utils.nutrition_ratio_config import NutritionRatioService, NutritionProfile
from app.extensions import db
import json
import traceback

nutrition_api_bp = Blueprint('nutrition_api', __name__)

@nutrition_api_bp.route('/api/nutrition/calculate', methods=['POST'])
def calculate_nutrition():
    """实时计算营养成分"""
    try:
        # 检查用户登录状态
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        ingredients_data = data.get('ingredients', [])
        pet_id = data.get('pet_id')
        
        print(f"收到营养计算请求: {data}")  # 调试日志
        
        if not ingredients_data:
            return jsonify({'error': '请选择食材'}), 400
        
        # 修复：统一处理pet_id数据类型
        if pet_id:
            try:
                pet_id = int(pet_id)  # 确保是整数
            except (ValueError, TypeError):
                pet_id = None
        
        # 修复：统一数据格式处理
        ingredient_ids = []
        weight_map = {}
        
        for item in ingredients_data:
            # 支持两种字段名格式：ingredient_id 和 id
            ingredient_id = item.get('ingredient_id') or item.get('id')
            weight = float(item.get('weight', 0))
            
            if ingredient_id and weight > 0:
                ingredient_ids.append(int(ingredient_id))
                weight_map[int(ingredient_id)] = weight
        
        if not ingredient_ids:
            return jsonify({'error': '请为食材设置有效重量'}), 400
        
        print(f"处理的食材ID: {ingredient_ids}")
        print(f"重量映射: {weight_map}")
        
        # 获取食材信息
        ingredients = Ingredient.query.filter(Ingredient.id.in_(ingredient_ids)).all()
        if not ingredients:
            return jsonify({'error': '未找到有效食材'}), 404
        
        print(f"找到食材数量: {len(ingredients)}")
        
        # 获取宠物信息（可选）
        pet = None
        if pet_id:
            pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
            if pet:
                print(f"找到宠物: {pet.name}")
        
        # 计算总营养成分
        total_nutrition = {
            'total_weight': 0.0,
            'calories': 0.0,
            'protein': 0.0,
            'fat': 0.0,
            'carbohydrate': 0.0,
            'fiber': 0.0,
            'calcium': 0.0,
            'phosphorus': 0.0,
            'vitamin_a': 0.0,
            'vitamin_d': 0.0,
            'taurine': 0.0,
            'omega_3': 0.0,
            'omega_6': 0.0
        }
        
        ingredient_details = []
        
        for ingredient in ingredients:
            weight = weight_map.get(ingredient.id, 0)
            if weight <= 0:
                continue
            
            print(f"处理食材: {ingredient.name}, 重量: {weight}g")
            
            # 重量比例 (基于100g)
            weight_ratio = weight / 100.0
            
            # 计算该食材的营养贡献 - 修复：处理None值
            contribution = {
                'calories': (ingredient.calories or 0) * weight_ratio,
                'protein': (ingredient.protein or 0) * weight_ratio,
                'fat': (ingredient.fat or 0) * weight_ratio,
                'carbohydrate': (ingredient.carbohydrate or 0) * weight_ratio,
                'fiber': (ingredient.fiber or 0) * weight_ratio,
                'calcium': (ingredient.calcium or 0) * weight_ratio,
                'phosphorus': (ingredient.phosphorus or 0) * weight_ratio,
                'vitamin_a': (ingredient.vitamin_a or 0) * weight_ratio,
                'vitamin_d': (ingredient.vitamin_d or 0) * weight_ratio,
                'taurine': (ingredient.taurine or 0) * weight_ratio,
                'omega_3': (getattr(ingredient, 'omega_3_fatty_acids', None) or 0) * weight_ratio,
                'omega_6': (getattr(ingredient, 'omega_6_fatty_acids', None) or 0) * weight_ratio,
            }
            
            # 累加到总营养
            total_nutrition['total_weight'] += weight
            for key in total_nutrition:
                if key != 'total_weight' and key in contribution:
                    total_nutrition[key] += contribution[key]
            
            # 记录食材详情
            ingredient_details.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'category': ingredient.category.value,
                'weight': weight,
                'percentage': 0,  # 稍后计算
                'contribution': contribution
            })
        
        # 计算每个食材的重量百分比
        if total_nutrition['total_weight'] > 0:
            for detail in ingredient_details:
                detail['percentage'] = round((detail['weight'] / total_nutrition['total_weight']) * 100, 1)
        
        # 计算营养比例
        nutrition_ratios = {}
        if total_nutrition['total_weight'] > 0:
            nutrition_ratios = {
                'protein_percent': round((total_nutrition['protein'] / total_nutrition['total_weight']) * 100, 1),
                'fat_percent': round((total_nutrition['fat'] / total_nutrition['total_weight']) * 100, 1),
                'carbohydrate_percent': round((total_nutrition['carbohydrate'] / total_nutrition['total_weight']) * 100, 1),
                'fiber_percent': round((total_nutrition['fiber'] / total_nutrition['total_weight']) * 100, 1),
                'calories_per_100g': round((total_nutrition['calories'] / total_nutrition['total_weight']) * 100, 1)
            }
        
        # 营养评估（简化版）
        nutrition_analysis = assess_nutrition_adequacy(total_nutrition, nutrition_ratios, pet)
        
        # 返回结果
        result = {
            'success': True,
            'total_nutrition': total_nutrition,
            'nutrition_ratios': nutrition_ratios,
            'ingredient_details': ingredient_details,
            'nutrition_analysis': nutrition_analysis,
            'pet_info': {
                'id': pet.id,
                'name': pet.name,
                'species': pet.species,
                'weight': pet.weight
            } if pet else None
        }
        
        print(f"营养计算成功: 总重量={total_nutrition['total_weight']}g, 热量={total_nutrition['calories']:.1f}kcal")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"营养计算失败: {str(e)}")
        traceback.print_exc()  # 打印完整错误堆栈
        return jsonify({'error': f'计算营养成分失败: {str(e)}'}), 500

@nutrition_api_bp.route('/api/nutrition/plans', methods=['GET'])
def get_nutrition_plans():
    """获取营养方案列表"""
    try:
        pet_id = request.args.get('pet_id')
        
        if not pet_id:
            # 返回所有基础方案
            plans = []
            for profile, plan in NutritionRatioService.NUTRITION_PLANS.items():
                plans.append({
                    'id': profile.value,
                    'name': plan.name,
                    'description': plan.description,
                    'special_notes': plan.special_notes,
                    'category_ratios': {
                        'red_meat': plan.category_ratios.red_meat,
                        'white_meat': plan.category_ratios.white_meat,
                        'fish': plan.category_ratios.fish,
                        'organs': plan.category_ratios.organs,
                        'vegetables': plan.category_ratios.vegetables,
                        'fruits': plan.category_ratios.fruits,
                        'grains': plan.category_ratios.grains
                    },
                    'is_recommended': False
                })
            return jsonify({'plans': plans})
        
        # 根据宠物信息推荐方案
        pet = Pet.query.filter_by(id=int(pet_id), user_id=session.get('user_id')).first()
        if not pet:
            return jsonify({'error': '宠物信息不存在'}), 404
        
        # 解析特殊需求
        special_needs = []
        if pet.special_needs and pet.special_needs != 'None':
            special_needs = [need.strip() for need in pet.special_needs.split(',')]
        
        # 获取推荐方案
        suitable_profiles = NutritionRatioService.get_suitable_plans(
            pet.species, pet.age, special_needs
        )
        
        plans = []
        for profile in suitable_profiles:
            plan = NutritionRatioService.get_plan(profile)
            if plan:
                plans.append({
                    'id': profile.value,
                    'name': plan.name,
                    'description': plan.description,
                    'special_notes': plan.special_notes,
                    'category_ratios': {
                        'red_meat': plan.category_ratios.red_meat,
                        'white_meat': plan.category_ratios.white_meat,
                        'fish': plan.category_ratios.fish,
                        'organs': plan.category_ratios.organs,
                        'vegetables': plan.category_ratios.vegetables,
                        'fruits': plan.category_ratios.fruits,
                        'grains': plan.category_ratios.grains
                    },
                    'is_recommended': True
                })
        
        # 添加其他可选方案
        all_profiles = set(NutritionRatioService.NUTRITION_PLANS.keys())
        other_profiles = all_profiles - set(suitable_profiles)
        
        for profile in other_profiles:
            plan = NutritionRatioService.get_plan(profile)
            if plan:
                plans.append({
                    'id': profile.value,
                    'name': plan.name,
                    'description': plan.description,
                    'special_notes': plan.special_notes,
                    'category_ratios': {
                        'red_meat': plan.category_ratios.red_meat,
                        'white_meat': plan.category_ratios.white_meat,
                        'fish': plan.category_ratios.fish,
                        'organs': plan.category_ratios.organs,
                        'vegetables': plan.category_ratios.vegetables,
                        'fruits': plan.category_ratios.fruits,
                        'grains': plan.category_ratios.grains
                    },
                    'is_recommended': False
                })
        
        return jsonify({'plans': plans})
        
    except Exception as e:
        print(f"获取营养方案失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'获取营养方案失败: {str(e)}'}), 500

@nutrition_api_bp.route('/api/nutrition/suggest-weights', methods=['POST'])
def suggest_ingredient_weights():
    """根据营养方案推荐食材重量"""
    try:
        data = request.get_json()
        ingredient_ids = data.get('ingredient_ids', [])
        nutrition_plan_id = data.get('nutrition_plan_id')
        pet_id = data.get('pet_id')
        total_weight = data.get('total_weight', 200)  # 默认200g
        
        if not ingredient_ids or not nutrition_plan_id:
            return jsonify({'error': '参数不完整'}), 400
        
        # 获取营养方案
        try:
            nutrition_profile = NutritionProfile(nutrition_plan_id)
            nutrition_plan = NutritionRatioService.get_plan(nutrition_profile)
        except ValueError:
            return jsonify({'error': '无效的营养方案'}), 400
        
        if not nutrition_plan:
            return jsonify({'error': '营养方案不存在'}), 404
        
        # 获取食材信息
        ingredients = Ingredient.query.filter(Ingredient.id.in_(ingredient_ids)).all()
        ingredient_dict = {ing.id: ing for ing in ingredients}
        
        # 计算推荐重量
        suggested_weights = NutritionRatioService.calculate_ingredient_weights(
            nutrition_plan, total_weight, ingredient_dict
        )
        
        # 如果有宠物信息，调整总重量
        if pet_id:
            pet = Pet.query.filter_by(id=pet_id, user_id=session.get('user_id')).first()
            if pet:
                # 根据宠物体重计算建议的日食量
                daily_food_amount = calculate_daily_food_amount(pet.weight, pet.species, pet.age)
                total_weight = daily_food_amount
                
                # 重新计算重量
                suggested_weights = NutritionRatioService.calculate_ingredient_weights(
                    nutrition_plan, total_weight, ingredient_dict
                )
        
        # 格式化返回结果
        result = []
        for ingredient in ingredients:
            weight = suggested_weights.get(ingredient.id, 0)
            result.append({
                'ingredient_id': ingredient.id,
                'ingredient_name': ingredient.name,
                'category': ingredient.category.value,
                'suggested_weight': round(weight, 1),
                'percentage': round((weight / total_weight) * 100, 1) if total_weight > 0 else 0
            })
        
        return jsonify({
            'suggested_weights': result,
            'total_weight': total_weight,
            'nutrition_plan': {
                'name': nutrition_plan.name,
                'description': nutrition_plan.description
            }
        })
        
    except Exception as e:
        print(f"计算推荐重量失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'计算推荐重量失败: {str(e)}'}), 500

def assess_nutrition_adequacy(total_nutrition, nutrition_ratios, pet=None):
    """评估营养充足性"""
    assessment = {
        'status': 'calculated',
        'warnings': [],
        'recommendations': [],
        'score': 0
    }
    
    if not nutrition_ratios:
        assessment['status'] = 'insufficient_data'
        return assessment
    
    score = 0
    
    # 基础营养比例检查
    protein_percent = nutrition_ratios.get('protein_percent', 0)
    fat_percent = nutrition_ratios.get('fat_percent', 0)
    carb_percent = nutrition_ratios.get('carbohydrate_percent', 0)
    
    # 蛋白质检查
    if protein_percent < 15:
        assessment['warnings'].append('蛋白质含量偏低，建议增加肉类食材')
        score += 20
    elif protein_percent > 40:
        assessment['warnings'].append('蛋白质含量偏高，建议减少肉类食材')
        score += 60
    elif 18 <= protein_percent <= 30:
        score += 100
        assessment['recommendations'].append('蛋白质比例良好')
    else:
        score += 80
    
    # 脂肪检查
    if fat_percent < 5:
        assessment['warnings'].append('脂肪含量偏低，建议添加适量脂肪来源')
    elif fat_percent > 25:
        assessment['warnings'].append('脂肪含量偏高，建议减少高脂食材')
    elif 8 <= fat_percent <= 15:
        assessment['recommendations'].append('脂肪比例适中')
    
    # 碳水化合物检查
    if carb_percent > 30:
        assessment['warnings'].append('碳水化合物含量偏高，注意控制谷物类食材')
    elif carb_percent <= 20:
        assessment['recommendations'].append('碳水化合物比例合理')
    
    # 钙磷比检查
    if total_nutrition.get('calcium', 0) > 0 and total_nutrition.get('phosphorus', 0) > 0:
        ca_p_ratio = total_nutrition['calcium'] / total_nutrition['phosphorus']
        if ca_p_ratio < 0.8:
            assessment['warnings'].append('钙磷比偏低，建议增加含钙食材')
        elif ca_p_ratio > 2.5:
            assessment['warnings'].append('钙磷比偏高，建议平衡钙磷摄入')
        else:
            assessment['recommendations'].append('钙磷比例良好')
    
    # 设置总体状态
    if len(assessment['warnings']) == 0:
        assessment['status'] = 'excellent'
        assessment['recommendations'].append('营养配比优秀，可以保存此食谱')
    elif len(assessment['warnings']) <= 2:
        assessment['status'] = 'good'
        assessment['recommendations'].append('营养配比良好，可考虑微调')
    else:
        assessment['status'] = 'needs_improvement'
        assessment['recommendations'].append('建议调整食材比例以改善营养平衡')
    
    assessment['score'] = min(score // 3, 100)  # 转换为100分制
    
    return assessment

# 辅助函数：计算每日推荐食量
def calculate_daily_food_amount(weight_kg, species, age):
    """计算每日推荐食量（克）"""
    try:
        # 基础代谢率计算（简化）
        if species.lower() == 'dog':
            if age < 1:  # 幼犬
                daily_calories = weight_kg * 100
            elif age > 7:  # 老年犬
                daily_calories = weight_kg * 80
            else:  # 成犬
                daily_calories = weight_kg * 95
        else:  # 猫
            if age < 1:  # 幼猫
                daily_calories = weight_kg * 120
            elif age > 7:  # 老年猫
                daily_calories = weight_kg * 85
            else:  # 成猫
                daily_calories = weight_kg * 100
        
        # 假设食物热量密度为每克3.5大卡
        daily_food_g = daily_calories / 3.5
        return round(daily_food_g, 1)
        
    except:
        # 默认值
        return weight_kg * 25