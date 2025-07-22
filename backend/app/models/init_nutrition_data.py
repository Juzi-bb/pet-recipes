"""
营养数据初始化脚本
基于AAFCO标准创建基础的食材数据和营养需求标准
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ingredient_model import Ingredient, IngredientCategory
from nutrition_requirements_model import NutritionRequirement, PetType, LifeStage, ActivityLevel
from datetime import datetime

def init_basic_ingredients(session):
    """初始化基础食材数据"""
    
    # 基础食材数据 (营养成分基于USDA数据库和宠物食品资料)
    basic_ingredients = [
        # 红肉类
        {
            'name': '牛肉(瘦)', 'name_en': 'Beef (lean)', 'category': IngredientCategory.RED_MEAT,
            'image_filename': 'beef_lean.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'lamb.jpg', 'seasonality': 'spring,winter',
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
            'image_filename': 'pork.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'chicken_breast.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'chicken_thigh.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'turkey.jpg', 'seasonality': 'autumn,winter',
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
            'image_filename': 'duck.jpg', 'seasonality': 'autumn,winter',
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
        
        # 鱼类
        {
            'name': '三文鱼', 'name_en': 'Salmon', 'category': IngredientCategory.FISH,
            'image_filename': 'salmon.jpg', 'seasonality': 'spring,summer,autumn',
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
            'image_filename': 'cod.jpg', 'seasonality': 'winter,spring',
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
            'image_filename': 'tuna.jpg', 'seasonality': 'summer,autumn',
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
            'image_filename': 'sardine.jpg', 'seasonality': 'summer,autumn',
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
        
        # 内脏类
        {
            'name': '鸡肝', 'name_en': 'Chicken liver', 'category': IngredientCategory.ORGANS,
            'image_filename': 'chicken_liver.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'beef_liver.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'chicken_heart.jpg', 'seasonality': 'all_year',
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
        
        # 蔬菜类
        {
            'name': '胡萝卜', 'name_en': 'Carrot', 'category': IngredientCategory.VEGETABLES,
            'image_filename': 'carrot.jpg', 'seasonality': 'autumn,winter',
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
            'image_filename': 'broccoli.jpg', 'seasonality': 'autumn,winter,spring',
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
            'image_filename': 'pumpkin.jpg', 'seasonality': 'autumn',
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
            'image_filename': 'sweet_potato.jpg', 'seasonality': 'autumn',
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
            'image_filename': 'spinach.jpg', 'seasonality': 'spring,autumn',
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
        
        # 水果类
        {
            'name': '苹果', 'name_en': 'Apple', 'category': IngredientCategory.FRUITS,
            'image_filename': 'apple.jpg', 'seasonality': 'autumn',
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
            'image_filename': 'blueberry.jpg', 'seasonality': 'summer',
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
            'image_filename': 'banana.jpg', 'seasonality': 'all_year',
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
        
        # 谷物类
        {
            'name': '糙米', 'name_en': 'Brown rice', 'category': IngredientCategory.GRAINS,
            'image_filename': 'brown_rice.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'oats.jpg', 'seasonality': 'all_year',
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
        
        # 乳制品类
        {
            'name': '酸奶(无糖)', 'name_en': 'Plain yogurt', 'category': IngredientCategory.DAIRY,
            'image_filename': 'plain_yogurt.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'fish_oil.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'onion.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'garlic.jpg', 'seasonality': 'all_year',
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
            'image_filename': 'chocolate.jpg', 'seasonality': 'all_year',
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
    
    # 创建食材记录
    for ing_data in basic_ingredients:
        # 检查是否已存在
        existing = session.query(Ingredient).filter_by(name=ing_data['name']).first()
        if not existing:
            ingredient = Ingredient(**ing_data)
            ingredient.data_source = "USDA + Pet Nutrition Database"
            ingredient.last_verified = datetime.utcnow()
            session.add(ingredient)
    
    session.commit()
    print(f"已添加 {len(basic_ingredients)} 种基础食材")


def init_nutrition_requirements(session):
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
        existing = session.query(NutritionRequirement).filter_by(
            pet_type=req_data['pet_type'],
            life_stage=req_data['life_stage'],
            activity_level=req_data['activity_level']
        ).first()
        
        if not existing:
            requirement = NutritionRequirement(**req_data)
            session.add(requirement)
    
    session.commit()
    print(f"已添加 {len(requirements)} 套营养需求标准")


def main():
    """主函数 - 初始化营养数据库"""
    # 创建数据库连接
    engine = create_engine('sqlite:///pet_nutrition.db')  # 根据你的数据库配置修改
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("开始初始化营养数据库...")
        
        # 初始化食材数据
        print("正在添加基础食材...")
        init_basic_ingredients(session)
        
        # 初始化营养需求标准
        print("正在添加营养需求标准...")
        init_nutrition_requirements(session)
        
        print("营养数据库初始化完成！")
        
    except Exception as e:
        print(f"初始化过程中发生错误: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()