"""
营养数据初始化脚本
基于AAFCO标准创建基础的食材数据和营养需求标准
"""
import os
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app
from app.extensions import db
from app.models.ingredient_model import Ingredient, IngredientCategory
from app.models.user_model import User
from app.models.pet_model import Pet
from app.models.nutrition_requirements_model import NutritionRequirement, PetType, LifeStage, ActivityLevel
from datetime import datetime

def init_basic_ingredients(force_reinit=False):
    """初始化基础食材数据"""
    
    # 如果强制重新初始化，先删除所有现有食材
    if force_reinit:
        print("🗑️ 正在删除现有食材数据...")
        existing_ingredients = Ingredient.query.all()
        for ingredient in existing_ingredients:
            db.session.delete(ingredient)
        db.session.commit()
        print(f"已删除 {len(existing_ingredients)} 个现有食材")

    # 基础食材数据 (营养成分基于USDA数据库和宠物食品资料)
    basic_ingredients = [
        # 红肉类
        {
            'name': '牛肉(瘦)', 'name_en': 'Beef (lean)', 'category': IngredientCategory.RED_MEAT,
            'image_filename': 'beef_lean.png', 'seasonality': 'all_year',
            'calories': 250, 'protein': 26.0, 'fat': 15.0, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.0,
            'calcium': 18, 'phosphorus': 200, 'potassium': 370, 'sodium': 72, 'chloride': 110, 'magnesium': 21,
            'iron': 2.6, 'copper': 0.1, 'manganese': 0.01, 'zinc': 4.8, 'iodine': 0.005, 'selenium': 0.026,
            'vitamin_a': 0, 'vitamin_d': 0, 'vitamin_e': 0.6, 'vitamin_k': 1.5,
            'thiamine': 0.04, 'riboflavin': 0.15, 'niacin': 4.2, 'pantothenic_acid': 0.65, 'pyridoxine': 0.38,
            'folic_acid': 0.006, 'vitamin_b12': 2.6, 'biotin': 0.003, 'choline': 69,
            'arginine': 1630, 'histidine': 860, 'isoleucine': 1240, 'leucine': 2080, 'lysine': 2260,
            'methionine': 680, 'phenylalanine': 1060, 'threonine': 1150, 'tryptophan': 280, 'valine': 1360,
            'taurine': 5, 'alpha_linolenic_acid': 0.02, 'eicosapentaenoic_acid': 0.01,
            'docosahexaenoic_acid': 0.002, 'arachidonic_acid': 0.03, 'omega_3_fatty_acids': 0.05, 'omega_6_fatty_acids': 0.8,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '切成小块，煮熟或烤制', 'storage_notes': '冷藏保存，3-5天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '羊肉', 'name_en': 'Lamb', 'category': IngredientCategory.RED_MEAT,
            'image_filename': 'lamb.png', 'seasonality': 'spring,winter',
            'calories': 294, 'protein': 25.0, 'fat': 21.0, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 65.0, 'ash': 1.0,
            'calcium': 17, 'phosphorus': 188, 'potassium': 310, 'sodium': 72, 'chloride': 110, 'magnesium': 20,
            'iron': 1.9, 'copper': 0.13, 'manganese': 0.02, 'zinc': 3.9, 'iodine': 0.003, 'selenium': 0.027,
            'vitamin_a': 0, 'vitamin_d': 0, 'vitamin_e': 0.4, 'vitamin_k': 1.2,
            'thiamine': 0.09, 'riboflavin': 0.21, 'niacin': 5.7, 'pantothenic_acid': 0.67, 'pyridoxine': 0.13,
            'folic_acid': 0.018, 'vitamin_b12': 2.7, 'biotin': 0.003, 'choline': 79,
            'arginine': 1440, 'histidine': 720, 'isoleucine': 1100, 'leucine': 1800, 'lysine': 2120,
            'methionine': 620, 'phenylalanine': 920, 'threonine': 1030, 'tryptophan': 240, 'valine': 1200,
            'taurine': 8, 'alpha_linolenic_acid': 0.15, 'eicosapentaenoic_acid': 0.02,
            'docosahexaenoic_acid': 0.005, 'arachidonic_acid': 0.08, 'omega_3_fatty_acids': 0.2, 'omega_6_fatty_acids': 1.2,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去骨切块，慢炖或烤制', 'storage_notes': '冷藏保存，2-3天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '猪肉', 'name_en': 'Pork', 'category': IngredientCategory.RED_MEAT,
            'image_filename': 'pork.png', 'seasonality': 'all_year',
            'calories': 242, 'protein': 25.7, 'fat': 14.0, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.0,
            'calcium': 19, 'phosphorus': 246, 'potassium': 423, 'sodium': 62, 'chloride': 95, 'magnesium': 28,
            'iron': 0.9, 'copper': 0.08, 'manganese': 0.01, 'zinc': 2.9, 'iodine': 0.001, 'selenium': 0.038,
            'vitamin_a': 2, 'vitamin_d': 53, 'vitamin_e': 0.3, 'vitamin_k': 0.0,
            'thiamine': 0.54, 'riboflavin': 0.32, 'niacin': 4.6, 'pantothenic_acid': 0.91, 'pyridoxine': 0.46,
            'folic_acid': 0.005, 'vitamin_b12': 0.7, 'biotin': 0.005, 'choline': 103,
            'arginine': 1610, 'histidine': 920, 'isoleucine': 1200, 'leucine': 2010, 'lysine': 2280,
            'methionine': 680, 'phenylalanine': 1030, 'threonine': 1170, 'tryptophan': 300, 'valine': 1330,
            'taurine': 0, 'alpha_linolenic_acid': 0.08, 'eicosapentaenoic_acid': 0.01,
            'docosahexaenoic_acid': 0.003, 'arachidonic_acid': 0.06, 'omega_3_fatty_acids': 0.1, 'omega_6_fatty_acids': 1.7,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '必须完全煮熟，去除多余脂肪', 'storage_notes': '冷藏保存，2-3天内使用',
            'data_source': 'USDA Food Database'
        },
        
        # 白肉类
        {
            'name': '鸡胸肉', 'name_en': 'Chicken breast', 'category': IngredientCategory.WHITE_MEAT,
            'image_filename': 'chicken_breast.png', 'seasonality': 'all_year',
            'calories': 165, 'protein': 31.0, 'fat': 3.6, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 75.0, 'ash': 1.0,
            'calcium': 15, 'phosphorus': 228, 'potassium': 256, 'sodium': 74, 'chloride': 77, 'magnesium': 29,
            'iron': 0.9, 'copper': 0.05, 'manganese': 0.02, 'zinc': 0.9, 'iodine': 0.006, 'selenium': 0.027,
            'vitamin_a': 21, 'vitamin_d': 0, 'vitamin_e': 0.3, 'vitamin_k': 0.3,
            'thiamine': 0.07, 'riboflavin': 0.11, 'niacin': 10.9, 'pantothenic_acid': 0.97, 'pyridoxine': 0.6,
            'folic_acid': 0.004, 'vitamin_b12': 0.3, 'biotin': 0.01, 'choline': 85,
            'arginine': 1890, 'histidine': 820, 'isoleucine': 1340, 'leucine': 2220, 'lysine': 2630,
            'methionine': 850, 'phenylalanine': 1200, 'threonine': 1270, 'tryptophan': 350, 'valine': 1430,
            'taurine': 15, 'alpha_linolenic_acid': 0.03, 'eicosapentaenoic_acid': 0.01,
            'docosahexaenoic_acid': 0.008, 'arachidonic_acid': 0.08, 'omega_3_fatty_acids': 0.05, 'omega_6_fatty_acids': 0.8,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去皮去骨，蒸煮或烤制', 'storage_notes': '冷藏保存，1-2天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '鸡腿肉', 'name_en': 'Chicken thigh', 'category': IngredientCategory.WHITE_MEAT,
            'image_filename': 'chicken_thigh.png', 'seasonality': 'all_year',
            'calories': 209, 'protein': 26.0, 'fat': 11.0, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.0,
            'calcium': 11, 'phosphorus': 180, 'potassium': 230, 'sodium': 90, 'chloride': 94, 'magnesium': 23,
            'iron': 1.3, 'copper': 0.08, 'manganese': 0.02, 'zinc': 1.4, 'iodine': 0.004, 'selenium': 0.019,
            'vitamin_a': 60, 'vitamin_d': 0, 'vitamin_e': 0.2, 'vitamin_k': 0.4,
            'thiamine': 0.08, 'riboflavin': 0.19, 'niacin': 6.2, 'pantothenic_acid': 1.0, 'pyridoxine': 0.4,
            'folic_acid': 0.008, 'vitamin_b12': 0.4, 'biotin': 0.01, 'choline': 74,
            'arginine': 1560, 'histidine': 680, 'isoleucine': 1110, 'leucine': 1840, 'lysine': 2170,
            'methionine': 710, 'phenylalanine': 990, 'threonine': 1050, 'tryptophan': 290, 'valine': 1180,
            'taurine': 18, 'alpha_linolenic_acid': 0.08, 'eicosapentaenoic_acid': 0.01,
            'docosahexaenoic_acid': 0.01, 'arachidonic_acid': 0.15, 'omega_3_fatty_acids': 0.1, 'omega_6_fatty_acids': 2.0,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去皮去骨，慢炖或烤制', 'storage_notes': '冷藏保存，1-2天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '火鸡肉', 'name_en': 'Turkey', 'category': IngredientCategory.WHITE_MEAT,
            'image_filename': 'turkey.png', 'seasonality': 'autumn,winter',
            'calories': 189, 'protein': 29.0, 'fat': 7.0, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.0,
            'calcium': 21, 'phosphorus': 230, 'potassium': 298, 'sodium': 70, 'chloride': 73, 'magnesium': 27,
            'iron': 1.4, 'copper': 0.1, 'manganese': 0.02, 'zinc': 1.7, 'iodine': 0.034, 'selenium': 0.031,
            'vitamin_a': 0, 'vitamin_d': 0, 'vitamin_e': 0.1, 'vitamin_k': 0.4,
            'thiamine': 0.05, 'riboflavin': 0.11, 'niacin': 6.0, 'pantothenic_acid': 0.87, 'pyridoxine': 0.47,
            'folic_acid': 0.008, 'vitamin_b12': 0.3, 'biotin': 0.01, 'choline': 69,
            'arginine': 1710, 'histidine': 790, 'isoleucine': 1280, 'leucine': 2120, 'lysine': 2520,
            'methionine': 810, 'phenylalanine': 1140, 'threonine': 1210, 'tryptophan': 330, 'valine': 1360,
            'taurine': 12, 'alpha_linolenic_acid': 0.06, 'eicosapentaenoic_acid': 0.01,
            'docosahexaenoic_acid': 0.01, 'arachidonic_acid': 0.09, 'omega_3_fatty_acids': 0.08, 'omega_6_fatty_acids': 1.8,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去皮切块，烤制或蒸煮', 'storage_notes': '冷藏保存，2-3天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '鸭肉', 'name_en': 'Duck', 'category': IngredientCategory.WHITE_MEAT,
            'image_filename': 'duck.png', 'seasonality': 'autumn,winter',
            'calories': 337, 'protein': 19.0, 'fat': 28.0, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 64.0, 'ash': 1.0,
            'calcium': 12, 'phosphorus': 203, 'potassium': 271, 'sodium': 74, 'chloride': 77, 'magnesium': 21,
            'iron': 2.7, 'copper': 0.23, 'manganese': 0.02, 'zinc': 1.9, 'iodine': 0.006, 'selenium': 0.014,
            'vitamin_a': 56, 'vitamin_d': 0, 'vitamin_e': 0.7, 'vitamin_k': 4.8,
            'thiamine': 0.18, 'riboflavin': 1.04, 'niacin': 9.4, 'pantothenic_acid': 6.2, 'pyridoxine': 0.65,
            'folic_acid': 0.56, 'vitamin_b12': 16.6, 'biotin': 0.21, 'choline': 194,
            'arginine': 1350, 'histidine': 580, 'isoleucine': 1040, 'leucine': 1820, 'lysine': 1650,
            'methionine': 520, 'phenylalanine': 1010, 'threonine': 940, 'tryptophan': 240, 'valine': 1190,
            'taurine': 50, 'alpha_linolenic_acid': 0.02, 'eicosapentaenoic_acid': 0.02,
            'docosahexaenoic_acid': 0.04, 'arachidonic_acid': 0.35, 'omega_3_fatty_acids': 0.08, 'omega_6_fatty_acids': 1.2,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '煮熟切小块，不宜过量', 'storage_notes': '冷藏保存，当天使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '鹌鹑肉', 'name_en': 'Quail meat', 'category': IngredientCategory.WHITE_MEAT,
            'image_filename': 'quail_meat.png', 'seasonality': 'all_year',
            'calories': 227, 'protein': 25.1, 'fat': 14.1, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.1,
            'calcium': 15, 'phosphorus': 307, 'potassium': 237, 'sodium': 51, 'chloride': 78, 'magnesium': 25,
            'iron': 4.5, 'copper': 0.66, 'manganese': 0.02, 'zinc': 3.1, 'iodine': 0.008, 'selenium': 0.026,
            'vitamin_a': 84, 'vitamin_d': 0, 'vitamin_e': 1.2, 'vitamin_k': 0.0,
            'thiamine': 0.28, 'riboflavin': 0.28, 'niacin': 8.1, 'pantothenic_acid': 1.8, 'pyridoxine': 0.52,
            'folic_acid': 0.009, 'vitamin_b12': 0.58, 'biotin': 0.01, 'choline': 124,
            'arginine': 1650, 'histidine': 680, 'isoleucine': 1210, 'leucine': 1920, 'lysine': 2140,
            'methionine': 650, 'phenylalanine': 980, 'threonine': 1080, 'tryptophan': 320, 'valine': 1280,
            'taurine': 25, 'alpha_linolenic_acid': 0.08, 'eicosapentaenoic_acid': 0.02,
            'docosahexaenoic_acid': 0.06, 'arachidonic_acid': 0.45, 'omega_3_fatty_acids': 0.16, 'omega_6_fatty_acids': 3.2,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '高蛋白质密度，优质蛋白质来源', 'storage_notes': '冷藏保存，1-2天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '鸡蛋', 'name_en': 'Chicken egg', 'category': IngredientCategory.WHITE_MEAT,
            'image_filename': 'chicken_egg.png', 'seasonality': 'all_year',
            'calories': 155, 'protein': 13.0, 'fat': 11.0, 'carbohydrate': 1.1, 'fiber': 0.0, 'moisture': 76.0, 'ash': 1.1,
            'calcium': 56, 'phosphorus': 198, 'potassium': 138, 'sodium': 142, 'chloride': 218, 'magnesium': 12,
            'iron': 1.8, 'copper': 0.07, 'manganese': 0.03, 'zinc': 1.3, 'iodine': 0.024, 'selenium': 0.031,
            'vitamin_a': 540, 'vitamin_d': 87, 'vitamin_e': 1.0, 'vitamin_k': 0.3,
            'thiamine': 0.04, 'riboflavin': 0.46, 'niacin': 0.07, 'pantothenic_acid': 1.44, 'pyridoxine': 0.17,
            'folic_acid': 0.047, 'vitamin_b12': 0.89, 'biotin': 0.025, 'choline': 251,
            'arginine': 755, 'histidine': 244, 'isoleucine': 686, 'leucine': 1086, 'lysine': 912,
            'methionine': 392, 'phenylalanine': 680, 'threonine': 556, 'tryptophan': 167, 'valine': 858,
            'taurine': 4, 'alpha_linolenic_acid': 0.04, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.04, 'arachidonic_acid': 0.15, 'omega_3_fatty_acids': 0.1, 'omega_6_fatty_acids': 1.4,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '完全煮熟，营养丰富的完整蛋白质', 'storage_notes': '冷藏保存，3周内使用',
            'data_source': 'USDA Food Database'
        },
        
        # 鱼类
        {
            'name': '三文鱼', 'name_en': 'Salmon', 'category': IngredientCategory.FISH,
            'image_filename': 'salmon.png', 'seasonality': 'spring,summer,autumn',
            'calories': 208, 'protein': 25.4, 'fat': 12.4, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.2,
            'calcium': 9, 'phosphorus': 289, 'potassium': 628, 'sodium': 44, 'chloride': 165, 'magnesium': 37,
            'iron': 0.3, 'copper': 0.05, 'manganese': 0.02, 'zinc': 0.4, 'iodine': 0.015, 'selenium': 0.041,
            'vitamin_a': 59, 'vitamin_d': 526, 'vitamin_e': 3.6, 'vitamin_k': 0.1,
            'thiamine': 0.23, 'riboflavin': 0.15, 'niacin': 8.5, 'pantothenic_acid': 1.66, 'pyridoxine': 0.6,
            'folic_acid': 0.025, 'vitamin_b12': 3.2, 'biotin': 0.005, 'choline': 91,
            'arginine': 1530, 'histidine': 750, 'isoleucine': 1170, 'leucine': 2060, 'lysine': 2170,
            'methionine': 700, 'phenylalanine': 990, 'threonine': 1110, 'tryptophan': 290, 'valine': 1310,
            'taurine': 130, 'alpha_linolenic_acid': 0.44, 'eicosapentaenoic_acid': 0.69,
            'docosahexaenoic_acid': 1.1, 'arachidonic_acid': 0.09, 'omega_3_fatty_acids': 2.3, 'omega_6_fatty_acids': 0.9,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '去骨去皮，蒸煮或烤制，避免生食', 'storage_notes': '冷藏保存，当天使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '鳕鱼', 'name_en': 'Cod', 'category': IngredientCategory.FISH,
            'image_filename': 'cod.png', 'seasonality': 'winter,spring',
            'calories': 105, 'protein': 23.0, 'fat': 0.9, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 82.0, 'ash': 1.2,
            'calcium': 18, 'phosphorus': 203, 'potassium': 468, 'sodium': 78, 'chloride': 120, 'magnesium': 32,
            'iron': 0.4, 'copper': 0.04, 'manganese': 0.02, 'zinc': 0.5, 'iodine': 0.11, 'selenium': 0.033,
            'vitamin_a': 40, 'vitamin_d': 36, 'vitamin_e': 0.4, 'vitamin_k': 0.1,
            'thiamine': 0.07, 'riboflavin': 0.07, 'niacin': 2.1, 'pantothenic_acid': 0.18, 'pyridoxine': 0.24,
            'folic_acid': 0.007, 'vitamin_b12': 0.9, 'biotin': 0.001, 'choline': 65,
            'arginine': 1380, 'histidine': 680, 'isoleucine': 1060, 'leucine': 1870, 'lysine': 1980,
            'methionine': 640, 'phenylalanine': 900, 'threonine': 1010, 'tryptophan': 260, 'valine': 1180,
            'taurine': 120, 'alpha_linolenic_acid': 0.004, 'eicosapentaenoic_acid': 0.15,
            'docosahexaenoic_acid': 0.15, 'arachidonic_acid': 0.007, 'omega_3_fatty_acids': 0.4, 'omega_6_fatty_acids': 0.01,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '去骨蒸煮，肉质细嫩', 'storage_notes': '冷藏保存，当天使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '金枪鱼', 'name_en': 'Tuna', 'category': IngredientCategory.FISH,
            'image_filename': 'tuna.png', 'seasonality': 'summer,autumn',
            'calories': 184, 'protein': 30.0, 'fat': 6.3, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 68.0, 'ash': 1.3,
            'calcium': 8, 'phosphorus': 254, 'potassium': 441, 'sodium': 43, 'chloride': 66, 'magnesium': 50,
            'iron': 1.0, 'copper': 0.09, 'manganese': 0.01, 'zinc': 0.6, 'iodine': 0.015, 'selenium': 0.108,
            'vitamin_a': 20, 'vitamin_d': 200, 'vitamin_e': 1.0, 'vitamin_k': 0.2,
            'thiamine': 0.24, 'riboflavin': 0.25, 'niacin': 18.8, 'pantothenic_acid': 0.28, 'pyridoxine': 1.0,
            'folic_acid': 0.005, 'vitamin_b12': 9.4, 'biotin': 0.001, 'choline': 65,
            'arginine': 1780, 'histidine': 890, 'isoleucine': 1390, 'leucine': 2440, 'lysine': 2590,
            'methionine': 835, 'phenylalanine': 1180, 'threonine': 1320, 'tryptophan': 340, 'valine': 1550,
            'taurine': 160, 'alpha_linolenic_acid': 0.02, 'eicosapentaenoic_acid': 0.28,
            'docosahexaenoic_acid': 1.14, 'arachidonic_acid': 0.04, 'omega_3_fatty_acids': 1.6, 'omega_6_fatty_acids': 0.2,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '选择低汞品种，适量食用', 'storage_notes': '冷藏保存，当天使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '沙丁鱼', 'name_en': 'Sardine', 'category': IngredientCategory.FISH,
            'image_filename': 'sardine.png', 'seasonality': 'summer,autumn',
            'calories': 208, 'protein': 25.0, 'fat': 11.5, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 72.0, 'ash': 2.9,
            'calcium': 382, 'phosphorus': 490, 'potassium': 397, 'sodium': 307, 'chloride': 472, 'magnesium': 39,
            'iron': 2.9, 'copper': 0.19, 'manganese': 0.11, 'zinc': 1.3, 'iodine': 0.035, 'selenium': 0.053,
            'vitamin_a': 32, 'vitamin_d': 272, 'vitamin_e': 2.0, 'vitamin_k': 2.6,
            'thiamine': 0.02, 'riboflavin': 0.23, 'niacin': 5.2, 'pantothenic_acid': 0.64, 'pyridoxine': 0.17,
            'folic_acid': 0.01, 'vitamin_b12': 8.9, 'biotin': 0.006, 'choline': 142,
            'arginine': 1480, 'histidine': 740, 'isoleucine': 1150, 'leucine': 2030, 'lysine': 2290,
            'methionine': 740, 'phenylalanine': 980, 'threonine': 1100, 'tryptophan': 280, 'valine': 1290,
            'taurine': 200, 'alpha_linolenic_acid': 0.15, 'eicosapentaenoic_acid': 0.48,
            'docosahexaenoic_acid': 0.51, 'arachidonic_acid': 0.17, 'omega_3_fatty_acids': 1.4, 'omega_6_fatty_acids': 1.5,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '可连骨食用，营养丰富', 'storage_notes': '冷藏保存，1-2天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '鲭鱼', 'name_en': 'Mackerel', 'category': IngredientCategory.FISH,
            'image_filename': 'mackerel.png', 'seasonality': 'spring,summer,autumn',
            'calories': 205, 'protein': 19.0, 'fat': 13.9, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.4,
            'calcium': 12, 'phosphorus': 217, 'potassium': 314, 'sodium': 90, 'chloride': 138, 'magnesium': 60,
            'iron': 1.6, 'copper': 0.09, 'manganese': 0.02, 'zinc': 0.6, 'iodine': 0.043, 'selenium': 0.044,
            'vitamin_a': 252, 'vitamin_d': 388, 'vitamin_e': 1.5, 'vitamin_k': 5.4,
            'thiamine': 0.15, 'riboflavin': 0.31, 'niacin': 9.1, 'pantothenic_acid': 0.86, 'pyridoxine': 0.4,
            'folic_acid': 0.002, 'vitamin_b12': 8.7, 'biotin': 0.008, 'choline': 65,
            'arginine': 1140, 'histidine': 560, 'isoleucine': 880, 'leucine': 1550, 'lysine': 1750,
            'methionine': 560, 'phenylalanine': 740, 'threonine': 830, 'tryptophan': 210, 'valine': 980,
            'taurine': 280, 'alpha_linolenic_acid': 0.10, 'eicosapentaenoic_acid': 0.90,
            'docosahexaenoic_acid': 1.40, 'arachidonic_acid': 0.22, 'omega_3_fatty_acids': 2.6, 'omega_6_fatty_acids': 0.2,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '富含牛磺酸和DHA，对心脏和眼睛极佳', 'storage_notes': '冷藏保存，当天使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '秋刀鱼', 'name_en': 'Pacific saury', 'category': IngredientCategory.FISH,
            'image_filename': 'pacific_saury.png', 'seasonality': 'autumn',
            'calories': 185, 'protein': 20.7, 'fat': 10.4, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 72.0, 'ash': 1.2,
            'calcium': 27, 'phosphorus': 240, 'potassium': 280, 'sodium': 32, 'chloride': 49, 'magnesium': 28,
            'iron': 1.4, 'copper': 0.08, 'manganese': 0.01, 'zinc': 0.6, 'iodine': 0.035, 'selenium': 0.036,
            'vitamin_a': 17, 'vitamin_d': 154, 'vitamin_e': 1.1, 'vitamin_k': 0.8,
            'thiamine': 0.01, 'riboflavin': 0.21, 'niacin': 10.1, 'pantothenic_acid': 0.75, 'pyridoxine': 0.45,
            'folic_acid': 0.017, 'vitamin_b12': 17.7, 'biotin': 0.002, 'choline': 142,
            'arginine': 1240, 'histidine': 610, 'isoleucine': 950, 'leucine': 1680, 'lysine': 1890,
            'methionine': 610, 'phenylalanine': 810, 'threonine': 910, 'tryptophan': 230, 'valine': 1060,
            'taurine': 320, 'alpha_linolenic_acid': 0.15, 'eicosapentaenoic_acid': 1.20,
            'docosahexaenoic_acid': 2.30, 'arachidonic_acid': 0.15, 'omega_3_fatty_acids': 3.8, 'omega_6_fatty_acids': 0.3,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '超高牛磺酸含量，猫咪的天然补品', 'storage_notes': '新鲜鱼当天使用，冷藏保存',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '生蚝', 'name_en': 'Oyster', 'category': IngredientCategory.FISH,
            'image_filename': 'oyster.png', 'seasonality': 'autumn,winter',
            'calories': 81, 'protein': 9.5, 'fat': 2.3, 'carbohydrate': 4.9, 'fiber': 0.0, 'moisture': 85.0, 'ash': 2.1,
            'calcium': 45, 'phosphorus': 162, 'potassium': 168, 'sodium': 417, 'chloride': 640, 'magnesium': 22,
            'iron': 6.7, 'copper': 4.6, 'manganese': 0.37, 'zinc': 90.8, 'iodine': 0.093, 'selenium': 0.077,
            'vitamin_a': 320, 'vitamin_d': 320, 'vitamin_e': 0.9, 'vitamin_k': 0.3,
            'thiamine': 0.15, 'riboflavin': 0.24, 'niacin': 1.6, 'pantothenic_acid': 0.5, 'pyridoxine': 0.04,
            'folic_acid': 0.025, 'vitamin_b12': 16.0, 'biotin': 0.01, 'choline': 65,
            'arginine': 540, 'histidine': 190, 'isoleucine': 390, 'leucine': 690, 'lysine': 720,
            'methionine': 230, 'phenylalanine': 340, 'threonine': 380, 'tryptophan': 110, 'valine': 450,
            'taurine': 396, 'alpha_linolenic_acid': 0.05, 'eicosapentaenoic_acid': 0.44,
            'docosahexaenoic_acid': 0.24, 'arachidonic_acid': 0.06, 'omega_3_fatty_acids': 0.8, 'omega_6_fatty_acids': 0.2,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '必须完全煮熟，去壳，富含锌和牛磺酸', 'storage_notes': '新鲜生蚝当天使用，冷藏保存',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '虾', 'name_en': 'Shrimp', 'category': IngredientCategory.FISH,
            'image_filename': 'shrimp.png', 'seasonality': 'summer,autumn',
            'calories': 99, 'protein': 24.0, 'fat': 0.3, 'carbohydrate': 0.2, 'fiber': 0.0, 'moisture': 76.0, 'ash': 1.7,
            'calcium': 70, 'phosphorus': 237, 'potassium': 259, 'sodium': 111, 'chloride': 171, 'magnesium': 37,
            'iron': 0.5, 'copper': 0.26, 'manganese': 0.04, 'zinc': 1.6, 'iodine': 0.035, 'selenium': 0.038,
            'vitamin_a': 54, 'vitamin_d': 0, 'vitamin_e': 2.3, 'vitamin_k': 0.3,
            'thiamine': 0.01, 'riboflavin': 0.04, 'niacin': 2.9, 'pantothenic_acid': 0.47, 'pyridoxine': 0.16,
            'folic_acid': 0.003, 'vitamin_b12': 1.1, 'biotin': 0.002, 'choline': 115,
            'arginine': 1740, 'histidine': 480, 'isoleucine': 1180, 'leucine': 1760, 'lysine': 2170,
            'methionine': 540, 'phenylalanine': 990, 'threonine': 920, 'tryptophan': 240, 'valine': 1140,
            'taurine': 154, 'alpha_linolenic_acid': 0.01, 'eicosapentaenoic_acid': 0.17,
            'docosahexaenoic_acid': 0.14, 'arachidonic_acid': 0.01, 'omega_3_fatty_acids': 0.32, 'omega_6_fatty_acids': 0.02,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': True,
            'preparation_notes': '去壳去虾线，完全煮熟，高蛋白低脂', 'storage_notes': '冷藏保存，当天使用',
            'data_source': 'USDA Food Database'
        },
        
        # 内脏类
        {
            'name': '鸡肝', 'name_en': 'Chicken liver', 'category': IngredientCategory.ORGANS,
            'image_filename': 'chicken_liver.png', 'seasonality': 'all_year',
            'calories': 167, 'protein': 24.5, 'fat': 4.8, 'carbohydrate': 0.7, 'fiber': 0.0, 'moisture': 76.0, 'ash': 1.4,
            'calcium': 8, 'phosphorus': 297, 'potassium': 230, 'sodium': 71, 'chloride': 109, 'magnesium': 19,
            'iron': 11.6, 'copper': 0.49, 'manganese': 0.34, 'zinc': 2.7, 'iodine': 0.007, 'selenium': 0.068,
            'vitamin_a': 11078, 'vitamin_d': 19, 'vitamin_e': 0.7, 'vitamin_k': 0.0,
            'thiamine': 0.18, 'riboflavin': 0.22, 'niacin': 4.9, 'pantothenic_acid': 1.3, 'pyridoxine': 0.3,
            'folic_acid': 0.009, 'vitamin_b12': 0.4, 'biotin': 0.01, 'choline': 69,
            'arginine': 1260, 'histidine': 580, 'isoleucine': 940, 'leucine': 1570, 'lysine': 1840,
            'methionine': 570, 'phenylalanine': 820, 'threonine': 880, 'tryptophan': 240, 'valine': 1000,
            'taurine': 8, 'alpha_linolenic_acid': 0.32, 'eicosapentaenoic_acid': 0.04,
            'docosahexaenoic_acid': 0.02, 'arachidonic_acid': 0.13, 'omega_3_fatty_acids': 0.4, 'omega_6_fatty_acids': 5.8,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去皮去脂，烤制或炖煮', 'storage_notes': '冷藏保存，1-2天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '牛肝', 'name_en': 'Beef liver', 'category': IngredientCategory.ORGANS,
            'image_filename': 'beef_liver.png', 'seasonality': 'all_year',
            'calories': 175, 'protein': 26.0, 'fat': 4.9, 'carbohydrate': 5.1, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.4,
            'calcium': 5, 'phosphorus': 387, 'potassium': 380, 'sodium': 69, 'chloride': 106, 'magnesium': 18,
            'iron': 6.2, 'copper': 14.3, 'manganese': 0.34, 'zinc': 4.0, 'iodine': 0.012, 'selenium': 0.039,
            'vitamin_a': 26091, 'vitamin_d': 42, 'vitamin_e': 0.4, 'vitamin_k': 3.1,
            'thiamine': 0.2, 'riboflavin': 2.8, 'niacin': 17.5, 'pantothenic_acid': 7.2, 'pyridoxine': 1.1,
            'folic_acid': 0.29, 'vitamin_b12': 59.3, 'biotin': 0.027, 'choline': 333,
            'arginine': 1540, 'histidine': 660, 'isoleucine': 1180, 'leucine': 2070, 'lysine': 1880,
            'methionine': 590, 'phenylalanine': 1150, 'threonine': 1070, 'tryptophan': 280, 'valine': 1350,
            'taurine': 40, 'alpha_linolenic_acid': 0.04, 'eicosapentaenoic_acid': 0.03,
            'docosahexaenoic_acid': 0.04, 'arachidonic_acid': 0.25, 'omega_3_fatty_acids': 0.11, 'omega_6_fatty_acids': 0.8,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '营养丰富，每周不超过1-2次', 'storage_notes': '冷藏保存，当天使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '鸡心', 'name_en': 'Chicken heart', 'category': IngredientCategory.ORGANS,
            'image_filename': 'chicken_heart.png', 'seasonality': 'all_year',
            'calories': 185, 'protein': 26.4, 'fat': 7.9, 'carbohydrate': 0.1, 'fiber': 0.0, 'moisture': 70.0, 'ash': 1.1,
            'calcium': 7, 'phosphorus': 191, 'potassium': 176, 'sodium': 54, 'chloride': 83, 'magnesium': 21,
            'iron': 9.0, 'copper': 0.28, 'manganese': 0.04, 'zinc': 3.0, 'iodine': 0.004, 'selenium': 0.058,
            'vitamin_a': 36, 'vitamin_d': 0, 'vitamin_e': 0.5, 'vitamin_k': 0.0,
            'thiamine': 0.24, 'riboflavin': 0.91, 'niacin': 6.8, 'pantothenic_acid': 2.5, 'pyridoxine': 0.28,
            'folic_acid': 0.065, 'vitamin_b12': 6.2, 'biotin': 0.01, 'choline': 120,
            'arginine': 1620, 'histidine': 700, 'isoleucine': 1250, 'leucine': 2190, 'lysine': 1990,
            'methionine': 630, 'phenylalanine': 1220, 'threonine': 1140, 'tryptophan': 300, 'valine': 1370,
            'taurine': 1200, 'alpha_linolenic_acid': 0.02, 'eicosapentaenoic_acid': 0.02,
            'docosahexaenoic_acid': 0.08, 'arachidonic_acid': 0.55, 'omega_3_fatty_acids': 0.12, 'omega_6_fatty_acids': 1.8,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '富含牛磺酸，对心脏有益', 'storage_notes': '冷藏保存，1-2天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '猪肾', 'name_en': 'Pork kidney', 'category': IngredientCategory.ORGANS,
            'image_filename': 'pork_kidney.png', 'seasonality': 'all_year',
            'calories': 130, 'protein': 25.4, 'fat': 3.2, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 77.0, 'ash': 1.1,
            'calcium': 14, 'phosphorus': 321, 'potassium': 262, 'sodium': 182, 'chloride': 280, 'magnesium': 17,
            'iron': 10.0, 'copper': 0.42, 'manganese': 0.16, 'zinc': 2.5, 'iodine': 0.051, 'selenium': 0.19,
            'vitamin_a': 475, 'vitamin_d': 42, 'vitamin_e': 0.2, 'vitamin_k': 0.0,
            'thiamine': 0.47, 'riboflavin': 2.84, 'niacin': 8.5, 'pantothenic_acid': 4.5, 'pyridoxine': 0.58,
            'folic_acid': 0.130, 'vitamin_b12': 28.2, 'biotin': 0.164, 'choline': 249,
            'arginine': 1380, 'histidine': 590, 'isoleucine': 1050, 'leucine': 1840, 'lysine': 1740,
            'methionine': 520, 'phenylalanine': 1020, 'threonine': 950, 'tryptophan': 250, 'valine': 1200,
            'taurine': 180, 'alpha_linolenic_acid': 0.08, 'eicosapentaenoic_acid': 0.05,
            'docosahexaenoic_acid': 0.12, 'arachidonic_acid': 0.40, 'omega_3_fatty_acids': 0.25, 'omega_6_fatty_acids': 0.8,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '富含B族维生素和牛磺酸，猫咪每周1-2次', 'storage_notes': '冷藏保存，当天使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '鸡胗', 'name_en': 'Chicken gizzard', 'category': IngredientCategory.ORGANS,
            'image_filename': 'chicken_gizzard.png', 'seasonality': 'all_year',
            'calories': 154, 'protein': 30.4, 'fat': 2.1, 'carbohydrate': 0.7, 'fiber': 0.0, 'moisture': 73.0, 'ash': 1.0,
            'calcium': 13, 'phosphorus': 260, 'potassium': 230, 'sodium': 97, 'chloride': 149, 'magnesium': 26,
            'iron': 4.6, 'copper': 0.34, 'manganese': 0.04, 'zinc': 4.4, 'iodine': 0.012, 'selenium': 0.058,
            'vitamin_a': 48, 'vitamin_d': 0, 'vitamin_e': 0.5, 'vitamin_k': 0.0,
            'thiamine': 0.07, 'riboflavin': 0.15, 'niacin': 4.6, 'pantothenic_acid': 0.75, 'pyridoxine': 0.15,
            'folic_acid': 0.004, 'vitamin_b12': 2.5, 'biotin': 0.003, 'choline': 79,
            'arginine': 1860, 'histidine': 800, 'isoleucine': 1420, 'leucine': 2490, 'lysine': 2260,
            'methionine': 720, 'phenylalanine': 1390, 'threonine': 1300, 'tryptophan': 340, 'valine': 1560,
            'taurine': 150, 'alpha_linolenic_acid': 0.02, 'eicosapentaenoic_acid': 0.01,
            'docosahexaenoic_acid': 0.05, 'arachidonic_acid': 0.25, 'omega_3_fatty_acids': 0.08, 'omega_6_fatty_acids': 0.4,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '高蛋白低脂，富含牛磺酸，质地较韧需充分煮熟', 'storage_notes': '冷藏保存，1-2天内使用',
            'data_source': 'USDA Food Database'
        },
        
        # 蔬菜类
        {
            'name': '胡萝卜', 'name_en': 'Carrot', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'carrot.png', 'seasonality': 'autumn,winter',
            'calories': 41, 'protein': 0.9, 'fat': 0.2, 'carbohydrate': 9.6, 'fiber': 2.8, 'moisture': 88.0, 'ash': 1.0,
            'calcium': 33, 'phosphorus': 35, 'potassium': 320, 'sodium': 69, 'chloride': 106, 'magnesium': 12,
            'iron': 0.3, 'copper': 0.05, 'manganese': 0.14, 'zinc': 0.2, 'iodine': 0.002, 'selenium': 0.0001,
            'vitamin_a': 16706, 'vitamin_d': 0, 'vitamin_e': 0.7, 'vitamin_k': 13.2,
            'thiamine': 0.07, 'riboflavin': 0.06, 'niacin': 1.0, 'pantothenic_acid': 0.27, 'pyridoxine': 0.14,
            'folic_acid': 0.019, 'vitamin_b12': 0.0, 'biotin': 0.006, 'choline': 8.8,
            'arginine': 79, 'histidine': 24, 'isoleucine': 43, 'leucine': 65, 'lysine': 58,
            'methionine': 12, 'phenylalanine': 37, 'threonine': 47, 'tryptophan': 9, 'valine': 48,
            'taurine': 0, 'alpha_linolenic_acid': 0.002, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.002, 'omega_6_fatty_acids': 0.12,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '蒸煮切丁，有助消化', 'storage_notes': '阴凉干燥处保存，可保存1-2周',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '西兰花', 'name_en': 'Broccoli', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'broccoli.png', 'seasonality': 'autumn,winter,spring',
            'calories': 34, 'protein': 2.8, 'fat': 0.4, 'carbohydrate': 7.0, 'fiber': 2.6, 'moisture': 89.0, 'ash': 0.8,
            'calcium': 47, 'phosphorus': 66, 'potassium': 316, 'sodium': 33, 'chloride': 51, 'magnesium': 21,
            'iron': 0.7, 'copper': 0.05, 'manganese': 0.21, 'zinc': 0.4, 'iodine': 0.015, 'selenium': 0.0025,
            'vitamin_a': 623, 'vitamin_d': 0, 'vitamin_e': 0.8, 'vitamin_k': 102,
            'thiamine': 0.07, 'riboflavin': 0.12, 'niacin': 0.6, 'pantothenic_acid': 0.57, 'pyridoxine': 0.18,
            'folic_acid': 0.063, 'vitamin_b12': 0.0, 'biotin': 0.0015, 'choline': 19,
            'arginine': 152, 'histidine': 57, 'isoleucine': 120, 'leucine': 156, 'lysine': 146,
            'methionine': 44, 'phenylalanine': 129, 'threonine': 105, 'tryptophan': 33, 'valine': 149,
            'taurine': 0, 'alpha_linolenic_acid': 0.02, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.02, 'omega_6_fatty_acids': 0.06,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '蒸煮至软烂，少量食用', 'storage_notes': '冷藏保存，3-5天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '南瓜', 'name_en': 'Pumpkin', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'pumpkin.png', 'seasonality': 'autumn',
            'calories': 26, 'protein': 1.0, 'fat': 0.1, 'carbohydrate': 6.5, 'fiber': 0.5, 'moisture': 92.0, 'ash': 0.8,
            'calcium': 21, 'phosphorus': 44, 'potassium': 340, 'sodium': 1, 'chloride': 15, 'magnesium': 12,
            'iron': 0.8, 'copper': 0.13, 'manganese': 0.13, 'zinc': 0.3, 'iodine': 0.001, 'selenium': 0.0003,
            'vitamin_a': 8513, 'vitamin_d': 0, 'vitamin_e': 1.1, 'vitamin_k': 1.1,
            'thiamine': 0.05, 'riboflavin': 0.11, 'niacin': 0.6, 'pantothenic_acid': 0.3, 'pyridoxine': 0.06,
            'folic_acid': 0.016, 'vitamin_b12': 0.0, 'biotin': 0.0003, 'choline': 8.2,
            'arginine': 61, 'histidine': 21, 'isoleucine': 37, 'leucine': 65, 'lysine': 69,
            'methionine': 7, 'phenylalanine': 36, 'threonine': 38, 'tryptophan': 12, 'valine': 43,
            'taurine': 0, 'alpha_linolenic_acid': 0.005, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.005, 'omega_6_fatty_acids': 0.04,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '蒸煮去皮，有助消化', 'storage_notes': '干燥处保存，可保存数月',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '红薯', 'name_en': 'Sweet potato', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'sweet_potato.png', 'seasonality': 'autumn',
            'calories': 86, 'protein': 1.6, 'fat': 0.1, 'carbohydrate': 20.1, 'fiber': 3.0, 'moisture': 77.0, 'ash': 1.0,
            'calcium': 30, 'phosphorus': 47, 'potassium': 337, 'sodium': 4, 'chloride': 6, 'magnesium': 25,
            'iron': 0.6, 'copper': 0.15, 'manganese': 0.26, 'zinc': 0.3, 'iodine': 0.001, 'selenium': 0.0006,
            'vitamin_a': 14187, 'vitamin_d': 0, 'vitamin_e': 0.3, 'vitamin_k': 1.8,
            'thiamine': 0.08, 'riboflavin': 0.06, 'niacin': 0.6, 'pantothenic_acid': 0.88, 'pyridoxine': 0.21,
            'folic_acid': 0.011, 'vitamin_b12': 0.0, 'biotin': 0.0006, 'choline': 12.3,
            'arginine': 61, 'histidine': 24, 'isoleucine': 63, 'leucine': 92, 'lysine': 78,
            'methionine': 31, 'phenylalanine': 80, 'threonine': 78, 'tryptophan': 18, 'valine': 86,
            'taurine': 0, 'alpha_linolenic_acid': 0.006, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.006, 'omega_6_fatty_acids': 0.01,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '蒸煮去皮，适量食用', 'storage_notes': '干燥处保存，可保存数周',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '菠菜', 'name_en': 'Spinach', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'spinach.png', 'seasonality': 'spring,autumn',
            'calories': 23, 'protein': 2.9, 'fat': 0.4, 'carbohydrate': 3.6, 'fiber': 2.2, 'moisture': 91.0, 'ash': 1.7,
            'calcium': 99, 'phosphorus': 49, 'potassium': 558, 'sodium': 79, 'chloride': 121, 'magnesium': 79,
            'iron': 2.7, 'copper': 0.13, 'manganese': 0.9, 'zinc': 0.5, 'iodine': 0.002, 'selenium': 0.001,
            'vitamin_a': 9377, 'vitamin_d': 0, 'vitamin_e': 2.0, 'vitamin_k': 483,
            'thiamine': 0.08, 'riboflavin': 0.19, 'niacin': 0.7, 'pantothenic_acid': 0.07, 'pyridoxine': 0.2,
            'folic_acid': 0.194, 'vitamin_b12': 0.0, 'biotin': 0.0007, 'choline': 19.3,
            'arginine': 162, 'histidine': 64, 'isoleucine': 147, 'leucine': 224, 'lysine': 174,
            'methionine': 53, 'phenylalanine': 129, 'threonine': 122, 'tryptophan': 39, 'valine': 161,
            'taurine': 0, 'alpha_linolenic_acid': 0.14, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.14, 'omega_6_fatty_acids': 0.03,
            'is_safe_for_dogs': True, 'is_safe_for_cats': False, 'is_common_allergen': False,
            'preparation_notes': '少量食用，含草酸，猫咪不宜', 'storage_notes': '冷藏保存，2-3天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '蘑菇', 'name_en': 'Mushroom', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'mushroom.png', 'seasonality': 'all_year',
            'calories': 22, 'protein': 3.1, 'fat': 0.3, 'carbohydrate': 3.3, 'fiber': 1.0, 'moisture': 92.0, 'ash': 0.8,
            'calcium': 3, 'phosphorus': 86, 'potassium': 318, 'sodium': 5, 'chloride': 8, 'magnesium': 9,
            'iron': 0.5, 'copper': 0.32, 'manganese': 0.05, 'zinc': 0.5, 'iodine': 0.018, 'selenium': 0.0093,
            'vitamin_a': 0, 'vitamin_d': 375, 'vitamin_e': 0.01, 'vitamin_k': 0.0,
            'thiamine': 0.08, 'riboflavin': 0.4, 'niacin': 3.6, 'pantothenic_acid': 1.5, 'pyridoxine': 0.1,
            'folic_acid': 0.017, 'vitamin_b12': 0.04, 'biotin': 0.016, 'choline': 17.3,
            'arginine': 85, 'histidine': 57, 'isoleucine': 86, 'leucine': 120, 'lysine': 107,
            'methionine': 31, 'phenylalanine': 85, 'threonine': 107, 'tryptophan': 35, 'valine': 231,
            'taurine': 0, 'alpha_linolenic_acid': 0.001, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.001, 'omega_6_fatty_acids': 0.05,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '只喂食商业种植的蘑菇，野生蘑菇有毒', 'storage_notes': '冷藏保存，2-3天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '彩椒', 'name_en': 'Bell pepper', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'bell_pepper.png', 'seasonality': 'summer,autumn',
            'calories': 31, 'protein': 1.0, 'fat': 0.3, 'carbohydrate': 7.3, 'fiber': 2.5, 'moisture': 92.0, 'ash': 0.4,
            'calcium': 7, 'phosphorus': 26, 'potassium': 211, 'sodium': 4, 'chloride': 6, 'magnesium': 12,
            'iron': 0.4, 'copper': 0.02, 'manganese': 0.11, 'zinc': 0.3, 'iodine': 0.001, 'selenium': 0.0001,
            'vitamin_a': 3131, 'vitamin_d': 0, 'vitamin_e': 1.6, 'vitamin_k': 8.8,
            'thiamine': 0.05, 'riboflavin': 0.09, 'niacin': 1.0, 'pantothenic_acid': 0.32, 'pyridoxine': 0.29,
            'folic_acid': 0.046, 'vitamin_b12': 0.0, 'biotin': 0.0006, 'choline': 5.6,
            'arginine': 62, 'histidine': 19, 'isoleucine': 30, 'leucine': 50, 'lysine': 53,
            'methionine': 12, 'phenylalanine': 37, 'threonine': 35, 'tryptophan': 11, 'valine': 41,
            'taurine': 0, 'alpha_linolenic_acid': 0.03, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.03, 'omega_6_fatty_acids': 0.06,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去籽去蒂，蒸煮至软，富含维生素C', 'storage_notes': '冷藏保存，1周内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '孢子甘蓝', 'name_en': 'Brussels sprouts', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'brussels_sprouts.png', 'seasonality': 'autumn,winter',
            'calories': 43, 'protein': 3.4, 'fat': 0.3, 'carbohydrate': 8.9, 'fiber': 3.8, 'moisture': 86.0, 'ash': 1.4,
            'calcium': 42, 'phosphorus': 69, 'potassium': 389, 'sodium': 25, 'chloride': 38, 'magnesium': 23,
            'iron': 1.4, 'copper': 0.07, 'manganese': 0.34, 'zinc': 0.4, 'iodine': 0.002, 'selenium': 0.0017,
            'vitamin_a': 754, 'vitamin_d': 0, 'vitamin_e': 0.9, 'vitamin_k': 177,
            'thiamine': 0.14, 'riboflavin': 0.09, 'niacin': 0.7, 'pantothenic_acid': 0.31, 'pyridoxine': 0.22,
            'folic_acid': 0.061, 'vitamin_b12': 0.0, 'biotin': 0.0017, 'choline': 19.1,
            'arginine': 131, 'histidine': 68, 'isoleucine': 112, 'leucine': 178, 'lysine': 169,
            'methionine': 28, 'phenylalanine': 125, 'threonine': 134, 'tryptophan': 38, 'valine': 155,
            'taurine': 0, 'alpha_linolenic_acid': 0.18, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.18, 'omega_6_fatty_acids': 0.06,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '蒸煮至软烂，少量食用避免胀气', 'storage_notes': '冷藏保存，1周内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '山药', 'name_en': 'Chinese yam', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'chinese_yam.png', 'seasonality': 'autumn,winter',
            'calories': 118, 'protein': 1.5, 'fat': 0.2, 'carbohydrate': 27.9, 'fiber': 4.1, 'moisture': 70.0, 'ash': 0.8,
            'calcium': 17, 'phosphorus': 55, 'potassium': 816, 'sodium': 9, 'chloride': 14, 'magnesium': 21,
            'iron': 0.5, 'copper': 0.18, 'manganese': 0.4, 'zinc': 0.2, 'iodine': 0.001, 'selenium': 0.0007,
            'vitamin_a': 138, 'vitamin_d': 0, 'vitamin_e': 0.4, 'vitamin_k': 2.3,
            'thiamine': 0.11, 'riboflavin': 0.03, 'niacin': 0.5, 'pantothenic_acid': 0.31, 'pyridoxine': 0.29,
            'folic_acid': 0.023, 'vitamin_b12': 0.0, 'biotin': 0.0008, 'choline': 16.5,
            'arginine': 46, 'histidine': 31, 'isoleucine': 34, 'leucine': 56, 'lysine': 70,
            'methionine': 8, 'phenylalanine': 40, 'threonine': 33, 'tryptophan': 7, 'valine': 44,
            'taurine': 0, 'alpha_linolenic_acid': 0.004, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.004, 'omega_6_fatty_acids': 0.09,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去皮蒸煮至软烂，易消化的碳水化合物', 'storage_notes': '阴凉干燥处保存，可保存数周',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '土豆', 'name_en': 'Potato', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'potato.png', 'seasonality': 'all_year',
            'calories': 77, 'protein': 2.1, 'fat': 0.1, 'carbohydrate': 17.5, 'fiber': 2.1, 'moisture': 79.0, 'ash': 1.1,
            'calcium': 12, 'phosphorus': 57, 'potassium': 425, 'sodium': 6, 'chloride': 9, 'magnesium': 23,
            'iron': 0.8, 'copper': 0.11, 'manganese': 0.15, 'zinc': 0.3, 'iodine': 0.002, 'selenium': 0.0004,
            'vitamin_a': 2, 'vitamin_d': 0, 'vitamin_e': 0.01, 'vitamin_k': 2.0,
            'thiamine': 0.08, 'riboflavin': 0.03, 'niacin': 1.1, 'pantothenic_acid': 0.3, 'pyridoxine': 0.3,
            'folic_acid': 0.015, 'vitamin_b12': 0.0, 'biotin': 0.0004, 'choline': 12.1,
            'arginine': 101, 'histidine': 38, 'isoleucine': 84, 'leucine': 125, 'lysine': 109,
            'methionine': 32, 'phenylalanine': 85, 'threonine': 69, 'tryptophan': 31, 'valine': 105,
            'taurine': 0, 'alpha_linolenic_acid': 0.003, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.003, 'omega_6_fatty_acids': 0.04,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去皮煮熟，避免绿色部分和芽眼，含龙葵素有毒', 'storage_notes': '阴凉干燥处保存，避免发芽变绿',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '西葫芦', 'name_en': 'Zucchini', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'zucchini.png', 'seasonality': 'summer,autumn',
            'calories': 17, 'protein': 1.2, 'fat': 0.3, 'carbohydrate': 3.1, 'fiber': 1.0, 'moisture': 95.0, 'ash': 0.4,
            'calcium': 16, 'phosphorus': 38, 'potassium': 261, 'sodium': 8, 'chloride': 12, 'magnesium': 18,
            'iron': 0.4, 'copper': 0.05, 'manganese': 0.18, 'zinc': 0.3, 'iodine': 0.002, 'selenium': 0.0002,
            'vitamin_a': 200, 'vitamin_d': 0, 'vitamin_e': 0.1, 'vitamin_k': 4.3,
            'thiamine': 0.05, 'riboflavin': 0.09, 'niacin': 0.5, 'pantothenic_acid': 0.20, 'pyridoxine': 0.16,
            'folic_acid': 0.024, 'vitamin_b12': 0.0, 'biotin': 0.0015, 'choline': 9.5,
            'arginine': 48, 'histidine': 21, 'isoleucine': 52, 'leucine': 71, 'lysine': 69,
            'methionine': 18, 'phenylalanine': 43, 'threonine': 41, 'tryptophan': 11, 'valine': 62,
            'taurine': 0, 'alpha_linolenic_acid': 0.06, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.06, 'omega_6_fatty_acids': 0.05,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '低热量高水分，蒸煮或生食皆可', 'storage_notes': '冷藏保存，1周内使用',
            'data_source': 'USDA Food Database'
        },

        {
            'name': '青豆', 'name_en': 'Green peas', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'green_peas.png', 'seasonality': 'spring,summer',
            'calories': 81, 'protein': 5.4, 'fat': 0.4, 'carbohydrate': 14.5, 'fiber': 5.7, 'moisture': 78.0, 'ash': 0.9,
            'calcium': 25, 'phosphorus': 108, 'potassium': 244, 'sodium': 5, 'chloride': 8, 'magnesium': 33,
            'iron': 1.5, 'copper': 0.18, 'manganese': 0.41, 'zinc': 1.2, 'iodine': 0.002, 'selenium': 0.0018,
            'vitamin_a': 765, 'vitamin_d': 0, 'vitamin_e': 0.1, 'vitamin_k': 24.8,
            'thiamine': 0.27, 'riboflavin': 0.13, 'niacin': 2.1, 'pantothenic_acid': 0.10, 'pyridoxine': 0.17,
            'folic_acid': 0.065, 'vitamin_b12': 0.0, 'biotin': 0.0019, 'choline': 28.4,
            'arginine': 274, 'histidine': 119, 'isoleucine': 207, 'leucine': 364, 'lysine': 353,
            'methionine': 54, 'phenylalanine': 217, 'threonine': 190, 'tryptophan': 60, 'valine': 233,
            'taurine': 0, 'alpha_linolenic_acid': 0.04, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.04, 'omega_6_fatty_acids': 0.2,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '高纤维高蛋白，蒸煮至软', 'storage_notes': '新鲜豆荚冷藏3-5天，冷冻可保存数月',
            'data_source': 'USDA Food Database'
        },

        {
            'name': '芹菜', 'name_en': 'Celery', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'celery.png', 'seasonality': 'autumn,winter',
            'calories': 16, 'protein': 0.7, 'fat': 0.2, 'carbohydrate': 3.0, 'fiber': 1.6, 'moisture': 95.0, 'ash': 0.8,
            'calcium': 40, 'phosphorus': 24, 'potassium': 260, 'sodium': 80, 'chloride': 123, 'magnesium': 11,
            'iron': 0.2, 'copper': 0.04, 'manganese': 0.10, 'zinc': 0.1, 'iodine': 0.002, 'selenium': 0.0004,
            'vitamin_a': 449, 'vitamin_d': 0, 'vitamin_e': 0.3, 'vitamin_k': 29.3,
            'thiamine': 0.02, 'riboflavin': 0.06, 'niacin': 0.3, 'pantothenic_acid': 0.25, 'pyridoxine': 0.07,
            'folic_acid': 0.036, 'vitamin_b12': 0.0, 'biotin': 0.0004, 'choline': 6.1,
            'arginine': 32, 'histidine': 13, 'isoleucine': 28, 'leucine': 42, 'lysine': 37,
            'methionine': 9, 'phenylalanine': 24, 'threonine': 27, 'tryptophan': 9, 'valine': 33,
            'taurine': 0, 'alpha_linolenic_acid': 0.001, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.001, 'omega_6_fatty_acids': 0.08,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '切小段避免窒息，低热量高纤维', 'storage_notes': '冷藏保存，1-2周内使用',
            'data_source': 'USDA Food Database'
        },

        {
            'name': '黄瓜', 'name_en': 'Cucumber', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'cucumber.png', 'seasonality': 'summer',
            'calories': 16, 'protein': 0.7, 'fat': 0.1, 'carbohydrate': 3.6, 'fiber': 0.5, 'moisture': 95.0, 'ash': 0.4,
            'calcium': 16, 'phosphorus': 24, 'potassium': 147, 'sodium': 2, 'chloride': 3, 'magnesium': 13,
            'iron': 0.3, 'copper': 0.04, 'manganese': 0.08, 'zinc': 0.2, 'iodine': 0.001, 'selenium': 0.0003,
            'vitamin_a': 105, 'vitamin_d': 0, 'vitamin_e': 0.03, 'vitamin_k': 16.4,
            'thiamine': 0.03, 'riboflavin': 0.03, 'niacin': 0.1, 'pantothenic_acid': 0.26, 'pyridoxine': 0.04,
            'folic_acid': 0.007, 'vitamin_b12': 0.0, 'biotin': 0.0003, 'choline': 6.0,
            'arginine': 42, 'histidine': 14, 'isoleucine': 26, 'leucine': 39, 'lysine': 37,
            'methionine': 8, 'phenylalanine': 25, 'threonine': 22, 'tryptophan': 5, 'valine': 27,
            'taurine': 0, 'alpha_linolenic_acid': 0.005, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.005, 'omega_6_fatty_acids': 0.03,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去皮切片，清爽低热量，夏季补水佳品', 'storage_notes': '冷藏保存，1周内使用',
            'data_source': 'USDA Food Database'
        },
        
        # 水果类
        {
            'name': '苹果', 'name_en': 'Apple', 'category': IngredientCategory.FRUITS,
            'image_filename': 'apple.png', 'seasonality': 'autumn',
            'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbohydrate': 13.8, 'fiber': 2.4, 'moisture': 86.0, 'ash': 0.2,
            'calcium': 6, 'phosphorus': 11, 'potassium': 107, 'sodium': 1, 'chloride': 15, 'magnesium': 5,
            'iron': 0.1, 'copper': 0.03, 'manganese': 0.04, 'zinc': 0.04, 'iodine': 0.001, 'selenium': 0.0,
            'vitamin_a': 54, 'vitamin_d': 0, 'vitamin_e': 0.2, 'vitamin_k': 2.2,
            'thiamine': 0.02, 'riboflavin': 0.03, 'niacin': 0.09, 'pantothenic_acid': 0.06, 'pyridoxine': 0.04,
            'folic_acid': 0.003, 'vitamin_b12': 0.0, 'biotin': 0.0003, 'choline': 3.4,
            'arginine': 6, 'histidine': 3, 'isoleucine': 7, 'leucine': 13, 'lysine': 12,
            'methionine': 1, 'phenylalanine': 6, 'threonine': 6, 'tryptophan': 1, 'valine': 10,
            'taurine': 0, 'alpha_linolenic_acid': 0.009, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.009, 'omega_6_fatty_acids': 0.04,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去核去籽，少量食用', 'storage_notes': '阴凉处保存，可保存1-2周',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '蓝莓', 'name_en': 'Blueberry', 'category': IngredientCategory.FRUITS,
            'image_filename': 'blueberry.png', 'seasonality': 'summer',
            'calories': 57, 'protein': 0.7, 'fat': 0.3, 'carbohydrate': 14.5, 'fiber': 2.4, 'moisture': 84.0, 'ash': 0.2,
            'calcium': 6, 'phosphorus': 12, 'potassium': 77, 'sodium': 1, 'chloride': 15, 'magnesium': 6,
            'iron': 0.3, 'copper': 0.06, 'manganese': 0.34, 'zinc': 0.2, 'iodine': 0.001, 'selenium': 0.0001,
            'vitamin_a': 80, 'vitamin_d': 0, 'vitamin_e': 0.6, 'vitamin_k': 19.3,
            'thiamine': 0.04, 'riboflavin': 0.04, 'niacin': 0.4, 'pantothenic_acid': 0.12, 'pyridoxine': 0.05,
            'folic_acid': 0.006, 'vitamin_b12': 0.0, 'biotin': 0.0002, 'choline': 6.0,
            'arginine': 25, 'histidine': 8, 'isoleucine': 20, 'leucine': 34, 'lysine': 16,
            'methionine': 7, 'phenylalanine': 20, 'threonine': 20, 'tryptophan': 6, 'valine': 24,
            'taurine': 0, 'alpha_linolenic_acid': 0.06, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.06, 'omega_6_fatty_acids': 0.09,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '富含抗氧化剂，适量食用', 'storage_notes': '冷藏保存，3-5天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '香蕉', 'name_en': 'Banana', 'category': IngredientCategory.FRUITS,
            'image_filename': 'banana.png', 'seasonality': 'all_year',
            'calories': 89, 'protein': 1.1, 'fat': 0.3, 'carbohydrate': 22.8, 'fiber': 2.6, 'moisture': 75.0, 'ash': 0.8,
            'calcium': 5, 'phosphorus': 22, 'potassium': 358, 'sodium': 1, 'chloride': 15, 'magnesium': 27,
            'iron': 0.3, 'copper': 0.08, 'manganese': 0.27, 'zinc': 0.2, 'iodine': 0.003, 'selenium': 0.001,
            'vitamin_a': 64, 'vitamin_d': 0, 'vitamin_e': 0.1, 'vitamin_k': 0.5,
            'thiamine': 0.03, 'riboflavin': 0.07, 'niacin': 0.7, 'pantothenic_acid': 0.33, 'pyridoxine': 0.37,
            'folic_acid': 0.02, 'vitamin_b12': 0.0, 'biotin': 0.004, 'choline': 9.8,
            'arginine': 49, 'histidine': 77, 'isoleucine': 28, 'leucine': 68, 'lysine': 50,
            'methionine': 8, 'phenylalanine': 49, 'threonine': 28, 'tryptophan': 9, 'valine': 47,
            'taurine': 0, 'alpha_linolenic_acid': 0.03, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.03, 'omega_6_fatty_acids': 0.05,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去皮切片，糖分较高，少量食用', 'storage_notes': '室温保存，数天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '梨', 'name_en': 'Pear', 'category': IngredientCategory.FRUITS,
            'image_filename': 'pear.png', 'seasonality': 'autumn',
            'calories': 57, 'protein': 0.4, 'fat': 0.1, 'carbohydrate': 15.2, 'fiber': 3.1, 'moisture': 84.0, 'ash': 0.3,
            'calcium': 9, 'phosphorus': 12, 'potassium': 116, 'sodium': 1, 'chloride': 15, 'magnesium': 7,
            'iron': 0.2, 'copper': 0.08, 'manganese': 0.05, 'zinc': 0.1, 'iodine': 0.001, 'selenium': 0.0001,
            'vitamin_a': 25, 'vitamin_d': 0, 'vitamin_e': 0.1, 'vitamin_k': 4.4,
            'thiamine': 0.01, 'riboflavin': 0.03, 'niacin': 0.16, 'pantothenic_acid': 0.05, 'pyridoxine': 0.03,
            'folic_acid': 0.007, 'vitamin_b12': 0.0, 'biotin': 0.0001, 'choline': 5.1,
            'arginine': 8, 'histidine': 3, 'isoleucine': 8, 'leucine': 15, 'lysine': 14,
            'methionine': 1, 'phenylalanine': 8, 'threonine': 8, 'tryptophan': 2, 'valine': 11,
            'taurine': 0, 'alpha_linolenic_acid': 0.002, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.002, 'omega_6_fatty_acids': 0.09,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去核去籽，果核含氰化物有毒，果肉适量食用', 'storage_notes': '室温保存至成熟，然后冷藏',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '草莓', 'name_en': 'Strawberry', 'category': IngredientCategory.FRUITS,
            'image_filename': 'strawberry.png', 'seasonality': 'spring,summer',
            'calories': 32, 'protein': 0.7, 'fat': 0.3, 'carbohydrate': 7.7, 'fiber': 2.0, 'moisture': 91.0, 'ash': 0.4,
            'calcium': 16, 'phosphorus': 24, 'potassium': 153, 'sodium': 1, 'chloride': 15, 'magnesium': 13,
            'iron': 0.4, 'copper': 0.05, 'manganese': 0.39, 'zinc': 0.1, 'iodine': 0.001, 'selenium': 0.0004,
            'vitamin_a': 12, 'vitamin_d': 0, 'vitamin_e': 0.3, 'vitamin_k': 2.2,
            'thiamine': 0.02, 'riboflavin': 0.02, 'niacin': 0.4, 'pantothenic_acid': 0.12, 'pyridoxine': 0.05,
            'folic_acid': 0.024, 'vitamin_b12': 0.0, 'biotin': 0.0004, 'choline': 5.7,
            'arginine': 33, 'histidine': 12, 'isoleucine': 16, 'leucine': 34, 'lysine': 26,
            'methionine': 2, 'phenylalanine': 19, 'threonine': 20, 'tryptophan': 6, 'valine': 19,
            'taurine': 0, 'alpha_linolenic_acid': 0.07, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.07, 'omega_6_fatty_acids': 0.09,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去叶蒂，富含维生素C和抗氧化剂', 'storage_notes': '冷藏保存，3-5天内使用',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '西瓜', 'name_en': 'Watermelon', 'category': IngredientCategory.FRUITS,
            'image_filename': 'watermelon.png', 'seasonality': 'summer',
            'calories': 30, 'protein': 0.6, 'fat': 0.2, 'carbohydrate': 7.6, 'fiber': 0.4, 'moisture': 91.0, 'ash': 0.3,
            'calcium': 7, 'phosphorus': 11, 'potassium': 112, 'sodium': 1, 'chloride': 15, 'magnesium': 10,
            'iron': 0.2, 'copper': 0.04, 'manganese': 0.04, 'zinc': 0.1, 'iodine': 0.001, 'selenium': 0.0004,
            'vitamin_a': 569, 'vitamin_d': 0, 'vitamin_e': 0.05, 'vitamin_k': 0.1,
            'thiamine': 0.03, 'riboflavin': 0.02, 'niacin': 0.2, 'pantothenic_acid': 0.22, 'pyridoxine': 0.05,
            'folic_acid': 0.003, 'vitamin_b12': 0.0, 'biotin': 0.0002, 'choline': 4.1,
            'arginine': 59, 'histidine': 7, 'isoleucine': 9, 'leucine': 18, 'lysine': 62,
            'methionine': 7, 'phenylalanine': 15, 'threonine': 27, 'tryptophan': 7, 'valine': 16,
            'taurine': 0, 'alpha_linolenic_acid': 0.05, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.05, 'omega_6_fatty_acids': 0.03,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '去籽，高水分低热量，夏季消暑佳品', 'storage_notes': '整个西瓜室温保存，切开后冷藏',
            'data_source': 'USDA Food Database'
        },
        
        # 谷物类
        {
            'name': '糙米', 'name_en': 'Brown rice', 'category': IngredientCategory.GRAINS,
            'image_filename': 'brown_rice.png', 'seasonality': 'all_year',
            'calories': 370, 'protein': 7.9, 'fat': 2.9, 'carbohydrate': 77.2, 'fiber': 3.5, 'moisture': 10.0, 'ash': 1.5,
            'calcium': 23, 'phosphorus': 333, 'potassium': 223, 'sodium': 7, 'chloride': 11, 'magnesium': 143,
            'iron': 1.5, 'copper': 0.2, 'manganese': 3.7, 'zinc': 2.0, 'iodine': 0.002, 'selenium': 0.023,
            'vitamin_a': 0, 'vitamin_d': 0, 'vitamin_e': 1.2, 'vitamin_k': 1.9,
            'thiamine': 0.4, 'riboflavin': 0.09, 'niacin': 5.1, 'pantothenic_acid': 1.5, 'pyridoxine': 0.51,
            'folic_acid': 0.02, 'vitamin_b12': 0.0, 'biotin': 0.012, 'choline': 30,
            'arginine': 602, 'histidine': 216, 'isoleucine': 320, 'leucine': 654, 'lysine': 303,
            'methionine': 179, 'phenylalanine': 410, 'threonine': 287, 'tryptophan': 101, 'valine': 459,
            'taurine': 0, 'alpha_linolenic_acid': 0.04, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.04, 'omega_6_fatty_acids': 1.2,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '煮熟至软烂，易消化', 'storage_notes': '密封干燥处保存，可保存数月',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '燕麦', 'name_en': 'Oats', 'category': IngredientCategory.GRAINS,
            'image_filename': 'oats.png', 'seasonality': 'all_year',
            'calories': 389, 'protein': 16.9, 'fat': 6.9, 'carbohydrate': 66.3, 'fiber': 10.6, 'moisture': 8.0, 'ash': 1.7,
            'calcium': 54, 'phosphorus': 523, 'potassium': 429, 'sodium': 2, 'chloride': 3, 'magnesium': 177,
            'iron': 4.7, 'copper': 0.63, 'manganese': 4.9, 'zinc': 4.0, 'iodine': 0.008, 'selenium': 0.028,
            'vitamin_a': 0, 'vitamin_d': 0, 'vitamin_e': 0.4, 'vitamin_k': 2.0,
            'thiamine': 0.76, 'riboflavin': 0.14, 'niacin': 0.96, 'pantothenic_acid': 1.35, 'pyridoxine': 0.12,
            'folic_acid': 0.056, 'vitamin_b12': 0.0, 'biotin': 0.02, 'choline': 40.4,
            'arginine': 820, 'histidine': 270, 'isoleucine': 580, 'leucine': 1284, 'lysine': 701,
            'methionine': 312, 'phenylalanine': 930, 'threonine': 575, 'tryptophan': 234, 'valine': 937,
            'taurine': 0, 'alpha_linolenic_acid': 0.11, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.11, 'omega_6_fatty_acids': 2.4,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '煮熟成粥状，高纤维', 'storage_notes': '密封干燥处保存，可保存1年',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '藜麦', 'name_en': 'Quinoa', 'category': IngredientCategory.GRAINS,
            'image_filename': 'quinoa.png', 'seasonality': 'all_year',
            'calories': 368, 'protein': 14.1, 'fat': 6.1, 'carbohydrate': 64.2, 'fiber': 7.0, 'moisture': 13.0, 'ash': 2.4,
            'calcium': 47, 'phosphorus': 457, 'potassium': 563, 'sodium': 5, 'chloride': 8, 'magnesium': 197,
            'iron': 4.6, 'copper': 0.59, 'manganese': 2.0, 'zinc': 3.1, 'iodine': 0.003, 'selenium': 0.0085,
            'vitamin_a': 14, 'vitamin_d': 0, 'vitamin_e': 2.4, 'vitamin_k': 0.0,
            'thiamine': 0.36, 'riboflavin': 0.32, 'niacin': 1.5, 'pantothenic_acid': 0.77, 'pyridoxine': 0.49,
            'folic_acid': 0.184, 'vitamin_b12': 0.0, 'biotin': 0.0234, 'choline': 70.2,
            'arginine': 1091, 'histidine': 407, 'isoleucine': 504, 'leucine': 840, 'lysine': 766,
            'methionine': 309, 'phenylalanine': 593, 'threonine': 421, 'tryptophan': 167, 'valine': 594,
            'taurine': 0, 'alpha_linolenic_acid': 0.26, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.26, 'omega_6_fatty_acids': 2.9,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '完整蛋白质，煮熟后易消化，超级食物', 'storage_notes': '密封干燥处保存，可保存2年',
            'data_source': 'USDA Food Database'
        },
        
        # 乳制品类
        {
            'name': '酸奶(无糖)', 'name_en': 'Plain yogurt', 'category': IngredientCategory.DAIRY,
            'image_filename': 'plain_yogurt.png', 'seasonality': 'all_year',
            'calories': 59, 'protein': 10.0, 'fat': 0.4, 'carbohydrate': 3.6, 'fiber': 0.0, 'moisture': 85.0, 'ash': 0.8,
            'calcium': 110, 'phosphorus': 135, 'potassium': 141, 'sodium': 36, 'chloride': 55, 'magnesium': 11,
            'iron': 0.05, 'copper': 0.009, 'manganese': 0.004, 'zinc': 0.52, 'iodine': 0.025, 'selenium': 0.002,
            'vitamin_a': 27, 'vitamin_d': 0, 'vitamin_e': 0.04, 'vitamin_k': 0.2,
            'thiamine': 0.023, 'riboflavin': 0.27, 'niacin': 0.75, 'pantothenic_acid': 0.39, 'pyridoxine': 0.063,
            'folic_acid': 0.007, 'vitamin_b12': 0.75, 'biotin': 0.0027, 'choline': 15.1,
            'arginine': 270, 'histidine': 220, 'isoleucine': 490, 'leucine': 820, 'lysine': 660,
            'methionine': 220, 'phenylalanine': 400, 'threonine': 380, 'tryptophan': 110, 'valine': 550,
            'taurine': 0, 'alpha_linolenic_acid': 0.011, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.011, 'omega_6_fatty_acids': 0.01,
            'is_safe_for_dogs': True, 'is_safe_for_cats': False, 'is_common_allergen': True,
            'preparation_notes': '选择无糖无添加剂的，适量食用', 'storage_notes': '冷藏保存，开封后3-5天内使用',
            'data_source': 'USDA Food Database'
        },
        
        # 油脂类
        {
            'name': '鱼油', 'name_en': 'Fish oil', 'category': IngredientCategory.OILS,
            'image_filename': 'fish_oil.png', 'seasonality': 'all_year',
            'calories': 902, 'protein': 0.0, 'fat': 100.0, 'carbohydrate': 0.0, 'fiber': 0.0, 'moisture': 0.0, 'ash': 0.0,
            'calcium': 0, 'phosphorus': 0, 'potassium': 0, 'sodium': 0, 'chloride': 0, 'magnesium': 0,
            'iron': 0.0, 'copper': 0.0, 'manganese': 0.0, 'zinc': 0.0, 'iodine': 0.0, 'selenium': 0.0,
            'vitamin_a': 30000, 'vitamin_d': 10000, 'vitamin_e': 20.0, 'vitamin_k': 0.0,
            'thiamine': 0.0, 'riboflavin': 0.0, 'niacin': 0.0, 'pantothenic_acid': 0.0, 'pyridoxine': 0.0,
            'folic_acid': 0.0, 'vitamin_b12': 0.0, 'biotin': 0.0, 'choline': 0.0,
            'arginine': 0, 'histidine': 0, 'isoleucine': 0, 'leucine': 0, 'lysine': 0,
            'methionine': 0, 'phenylalanine': 0, 'threonine': 0, 'tryptophan': 0, 'valine': 0,
            'taurine': 0, 'alpha_linolenic_acid': 1.0, 'eicosapentaenoic_acid': 18.0,
            'docosahexaenoic_acid': 12.0, 'arachidonic_acid': 1.5, 'omega_3_fatty_acids': 30.0, 'omega_6_fatty_acids': 2.0,
            'is_safe_for_dogs': True, 'is_safe_for_cats': True, 'is_common_allergen': False,
            'preparation_notes': '按体重计算用量，每日少量添加', 'storage_notes': '冷藏保存，避光防氧化',
            'data_source': 'Supplement Database'
        },
        
        # 危险食材示例
        {
            'name': '洋葱', 'name_en': 'Onion', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'onion.png', 'seasonality': 'all_year',
            'calories': 40, 'protein': 1.1, 'fat': 0.1, 'carbohydrate': 9.3, 'fiber': 1.7, 'moisture': 89.0, 'ash': 0.4,
            'calcium': 23, 'phosphorus': 29, 'potassium': 146, 'sodium': 4, 'chloride': 6, 'magnesium': 10,
            'iron': 0.2, 'copper': 0.04, 'manganese': 0.13, 'zinc': 0.2, 'iodine': 0.002, 'selenium': 0.0005,
            'vitamin_a': 2, 'vitamin_d': 0, 'vitamin_e': 0.02, 'vitamin_k': 0.4,
            'thiamine': 0.05, 'riboflavin': 0.03, 'niacin': 0.12, 'pantothenic_acid': 0.12, 'pyridoxine': 0.12,
            'folic_acid': 0.019, 'vitamin_b12': 0.0, 'biotin': 0.0009, 'choline': 6.1,
            'arginine': 157, 'histidine': 27, 'isoleucine': 50, 'leucine': 74, 'lysine': 70,
            'methionine': 16, 'phenylalanine': 52, 'threonine': 46, 'tryptophan': 20, 'valine': 50,
            'taurine': 0, 'alpha_linolenic_acid': 0.001, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.001, 'omega_6_fatty_acids': 0.01,
            'is_safe_for_dogs': False, 'is_safe_for_cats': False, 'is_common_allergen': False,
            'preparation_notes': '含有硫化合物，对宠物有毒', 'storage_notes': '干燥处保存',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '大蒜', 'name_en': 'Garlic', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'garlic.png', 'seasonality': 'all_year',
            'calories': 149, 'protein': 6.4, 'fat': 0.5, 'carbohydrate': 33.1, 'fiber': 2.1, 'moisture': 59.0, 'ash': 1.5,
            'calcium': 181, 'phosphorus': 153, 'potassium': 401, 'sodium': 17, 'chloride': 26, 'magnesium': 25,
            'iron': 1.7, 'copper': 0.3, 'manganese': 1.7, 'zinc': 1.2, 'iodine': 0.009, 'selenium': 0.014,
            'vitamin_a': 9, 'vitamin_d': 0, 'vitamin_e': 0.08, 'vitamin_k': 1.7,
            'thiamine': 0.2, 'riboflavin': 0.11, 'niacin': 0.7, 'pantothenic_acid': 0.6, 'pyridoxine': 1.24,
            'folic_acid': 0.003, 'vitamin_b12': 0.0, 'biotin': 0.0017, 'choline': 23.2,
            'arginine': 634, 'histidine': 113, 'isoleucine': 217, 'leucine': 308, 'lysine': 273,
            'methionine': 76, 'phenylalanine': 183, 'threonine': 157, 'tryptophan': 66, 'valine': 291,
            'taurine': 0, 'alpha_linolenic_acid': 0.02, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.02, 'omega_6_fatty_acids': 0.23,
            'is_safe_for_dogs': False, 'is_safe_for_cats': False, 'is_common_allergen': False,
            'preparation_notes': '含有硫化合物，对宠物有毒', 'storage_notes': '干燥处保存',
            'data_source': 'USDA Food Database'
        },
        {
            'name': '巧克力', 'name_en': 'Chocolate', 'category': IngredientCategory.SUPPLEMENTS,
            'image_filename': 'chocolate.png', 'seasonality': 'all_year',
            'calories': 546, 'protein': 4.9, 'fat': 31.3, 'carbohydrate': 59.4, 'fiber': 7.0, 'moisture': 1.0, 'ash': 2.3,
            'calcium': 73, 'phosphorus': 308, 'potassium': 559, 'sodium': 24, 'chloride': 37, 'magnesium': 228,
            'iron': 11.9, 'copper': 1.8, 'manganese': 1.9, 'zinc': 3.3, 'iodine': 0.002, 'selenium': 0.007,
            'vitamin_a': 39, 'vitamin_d': 0, 'vitamin_e': 0.6, 'vitamin_k': 7.3,
            'thiamine': 0.03, 'riboflavin': 0.08, 'niacin': 1.1, 'pantothenic_acid': 0.42, 'pyridoxine': 0.02,
            'folic_acid': 0.012, 'vitamin_b12': 0.3, 'biotin': 0.001, 'choline': 52.1,
            'arginine': 230, 'histidine': 78, 'isoleucine': 190, 'leucine': 310, 'lysine': 190,
            'methionine': 63, 'phenylalanine': 190, 'threonine': 160, 'tryptophan': 58, 'valine': 240,
            'taurine': 0, 'alpha_linolenic_acid': 0.11, 'eicosapentaenoic_acid': 0.0,
            'docosahexaenoic_acid': 0.0, 'arachidonic_acid': 0.0, 'omega_3_fatty_acids': 0.11, 'omega_6_fatty_acids': 1.4,
            'is_safe_for_dogs': False, 'is_safe_for_cats': False, 'is_common_allergen': False,
            'preparation_notes': '含有可可碱，对宠物有毒', 'storage_notes': '阴凉干燥处保存',
            'data_source': 'USDA Food Database'
        }
    ]
    
    added_count = 0
    updated_count = 0

    # 创建或更新食材记录
    for ing_data in basic_ingredients:
        # 检查是否已存在
        existing = Ingredient.query.filter_by(name=ing_data['name']).first()
        if existing and not force_reinit:
            # 如果存在且不是强制重新初始化，则更新
            for key, value in ing_data.items():
                setattr(existing, key, value)
            existing.data_source = "USDA + Pet Nutrition Database"
            existing.last_verified = datetime.utcnow()
            updated_count += 1
        elif not existing or force_reinit:
            # 如果不存在或强制重新初始化，则创建新的
            ingredient = Ingredient(**ing_data)
            ingredient.data_source = "USDA + Pet Nutrition Database"
            ingredient.last_verified = datetime.utcnow()
            db.session.add(ingredient)
            added_count += 1
    
    db.session.commit()
    if force_reinit:
        print(f"✅ 强制重新初始化完成：添加了 {added_count} 种食材")
    else:
        print(f"✅ 更新完成：新增 {added_count} 种，更新 {updated_count} 种食材")
    
    return added_count + updated_count


def init_nutrition_requirements():
    """初始化营养需求标准 (基于AAFCO 2016标准)"""
    
    requirements = [
        # 犬类营养需求
        {
            'pet_type': PetType.DOG,
            'life_stage': LifeStage.ADULT,
            'activity_level': ActivityLevel.MODERATE,
            'min_weight': 1.0, 'max_weight': 100.0,
            'calories_per_kg': 95,  # 成犬维持代谢能
            'protein_min': 18.0, 'fat_min': 5.5,
            'calcium_min': 6000, 'calcium_max': 25000,
            'phosphorus_min': 5000, 'phosphorus_max': 16000,
            'potassium_min': 6000, 'sodium_min': 800, 'sodium_max': 12000,
            'chloride_min': 1200, 'magnesium_min': 400,
            'iron_min': 80, 'iron_max': 3000,
            'copper_min': 7.3, 'copper_max': 250,
            'manganese_min': 5.0, 'manganese_max': 1000,
            'zinc_min': 120, 'zinc_max': 1000,
            'iodine_min': 1.5, 'iodine_max': 50,
            'selenium_min': 0.11, 'selenium_max': 2.0,
            'vitamin_a_min': 5000, 'vitamin_a_max': 250000,
            'vitamin_d_min': 500, 'vitamin_d_max': 5000,
            'vitamin_e_min': 50,
            'thiamine_min': 2.25, 'riboflavin_min': 5.2,
            'niacin_min': 13.6, 'pantothenic_acid_min': 12.0,
            'pyridoxine_min': 1.5, 'folic_acid_min': 0.216,
            'vitamin_b12_min': 28, 'choline_min': 1360,
            'arginine_min': 0.62, 'histidine_min': 0.22,
            'isoleucine_min': 0.45, 'leucine_min': 0.72,
            'lysine_min': 0.63, 'methionine_min': 0.33,
            'phenylalanine_min': 0.45, 'threonine_min': 0.58,
            'tryptophan_min': 0.20, 'valine_min': 0.48,
            'calcium_phosphorus_ratio_min': 1.0,
            'calcium_phosphorus_ratio_max': 2.0,
            'standard_source': 'AAFCO 2016',
            'notes': '成犬维持期营养需求'
        },
        
        # 幼犬营养需求
        {
            'pet_type': PetType.DOG,
            'life_stage': LifeStage.PUPPY_KITTEN,
            'activity_level': ActivityLevel.HIGH,
            'min_weight': 0.5, 'max_weight': 50.0,
            'calories_per_kg': 200,  # 幼犬需要更多热量
            'protein_min': 22.5, 'fat_min': 8.5,
            'calcium_min': 10000, 'calcium_max': 25000,
            'phosphorus_min': 8000, 'phosphorus_max': 16000,
            'potassium_min': 6000, 'sodium_min': 3000, 'sodium_max': 12000,
            'chloride_min': 4500, 'magnesium_min': 400,
            'iron_min': 88, 'iron_max': 3000,
            'copper_min': 12.4, 'copper_max': 250,
            'manganese_min': 7.2, 'manganese_max': 1000,
            'zinc_min': 100, 'zinc_max': 1000,
            'iodine_min': 1.5, 'iodine_max': 50,
            'selenium_min': 0.35, 'selenium_max': 2.0,
            'vitamin_a_min': 5000, 'vitamin_a_max': 250000,
            'vitamin_d_min': 500, 'vitamin_d_max': 5000,
            'vitamin_e_min': 50,
            'thiamine_min': 2.25, 'riboflavin_min': 5.2,
            'niacin_min': 13.6, 'pantothenic_acid_min': 12.0,
            'pyridoxine_min': 1.5, 'folic_acid_min': 0.216,
            'vitamin_b12_min': 28, 'choline_min': 1360,
            'arginine_min': 1.0, 'histidine_min': 0.39,
            'isoleucine_min': 0.71, 'leucine_min': 1.29,
            'lysine_min': 1.2, 'methionine_min': 0.53,
            'phenylalanine_min': 0.83, 'threonine_min': 1.04,
            'tryptophan_min': 0.28, 'valine_min': 0.68,
            'alpha_linolenic_acid_min': 0.08,
            'epa_dha_min': 0.05,
            'calcium_phosphorus_ratio_min': 1.0,
            'calcium_phosphorus_ratio_max': 2.0,
            'standard_source': 'AAFCO 2016',
            'notes': '幼犬生长期营养需求'
        },
        
        # 大型犬幼犬特殊需求
        {
            'pet_type': PetType.DOG,
            'life_stage': LifeStage.LARGE_BREED_PUPPY,
            'activity_level': ActivityLevel.HIGH,
            'min_weight': 15.0, 'max_weight': 80.0,
            'calories_per_kg': 150,  # 大型犬幼犬热量需求相对较低
            'protein_min': 22.5, 'fat_min': 8.5,
            'calcium_min': 10000, 'calcium_max': 18000,  # 钙含量上限更严格
            'phosphorus_min': 8000, 'phosphorus_max': 14000,
            'potassium_min': 6000, 'sodium_min': 3000, 'sodium_max': 12000,
            'chloride_min': 4500, 'magnesium_min': 400,
            'iron_min': 88, 'iron_max': 3000,
            'copper_min': 12.4, 'copper_max': 250,
            'manganese_min': 7.2, 'manganese_max': 1000,
            'zinc_min': 100, 'zinc_max': 1000,
            'iodine_min': 1.5, 'iodine_max': 50,
            'selenium_min': 0.35, 'selenium_max': 2.0,
            'vitamin_a_min': 5000, 'vitamin_a_max': 250000,
            'vitamin_d_min': 500, 'vitamin_d_max': 5000,
            'vitamin_e_min': 50,
            'thiamine_min': 2.25, 'riboflavin_min': 5.2,
            'niacin_min': 13.6, 'pantothenic_acid_min': 12.0,
            'pyridoxine_min': 1.5, 'folic_acid_min': 0.216,
            'vitamin_b12_min': 28, 'choline_min': 1360,
            'arginine_min': 1.0, 'histidine_min': 0.39,
            'isoleucine_min': 0.71, 'leucine_min': 1.29,
            'lysine_min': 1.2, 'methionine_min': 0.53,
            'phenylalanine_min': 0.83, 'threonine_min': 1.04,
            'tryptophan_min': 0.28, 'valine_min': 0.68,
            'alpha_linolenic_acid_min': 0.08,
            'epa_dha_min': 0.05,
            'calcium_phosphorus_ratio_min': 1.0,
            'calcium_phosphorus_ratio_max': 1.8,  # 更严格的钙磷比
            'standard_source': 'AAFCO 2016',
            'notes': '大型犬幼犬特殊营养需求，控制钙磷比例防止骨骼发育问题'
        },
        
        # 猫咪成年营养需求
        {
            'pet_type': PetType.CAT,
            'life_stage': LifeStage.ADULT,
            'activity_level': ActivityLevel.MODERATE,
            'min_weight': 2.0, 'max_weight': 12.0,
            'calories_per_kg': 100,  # 成猫维持代谢能
            'protein_min': 26.0, 'fat_min': 9.0,
            'calcium_min': 6000, 'calcium_max': 25000,
            'phosphorus_min': 5000, 'phosphorus_max': 16000,
            'potassium_min': 6000, 'sodium_min': 800, 'sodium_max': 12000,
            'chloride_min': 1900, 'magnesium_min': 400, 
            'iron_min': 80, 'iron_max': 3000,
            'copper_min': 5.0, 'copper_max': 250,
            'manganese_min': 7.6, 'manganese_max': 1000,
            'zinc_min': 75, 'zinc_max': 2000,
            'iodine_min': 1.8, 'iodine_max': 50,
            'selenium_min': 0.1, 'selenium_max': 2.0,
            'vitamin_a_min': 3332, 'vitamin_a_max': 333300,
            'vitamin_d_min': 280, 'vitamin_d_max': 30000,
            'vitamin_e_min': 40,
            'thiamine_min': 5.6, 'riboflavin_min': 4.0,
            'niacin_min': 60.0, 'pantothenic_acid_min': 5.75,
            'pyridoxine_min': 2.5, 'folic_acid_min': 0.8,
            'vitamin_b12_min': 20, 'choline_min': 2550,
            'arginine_min': 1.04, 'histidine_min': 0.33,
            'isoleucine_min': 0.56, 'leucine_min': 1.28,
            'lysine_min': 0.83, 'methionine_min': 0.43,
            'phenylalanine_min': 0.43, 'threonine_min': 0.73,
            'tryptophan_min': 0.25, 'valine_min': 0.64,
            'taurine_min': 400,  # 猫咪特需
            'alpha_linolenic_acid_min': 0.02,
            'arachidonic_acid_min': 0.02,  # 猫咪特需
            'calcium_phosphorus_ratio_min': 1.0,
            'calcium_phosphorus_ratio_max': 2.0,
            'standard_source': 'AAFCO 2016',
            'notes': '成猫维持期营养需求，包含猫咪特需的牛磺酸和花生四烯酸'
        },
        
        # 幼猫营养需求
        {
            'pet_type': PetType.CAT,
            'life_stage': LifeStage.PUPPY_KITTEN,
            'activity_level': ActivityLevel.HIGH,
            'min_weight': 0.1, 'max_weight': 8.0,
            'calories_per_kg': 250,  # 幼猫需要更多热量
            'protein_min': 30.0, 'fat_min': 9.0,
            'calcium_min': 10000, 'calcium_max': 25000,
            'phosphorus_min': 8000, 'phosphorus_max': 16000,
            'potassium_min': 6000, 'sodium_min': 1600, 'sodium_max': 12000,
            'chloride_min': 2400, 'magnesium_min': 400,
            'iron_min': 80, 'iron_max': 3000,
            'copper_min': 8.4, 'copper_max': 250,
            'manganese_min': 7.6, 'manganese_max': 1000,
            'zinc_min': 75, 'zinc_max': 2000,
            'iodine_min': 1.8, 'iodine_max': 50,
            'selenium_min': 0.1, 'selenium_max': 2.0,
            'vitamin_a_min': 6668, 'vitamin_a_max': 333300,
            'vitamin_d_min': 280, 'vitamin_d_max': 30000,
            'vitamin_e_min': 40,
            'thiamine_min': 5.6, 'riboflavin_min': 4.0,
            'niacin_min': 60.0, 'pantothenic_acid_min': 5.75,
            'pyridoxine_min': 2.5, 'folic_acid_min': 0.8,
            'vitamin_b12_min': 20, 'choline_min': 2550,
            'arginine_min': 1.83, 'histidine_min': 0.53,
            'isoleucine_min': 0.79, 'leucine_min': 1.7,
            'lysine_min': 1.2, 'methionine_min': 0.62,
            'phenylalanine_min': 0.52, 'threonine_min': 0.96,
            'tryptophan_min': 0.25, 'valine_min': 0.78,
            'taurine_min': 400,  # 猫咪特需
            'alpha_linolenic_acid_min': 0.02,
            'epa_dha_min': 0.012,
            'arachidonic_acid_min': 0.02,  # 猫咪特需
            'calcium_phosphorus_ratio_min': 1.0,
            'calcium_phosphorus_ratio_max': 2.0,
            'standard_source': 'AAFCO 2016',
            'notes': '幼猫生长期营养需求，蛋白质需求更高'
        }
    ]
    
    # 创建营养需求记录
    for req_data in requirements:
        # 检查是否已存在
        existing = db.session.query(NutritionRequirement).filter_by(
            pet_type=req_data['pet_type'],
            life_stage=req_data['life_stage'],
            activity_level=req_data['activity_level']
        ).first()
        
        if not existing:
            requirement = NutritionRequirement(**req_data)
            db.session.add(requirement)
    
    db.session.commit()
    print(f"已添加 {len(requirements)} 套营养需求标准")


def init_database(force_reinit=False):
    """初始化数据库的主函数"""
    try:
        # 创建Flask应用上下文
        app = create_app()
        
        with app.app_context():
            if force_reinit:
                print("🔄 开始强制重新初始化营养数据库...")
            else:
                print("📝 开始更新营养数据库...")
            
            # 创建所有数据库表
            db.create_all()
            print("数据库表创建完成")
            
            # 初始化食材数据
            print("正在添加基础食材...")
            ingredient_count = init_basic_ingredients(force_reinit=force_reinit)
            
            # 初始化营养需求标准
            if force_reinit:
                print("📊 正在添加营养需求标准...")
                init_nutrition_requirements()
            
            print("=" * 50)
            print("🎉 营养数据库处理完成！")
            print(f"📋 处理了 {ingredient_count} 种食材")
            print("=" * 50)
            
            return True
            
    except Exception as e:
        print(f"❌ 初始化过程中发生错误: {e}")
        if 'db' in locals():
            db.session.rollback()
        return False

def main():
    """主函数，支持命令行参数"""
    import sys
    
    force_reinit = '--force' in sys.argv or '-f' in sys.argv
    
    if force_reinit:
        confirm = input("⚠️  确认要强制重新初始化所有食材数据吗？这将删除现有数据！(y/N): ")
        if confirm.lower() != 'y':
            print("❌ 操作已取消")
            return False
    
    return init_database(force_reinit=force_reinit)


if __name__ == "__main__":
    print("宠物食谱网站 - 数据库初始化/更新工具")
    print("=" * 40)
    print("使用方法:")
    print("  python init_nutrition_data.py        # 更新模式（保留现有数据）")
    print("  python init_nutrition_data.py --force # 强制重新初始化（删除现有数据）")
    print("=" * 40)
    
    if main():
        print("\n🎉 操作成功！你现在可以启动应用了。")
        print("\n启动命令:")
        print("python run.py")
        print("\n然后在浏览器中访问: http://localhost:5001")
    else:
        print("\n❌ 操作失败，请检查错误信息。")