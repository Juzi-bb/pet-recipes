// static/js/nutritionCalculator.js
/**
 * 营养计算前端集成
 * 提供实时营养计算和可视化功能
 */

class NutritionCalculator {
    constructor() {
        this.selectedIngredients = new Map(); // ingredient_id -> {ingredient, weight}
        this.currentNutritionPlan = null;
        this.currentPetId = null;
        this.nutritionChart = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadNutritionPlans();
    }
    
    bindEvents() {
        // 营养方案选择
        $(document).on('change', '#nutrition-plan-select', (e) => {
            this.currentNutritionPlan = e.target.value;
            this.suggestWeights();
        });
        
        // 食材选择
        $(document).on('change', '.ingredient-checkbox', (e) => {
            const ingredientId = parseInt(e.target.value);
            if (e.target.checked) {
                this.addIngredient(ingredientId);
            } else {
                this.removeIngredient(ingredientId);
            }
        });
        
        // 重量调整
        $(document).on('input', '.weight-input', (e) => {
            const ingredientId = parseInt(e.target.dataset.ingredientId);
            const weight = parseFloat(e.target.value) || 0;
            this.updateIngredientWeight(ingredientId, weight);
        });
        
        // 一键分配重量按钮
        $(document).on('click', '#suggest-weights-btn', () => {
            this.suggestWeights();
        });
        
        // 宠物选择
        $(document).on('change', '#pet-select', (e) => {
            this.currentPetId = e.target.value;
            this.loadNutritionPlans();
        });
    }
    
    async loadNutritionPlans() {
        try {
            const url = this.currentPetId
                ? `/api/nutrition/plans?pet_id=${this.currentPetId}`
                : '/api/nutrition/plans';
                
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.plans) {
                this.renderNutritionPlans(data.plans);
            }
        } catch (error) {
            console.error('加载营养方案失败:', error);
            this.showNotification('加载营养方案失败', 'error');
        }
    }
    
    renderNutritionPlans(plans) {
        const select = $('#nutrition-plan-select');
        select.empty().append('<option value="">请选择营养方案</option>');
        
        // 推荐方案
        const recommended = plans.filter(p => p.is_recommended);
        if (recommended.length > 0) {
            const recommendedGroup = $('<optgroup label="推荐方案"></optgroup>');
            recommended.forEach(plan => {
                recommendedGroup.append(`
                    <option value="${plan.id}" data-description="${plan.description}">
                        ${plan.name}
                    </option>
                `);
            });
            select.append(recommendedGroup);
        }
        
        // 其他方案
        const others = plans.filter(p => !p.is_recommended);
        if (others.length > 0) {
            const othersGroup = $('<optgroup label="其他方案"></optgroup>');
            others.forEach(plan => {
                othersGroup.append(`
                    <option value="${plan.id}" data-description="${plan.description}">
                        ${plan.name}
                    </option>
                `);
            });
            select.append(othersGroup);
        }
        
        // 显示方案描述
        select.on('change', (e) => {
            const selectedOption = e.target.selectedOptions[0];
            const description = selectedOption ? selectedOption.dataset.description : '';
            $('#plan-description').text(description);
        });
    }
    
    addIngredient(ingredientId) {
        // 获取食材信息（从页面上的食材卡片）
        const ingredientCard = $(`.ingredient-card[data-ingredient-id="${ingredientId}"]`);
        const ingredientData = {
            id: ingredientId,
            name: ingredientCard.find('.ingredient-name').text(),
            category: ingredientCard.data('category'),
            calories: parseFloat(ingredientCard.data('calories')) || 0,
            protein: parseFloat(ingredientCard.data('protein')) || 0,
            fat: parseFloat(ingredientCard.data('fat')) || 0
        };
        
        this.selectedIngredients.set(ingredientId, {
            ingredient: ingredientData,
            weight: 0
        });
        
        this.renderSelectedIngredients();
        this.calculateNutrition();
    }
    
    removeIngredient(ingredientId) {
        this.selectedIngredients.delete(ingredientId);
        this.renderSelectedIngredients();
        this.calculateNutrition();
    }
    
    updateIngredientWeight(ingredientId, weight) {
        if (this.selectedIngredients.has(ingredientId)) {
            this.selectedIngredients.get(ingredientId).weight = weight;
            this.calculateNutrition();
        }
    }
    
    renderSelectedIngredients() {
        const container = $('#selected-ingredients-list');
        container.empty();
        
        if (this.selectedIngredients.size === 0) {
            container.html('<p class="text-muted">请选择食材</p>');
            return;
        }
        
        this.selectedIngredients.forEach((data, ingredientId) => {
            const { ingredient, weight } = data;
            container.append(`
                <div class="ingredient-weight-item mb-3 p-3 border rounded">
                    <div class="row align-items-center">
                        <div class="col-md-4">
                            <span class="fw-bold">${ingredient.name}</span>
                            <small class="text-muted d-block">${this.getCategoryName(ingredient.category)}</small>
                        </div>
                        <div class="col-md-3">
                            <div class="input-group">
                                <input type="number" 
                                    class="form-control weight-input" 
                                    data-ingredient-id="${ingredientId}"
                                    value="${weight}"
                                    min="0"
                                    max="1000"
                                    placeholder="重量">
                                <span class="input-group-text">g</span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted">
                                热量: ${(ingredient.calories * weight / 100).toFixed(1)} kcal<br>
                                蛋白质: ${(ingredient.protein * weight / 100).toFixed(1)}g
                            </small>
                        </div>
                        <div class="col-md-2">
                            <button type="button" 
                                    class="btn btn-outline-danger btn-sm"
                                    onclick="nutritionCalculator.removeIngredient(${ingredientId})">
                                移除
                            </button>
                        </div>
                    </div>
                </div>
            `);
        });
    }
    
    async suggestWeights() {
        if (!this.currentNutritionPlan || this.selectedIngredients.size === 0) {
            this.showNotification('请选择营养方案和食材', 'warning');
            return;
        }
        
        try {
            const ingredientIds = Array.from(this.selectedIngredients.keys());
            const response = await fetch('/api/nutrition/suggest-weights', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ingredient_ids: ingredientIds,
                    nutrition_plan_id: this.currentNutritionPlan,
                    pet_id: this.currentPetId,
                    total_weight: 200  // 默认200g
                })
            });
            
            const data = await response.json();
            
            if (data.suggested_weights) {
                // 更新重量
                data.suggested_weights.forEach(item => {
                    if (this.selectedIngredients.has(item.ingredient_id)) {
                        this.selectedIngredients.get(item.ingredient_id).weight = item.suggested_weight;
                    }
                });
                
                this.renderSelectedIngredients();
                this.calculateNutrition();
                this.showNotification('重量分配完成', 'success');
            }
        } catch (error) {
            console.error('推荐重量失败:', error);
            this.showNotification('推荐重量失败', 'error');
        }
    }
    
    async calculateNutrition() {
        if (this.selectedIngredients.size === 0) {
            this.clearNutritionDisplay();
            return;
        }
        
        const ingredients = Array.from(this.selectedIngredients.values()).map(data => ({
            id: data.ingredient.id,
            weight: data.weight
        }));
        
        try {
            const response = await fetch('/api/nutrition/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ingredients: ingredients,
                    pet_id: this.currentPetId
                })
            });
            
            const data = await response.json();
            
            if (data.total_nutrition) {
                this.displayNutritionResults(data);
                this.updateNutritionChart(data);
            }
        } catch (error) {
            console.error('营养计算失败:', error);
            this.showNotification('营养计算失败', 'error');
        }
    }
    
    displayNutritionResults(data) {
        const { total_nutrition, nutrition_ratios, nutrition_assessment } = data;
        
        // 显示总营养
        $('#total-weight').text(total_nutrition.total_weight.toFixed(1));
        $('#total-calories').text(total_nutrition.calories.toFixed(1));
        $('#total-protein').text(total_nutrition.protein.toFixed(1));
        $('#total-fat').text(total_nutrition.fat.toFixed(1));
        $('#calcium-phosphorus-ratio').text(total_nutrition.calcium_phosphorus_ratio.toFixed(2));
        
        // 显示营养比例
        if (nutrition_ratios) {
            $('#protein-percent').text(nutrition_ratios.protein_percent);
            $('#fat-percent').text(nutrition_ratios.fat_percent);
            $('#carb-percent').text(nutrition_ratios.carbohydrate_percent);
        }
        
        // 显示营养评估
        this.displayNutritionAssessment(nutrition_assessment);
    }
    
    displayNutritionAssessment(assessment) {
        const container = $('#nutrition-assessment');
        container.empty();
        
        // 总体状态
        const statusClass = {
            'good': 'success',
            'fair': 'warning', 
            'poor': 'danger',
            'unknown': 'secondary'
        }[assessment.overall_status] || 'secondary';
        
        const statusText = {
            'good': '营养均衡',
            'fair': '基本达标',
            'poor': '需要改进',
            'unknown': '评估中'
        }[assessment.overall_status] || '未知';
        
        container.append(`
            <div class="alert alert-${statusClass} mb-3">
                <strong>营养评估: ${statusText}</strong>
            </div>
        `);
        
        // 营养缺陷
        if (assessment.deficiencies && assessment.deficiencies.length > 0) {
            const deficienciesHtml = assessment.deficiencies.map(def => `
                <li class="list-group-item list-group-item-danger">
                    <strong>${this.getNutrientName(def.nutrient)}</strong> 不足 
                    (当前: ${def.current.toFixed(1)}%, 建议: ≥${def.recommended_min}%)
                </li>
            `).join('');
            
            container.append(`
                <div class="mb-3">
                    <h6 class="text-danger">营养不足:</h6>
                    <ul class="list-group">
                        ${deficienciesHtml}
                    </ul>
                </div>
            `);
        }
        
        // 营养过量
        if (assessment.excesses && assessment.excesses.length > 0) {
            const excessesHtml = assessment.excesses.map(exc => `
                <li class="list-group-item list-group-item-warning">
                    <strong>${this.getNutrientName(exc.nutrient)}</strong> 过量
                    (当前: ${exc.current.toFixed(1)}%, 建议: ≤${exc.recommended_max}%)
                </li>
            `).join('');
            
            container.append(`
                <div class="mb-3">
                    <h6 class="text-warning">营养过量:</h6>
                    <ul class="list-group">
                        ${excessesHtml}
                    </ul>
                </div>
            `);
        }
        
        // 建议
        if (assessment.recommendations && assessment.recommendations.length > 0) {
            const recommendationsHtml = assessment.recommendations.map(rec => `
                <li class="list-group-item list-group-item-info">${rec}</li>
            `).join('');
            
            container.append(`
                <div class="mb-3">
                    <h6 class="text-info">改进建议:</h6>
                    <ul class="list-group">
                        ${recommendationsHtml}
                    </ul>
                </div>
            `);
        }
    }
    
    updateNutritionChart(data) {
        const { nutrition_ratios, nutrition_assessment } = data;
        
        if (!nutrition_ratios) {
            this.clearChart();
            return;
        }
        
        // 销毁现有图表
        if (this.nutritionChart) {
            this.nutritionChart.destroy();
        }
        
        // 创建新图表
        this.createNutritionChart(nutrition_ratios, nutrition_assessment);
    }
    
    createNutritionChart(nutritionRatios, assessment) {
        const ctx = document.getElementById('nutrition-chart').getContext('2d');
        
        // 主题色配置
        const themeColors = {
            primary: '#510B0B',
            secondary: '#B82F0D', 
            accent: '#5580AD',
            neutral: '#A1B4B2',
            light: '#EDBF9D',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545'
        };
        
        // 准备数据
        const chartData = this.prepareChartData(nutritionRatios, assessment, themeColors);
        
        // 创建横向柱状图
        this.nutritionChart = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                indexAxis: 'y', // 横向柱状图
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const nutrient = context.label;
                                const actual = context.parsed.x;
                                const target = this.getNutrientTarget(nutrient);
                                
                                let label = `${nutrient}: ${actual.toFixed(1)}%`;
                                if (target) {
                                    label += ` (目标: ${target.min}-${target.max}%)`;
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 50, // 最大50%
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(161, 180, 178, 0.2)'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    }
                },
                elements: {
                    bar: {
                        borderRadius: 8,
                        borderSkipped: false
                    }
                },
                animation: {
                    duration: 800,
                    easing: 'easeOutQuart'
                }
            }
        });
    }
    
    prepareChartData(nutritionRatios, assessment, themeColors) {
        const nutrients = [
            { key: 'protein_percent', label: '蛋白质', target: { min: 18, max: 35 } },
            { key: 'fat_percent', label: '脂肪', target: { min: 5.5, max: 20 } },
            { key: 'carbohydrate_percent', label: '碳水化合物', target: { min: 0, max: 25 } },
            { key: 'fiber_percent', label: '纤维', target: { min: 1, max: 8 } }
        ];
        
        const labels = [];
        const data = [];
        const backgroundColor = [];
        const borderColor = [];
        
        nutrients.forEach(nutrient => {
            const value = nutritionRatios[nutrient.key] || 0;
            const status = this.getNutrientStatus(value, nutrient.target, assessment);
            
            labels.push(nutrient.label);
            data.push(value);
            
            // 根据营养状态设置颜色
            switch (status) {
                case 'deficient':
                    backgroundColor.push('rgba(220, 53, 69, 0.7)'); // 缺乏 - 红色
                    borderColor.push('rgba(220, 53, 69, 1)');
                    break;
                case 'excessive':
                    backgroundColor.push('rgba(255, 193, 7, 0.7)'); // 过量 - 黄色
                    borderColor.push('rgba(255, 193, 7, 1)');
                    break;
                case 'optimal':
                    backgroundColor.push('rgba(40, 167, 69, 0.7)'); // 最优 - 绿色
                    borderColor.push('rgba(40, 167, 69, 1)');
                    break;
                default:
                    backgroundColor.push('rgba(161, 180, 178, 0.7)'); // 默认 - 灰色
                    borderColor.push('rgba(161, 180, 178, 1)');
            }
        });
        
        return {
            labels: labels,
            datasets: [{
                label: '营养比例',
                data: data,
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 2
            }]
        };
    }
    
    getNutrientStatus(value, target, assessment) {
        // 检查营养评估中的缺陷和过量
        if (assessment.deficiencies) {
            const deficiency = assessment.deficiencies.find(d =>
                (target.min && value < target.min) ||
                (d.nutrient === 'protein' && target.min === 18) ||
                (d.nutrient === 'fat' && target.min === 5.5)
            );
            if (deficiency) return 'deficient';
        }
        
        if (assessment.excesses) {
            const excess = assessment.excesses.find(e =>
                (target.max && value > target.max) ||
                (e.nutrient === 'protein' && target.max === 35) ||
                (e.nutrient === 'fat' && target.max === 20)
            );
            if (excess) return 'excessive';
        }
        
        // 检查是否在理想范围内
        if (target.min && target.max) {
            if (value >= target.min && value <= target.max) {
                return 'optimal';
            }
        }
        
        return 'unknown';
    }
    
    getNutrientTarget(nutrientLabel) {
        const targets = {
            '蛋白质': { min: 18, max: 35 },
            '脂肪': { min: 5.5, max: 20 },
            '碳水化合物': { min: 0, max: 25 },
            '纤维': { min: 1, max: 8 }
        };
        return targets[nutrientLabel];
    }
    
    clearChart() {
        if (this.nutritionChart) {
            this.nutritionChart.destroy();
            this.nutritionChart = null;
        }
        
        // 显示空状态
        const ctx = document.getElementById('nutrition-chart').getContext('2d');
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        
        // 添加提示文本
        ctx.fillStyle = '#A1B4B2';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('选择食材后显示图表', ctx.canvas.width / 2, ctx.canvas.height / 2);
    }
    
    clearNutritionDisplay() {
        $('#total-weight, #total-calories, #total-protein, #total-fat, #calcium-phosphorus-ratio').text('0');
        $('#protein-percent, #fat-percent, #carb-percent').text('0');
        $('#nutrition-assessment').empty();
    }
    
    getCategoryName(category) {
        const categoryNames = {
            'red_meat': '红肉',
            'white_meat': '白肉',
            'fish': '鱼类',
            'organs': '内脏',
            'vegetables': '蔬菜',
            'fruits': '水果',
            'grains': '谷物',
            'dairy': '乳制品',
            'supplements': '营养补充剂',
            'oils': '油脂类'
        };
        return categoryNames[category] || category;
    }
    
    getNutrientName(nutrient) {
        const nutrientNames = {
            'protein': '蛋白质',
            'fat': '脂肪',
            'carbohydrate': '碳水化合物',
            'calcium': '钙',
            'phosphorus': '磷'
        };
        return nutrientNames[nutrient] || nutrient;
    }
    
    showNotification(message, type = 'info') {
        // 简单的通知实现，您可以根据需要使用更复杂的通知库
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                style="top: 20px; right: 20px; z-index: 1050; min-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(notification);
        
        // 自动消失
        setTimeout(() => {
            notification.alert('close');
        }, 3000);
    }
}

// 全局实例
let nutritionCalculator;

$(document).ready(function() {
    nutritionCalculator = new NutritionCalculator();
});