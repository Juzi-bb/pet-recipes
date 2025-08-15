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
            this.showNotification('Failed to load nutrition plans', 'error');
        }
    }
    
    renderNutritionPlans(plans) {
        const select = $('#nutrition-plan-select');
        select.empty().append('<option value="">Select nutrition plan</option>');
        
        // 推荐方案
        const recommended = plans.filter(p => p.is_recommended);
        if (recommended.length > 0) {
            const recommendedGroup = $('<optgroup label="Recommended Plans"></optgroup>');
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
            const othersGroup = $('<optgroup label="Other Plans"></optgroup>');
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
            container.html('<p class="text-muted">Please select ingredients</p>');
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
                                    placeholder="Weight">
                                <span class="input-group-text">g</span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted">
                                Calories: ${(ingredient.calories * weight / 100).toFixed(1)} kcal<br>
                                Protein: ${(ingredient.protein * weight / 100).toFixed(1)}g
                            </small>
                        </div>
                        <div class="col-md-2">
                            <button type="button" 
                                    class="btn btn-outline-danger btn-sm"
                                    onclick="nutritionCalculator.removeIngredient(${ingredientId})">
                                Remove
                            </button>
                        </div>
                    </div>
                </div>
            `);
        });
    }
    
    async suggestWeights() {
        if (!this.currentNutritionPlan || this.selectedIngredients.size === 0) {
            this.showNotification('Please select nutrition plan and ingredients', 'warning');
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
                this.showNotification('Weight allocation completed', 'success');
            }
        } catch (error) {
            console.error('推荐重量失败:', error);
            this.showNotification('Failed to suggest weights', 'error');
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
            this.showNotification('Failed to calculate nutrition', 'error');
        }
    }
    
    displayNutritionResults(data) {
        const { total_nutrition, nutrition_ratios, nutrition_analysis } = data;
        
        // 显示总营养
        $('#total-weight').text(total_nutrition.total_weight.toFixed(1));
        $('#total-calories').text(total_nutrition.calories.toFixed(1));
        $('#total-protein').text(total_nutrition.protein.toFixed(1));
        $('#total-fat').text(total_nutrition.fat.toFixed(1));
        
        // 计算钙磷比
        if (total_nutrition.calcium > 0 && total_nutrition.phosphorus > 0) {
            const caPhosRatio = total_nutrition.calcium / total_nutrition.phosphorus;
            $('#calcium-phosphorus-ratio').text(caPhosRatio.toFixed(2));
        } else {
            $('#calcium-phosphorus-ratio').text('N/A');
        }
        
        // 显示营养比例
        if (nutrition_ratios) {
            $('#protein-percent').text(nutrition_ratios.protein_percent);
            $('#fat-percent').text(nutrition_ratios.fat_percent);
            $('#carb-percent').text(nutrition_ratios.carbohydrate_percent);
        }
        
        // 显示营养评估
        this.displayNutritionAssessment(nutrition_analysis);
    }
    
    displayNutritionAssessment(analysis) {
        const container = $('#nutrition-assessment');
        container.empty();
        
        if (!analysis) {
            return;
        }
        
        // 总体状态
        const statusClass = {
            'excellent': 'success',
            'good': 'success', 
            'needs_improvement': 'warning',
            'calculated': 'info'
        }[analysis.status] || 'secondary';
        
        const statusText = {
            'excellent': 'Excellent Balance',
            'good': 'Good Balance',
            'needs_improvement': 'Needs Improvement',
            'calculated': 'Calculated'
        }[analysis.status] || 'Unknown';
        
        container.append(`
            <div class="alert alert-${statusClass} mb-3">
                <strong>Nutrition Assessment: ${statusText}</strong>
                ${analysis.score ? `<span class="float-end">Score: ${analysis.score}/100</span>` : ''}
            </div>
        `);
        
        // 警告信息
        if (analysis.warnings && analysis.warnings.length > 0) {
            const warningsHtml = analysis.warnings.map(warning => `
                <li class="list-group-item list-group-item-warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>${warning}
                </li>
            `).join('');
            
            container.append(`
                <div class="mb-3">
                    <h6 class="text-warning">Warnings:</h6>
                    <ul class="list-group">
                        ${warningsHtml}
                    </ul>
                </div>
            `);
        }
        
        // 建议
        if (analysis.recommendations && analysis.recommendations.length > 0) {
            const recommendationsHtml = analysis.recommendations.map(rec => `
                <li class="list-group-item list-group-item-info">
                    <i class="bi bi-lightbulb me-2"></i>${rec}
                </li>
            `).join('');
            
            container.append(`
                <div class="mb-3">
                    <h6 class="text-info">Recommendations:</h6>
                    <ul class="list-group">
                        ${recommendationsHtml}
                    </ul>
                </div>
            `);
        }
    }
    
    updateNutritionChart(data) {
        const { nutrition_ratios, nutrition_analysis } = data;
        
        if (!nutrition_ratios) {
            this.clearChart();
            return;
        }
        
        // 销毁现有图表
        if (this.nutritionChart) {
            this.nutritionChart.destroy();
        }
        
        // 创建新图表
        this.createNutritionChart(nutrition_ratios, nutrition_analysis);
    }
    
    createNutritionChart(nutritionRatios, analysis) {
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
        const chartData = this.prepareChartData(nutritionRatios, analysis, themeColors);
        
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
                                    label += ` (Target: ${target.min}-${target.max}%)`;
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
    
    prepareChartData(nutritionRatios, analysis, themeColors) {
        const nutrients = [
            { key: 'protein_percent', label: 'Protein', target: { min: 18, max: 35 } },
            { key: 'fat_percent', label: 'Fat', target: { min: 5.5, max: 20 } },
            { key: 'carbohydrate_percent', label: 'Carbohydrate', target: { min: 0, max: 25 } },
            { key: 'fiber_percent', label: 'Fiber', target: { min: 1, max: 8 } }
        ];
        
        const labels = [];
        const data = [];
        const backgroundColor = [];
        const borderColor = [];
        
        nutrients.forEach(nutrient => {
            const value = nutritionRatios[nutrient.key] || 0;
            const status = this.getNutrientStatus(value, nutrient.target, analysis);
            
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
                label: 'Nutrition Ratio',
                data: data,
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 2
            }]
        };
    }
    
    getNutrientStatus(value, target, analysis) {
        // 简化的状态判断逻辑
        if (target.min && value < target.min) {
            return 'deficient';
        }
        if (target.max && value > target.max) {
            return 'excessive';
        }
        if (target.min && target.max && value >= target.min && value <= target.max) {
            return 'optimal';
        }
        return 'unknown';
    }
    
    getNutrientTarget(nutrientLabel) {
        const targets = {
            'Protein': { min: 18, max: 35 },
            'Fat': { min: 5.5, max: 20 },
            'Carbohydrate': { min: 0, max: 25 },
            'Fiber': { min: 1, max: 8 }
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
        ctx.fillText('Select ingredients to view chart', ctx.canvas.width / 2, ctx.canvas.height / 2);
    }
    
    clearNutritionDisplay() {
        $('#total-weight, #total-calories, #total-protein, #total-fat, #calcium-phosphorus-ratio').text('0');
        $('#protein-percent, #fat-percent, #carb-percent').text('0');
        $('#nutrition-assessment').empty();
    }
    
    getCategoryName(category) {
        const categoryNames = {
            'red_meat': 'Red Meat',
            'white_meat': 'White Meat',
            'fish': 'Fish',
            'organs': 'Organs',
            'vegetables': 'Vegetables',
            'fruits': 'Fruits',
            'grains': 'Grains',
            'dairy': 'Dairy',
            'supplements': 'Supplements',
            'oils': 'Oils'
        };
        return categoryNames[category] || category;
    }
    
    getNutrientName(nutrient) {
        const nutrientNames = {
            'protein': 'Protein',
            'fat': 'Fat',
            'carbohydrate': 'Carbohydrate',
            'calcium': 'Calcium',
            'phosphorus': 'Phosphorus'
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