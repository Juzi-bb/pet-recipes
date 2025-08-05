/**
 * 食材百科交互功能
 * 提供搜索、筛选、分页等功能
 */

// 全局变量
let currentPage = 1;
let totalPages = 1;
let currentCategory = 'all';
let currentSafetyFilter = 'all';
let currentSearchTerm = '';
let ingredients = [];
let categories = [];
let searchTimeout = null;

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEncyclopedia();
    setupEventListeners();
});

// 初始化食材百科
async function initializeEncyclopedia() {
    try {
        // 确保初始值正确设置
        currentCategory = 'all';
        currentSafetyFilter = 'all';
        currentSearchTerm = '';
        currentPage = 1;
        
        console.log('正在初始化食材百科...'); // 调试日志
        
        // 并行加载统计信息和分类信息
        await Promise.all([
            loadStatistics(),
            loadCategories()
        ]);
        
        // 加载初始食材数据
        await loadIngredients();
        
        console.log('食材百科初始化成功'); // 调试日志
        
    } catch (error) {
        console.error('初始化食材百科失败:', error);
        showError('Failed to load encyclopedia data, please refresh the page');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索输入框
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', handleSearch);
    searchInput.addEventListener('blur', function() {
        // 延迟隐藏搜索建议，允许点击
        setTimeout(() => {
            document.getElementById('searchSuggestions').style.display = 'none';
        }, 200);
    });
    
    // 安全性筛选
    const safetyFilter = document.getElementById('safetyFilter');
    safetyFilter.addEventListener('change', handleSafetyFilter);
    
    // 分页按钮
    document.getElementById('prevBtn').addEventListener('click', previousPage);
    document.getElementById('nextBtn').addEventListener('click', nextPage);
    
    // 键盘快捷键
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// 加载统计信息
async function loadStatistics() {
    try {
        const response = await fetch('/api/ingredients/stats');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // 更新统计显示
        document.getElementById('totalIngredients').textContent = data.stats.total_ingredients || 0;
        document.getElementById('safeForDogs').textContent = data.stats.safe_for_dogs || 0;
        document.getElementById('safeForCats').textContent = data.stats.safe_for_cats || 0;
        
    } catch (error) {
        console.error('Failed to load statistics:', error);
        // 使用默认值
        document.getElementById('totalIngredients').textContent = '0';
        document.getElementById('safeForDogs').textContent = '0';
        document.getElementById('safeForCats').textContent = '0';
    }
}

// 加载分类信息
async function loadCategories() {
    try {
        const response = await fetch('/api/ingredients/categories');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('分类数据:', data); // 调试日志
        categories = data.categories;
        
        renderCategoryTabs();
        
    } catch (error) {
        console.error('加载分类失败:', error);
        showError('Failed to load categories');
    }
}

// 渲染分类标签
function renderCategoryTabs() {
    const tabsContainer = document.getElementById('categoryTabs');
    
    // 清空现有内容
    tabsContainer.innerHTML = '';
    
    // 添加"全部"标签
    const allTab = document.createElement('button');
    allTab.className = 'category-tab active';
    allTab.setAttribute('data-category', 'all');
    allTab.innerHTML = `
        <i class="fas fa-th-large"></i>
        <span>All</span>
        <span class="category-count" id="countAll">0</span>
    `;
    allTab.addEventListener('click', () => selectCategory('all'));
    tabsContainer.appendChild(allTab);
    
    // 更新全部分类的计数
    const totalCount = categories.reduce((sum, cat) => sum + cat.count, 0);
    document.getElementById('countAll').textContent = totalCount;
    
    // 添加其他分类标签
    categories.forEach(category => {
        const tab = document.createElement('button');
        tab.className = 'category-tab';
        // 使用category.id而不是category.value
        tab.setAttribute('data-category', category.id);
        tab.innerHTML = `
            <i class="${category.icon_class}"></i>
            <span>${category.name}</span>
            <span class="category-count">${category.count}</span>
        `;
        // 绑定点击事件，使用category.id
        tab.addEventListener('click', () => selectCategory(category.id));
        tabsContainer.appendChild(tab);
    });
    
    console.log('分类标签渲染完成，共', categories.length, '个分类'); // 调试日志
}

// 选择分类
async function selectCategory(categoryValue) {
    // 确保categoryValue是有效的
    if (!categoryValue || categoryValue === 'undefined') {
        categoryValue = 'all';
    }
    
    currentCategory = categoryValue;
    currentPage = 1;
    
    console.log('选择的分类:', categoryValue); // 调试日志
    
    // 更新分类标签状态
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    const selectedTab = document.querySelector(`[data-category="${categoryValue}"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
        console.log('分类标签状态已更新'); // 调试日志
    } else {
        console.warn('未找到对应的分类标签:', categoryValue); // 调试日志
    }
    
    // 重新加载食材
    await loadIngredients();
}

// 处理搜索
function handleSearch(event) {
    const searchTerm = event.target.value.trim();
    
    // 清除之前的搜索定时器
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // 设置新的搜索定时器（防抖）
    searchTimeout = setTimeout(async () => {
        currentSearchTerm = searchTerm;
        currentPage = 1;
        
        if (searchTerm.length >= 2) {
            // 显示搜索建议
            await showSearchSuggestions(searchTerm);
        } else {
            // 隐藏搜索建议
            document.getElementById('searchSuggestions').style.display = 'none';
        }
        
        // 重新加载食材
        await loadIngredients();
    }, 300);
}

// 显示搜索建议
async function showSearchSuggestions(searchTerm) {
    try {
        const response = await fetch(`/api/ingredients/search/suggestions?q=${encodeURIComponent(searchTerm)}`);
        if (!response.ok) return;
        
        const data = await response.json();
        const suggestionsContainer = document.getElementById('searchSuggestions');
        
        if (data.suggestions.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
        }
        
        suggestionsContainer.innerHTML = data.suggestions.map(suggestion => `
            <div class="suggestion-item" onclick="selectSuggestion(${suggestion.id}, '${suggestion.name}')">
                <i class="fas fa-seedling"></i>
                <span>${suggestion.name}</span>
                ${suggestion.name_en ? `<span style="color: #999; font-style: italic;">- ${suggestion.name_en}</span>` : ''}
            </div>
        `).join('');
        
        suggestionsContainer.style.display = 'block';
        
    } catch (error) {
        console.error('加载搜索建议失败:', error);
    }
}

// 选择搜索建议
function selectSuggestion(ingredientId, ingredientName) {
    // 跳转到食材详情页
    window.location.href = `/ingredient/${ingredientId}`;
}

// 处理安全性筛选
async function handleSafetyFilter(event) {
    currentSafetyFilter = event.target.value;
    currentPage = 1;
    console.log('安全性筛选变更:', currentSafetyFilter); // 调试日志
    await loadIngredients();
}

// 加载食材数据
async function loadIngredients() {
    try {
        showLoading();
        
        // 构建查询参数
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 24
        });
        
        // 只有当分类不是'all'且有效时才添加分类参数
        if (currentCategory && currentCategory !== 'all' && currentCategory !== 'undefined') {
            params.append('category', currentCategory);
        }
        
        // 只有当安全筛选不是'all'且有效时才添加安全参数
        if (currentSafetyFilter && currentSafetyFilter !== 'all' && currentSafetyFilter !== 'undefined') {
            params.append('safe_for', currentSafetyFilter);
        }
        
        // 只有当搜索词存在且有效时才添加搜索参数
        if (currentSearchTerm && currentSearchTerm.trim() !== '') {
            params.append('search', currentSearchTerm.trim());
        }
        
        console.log('正在加载食材，参数:', params.toString()); // 调试日志
        
        const response = await fetch(`/api/ingredients?${params.toString()}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('食材数据加载成功，数量:', data.ingredients.length); // 调试日志
        
        ingredients = data.ingredients;
        totalPages = data.pagination ? data.pagination.total_pages : 1;
        currentPage = data.pagination ? data.pagination.current_page : 1;
        
        renderIngredients();
        updatePagination();
        hideLoading();
        
    } catch (error) {
        console.error('加载食材失败:', error);
        hideLoading();
        showError('Failed to load ingredients, please check your network connection');
    }
}

// 渲染食材网格
function renderIngredients() {
    const grid = document.getElementById('ingredientsGrid');
    const noResults = document.getElementById('noResults');
    
    if (ingredients.length === 0) {
        grid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    noResults.style.display = 'none';
    grid.style.display = 'grid';
    
    grid.innerHTML = ingredients.map(ingredient => createIngredientCard(ingredient)).join('');
}

// 创建食材卡片HTML
function createIngredientCard(ingredient) {
    // 生成安全性标签
    let safetyBadge = '';
    if (ingredient.is_safe_for_dogs && ingredient.is_safe_for_cats) {
        safetyBadge = '<div class="safety-badge">Safe</div>';
    } else if (ingredient.is_safe_for_dogs || ingredient.is_safe_for_cats) {
        safetyBadge = '<div class="safety-badge partial">Partial</div>';
    } else if (ingredient.is_common_allergen) {
        safetyBadge = '<div class="safety-badge unsafe">Caution</div>';
    }
    
    // 生成营养亮点标签
    let nutritionHighlights = '';
    const highlights = [];
    
    if (ingredient.protein && ingredient.protein > 20) {
        highlights.push('<span class="nutrition-tag high-protein">High Protein</span>');
    }
    if (ingredient.fat && ingredient.fat < 5) {
        highlights.push('<span class="nutrition-tag low-fat">Low Fat</span>');
    }
    if (ingredient.fiber && ingredient.fiber > 3) {
        highlights.push('<span class="nutrition-tag high-fiber">High Fiber</span>');
    }
    
    if (highlights.length > 0) {
        nutritionHighlights = `<div class="nutrition-highlights">${highlights.slice(0, 2).join('')}</div>`;
    }
    
    // 生成分类标签
    const categoryBadge = `<div class="category-badge">${getCategoryName(ingredient.category)}</div>`;
    
    // 生成图片HTML
    const imageHtml = ingredient.image_filename 
        ? `<img src="/static/images/ingredients/${ingredient.image_filename}" alt="${ingredient.name}" onerror="handleImageError(this)">`
        : '<div class="no-image"><i class="fas fa-image"></i><span>No Image</span></div>';
    
    // 生成营养信息
    const nutritionInfo = `
        ${ingredient.calories || 0} kcal/100g<br>
        Protein: ${ingredient.protein || 0}g | Fat: ${ingredient.fat || 0}g
    `;
    
    return `
        <div class="ingredient-card" onclick="viewIngredientDetail(${ingredient.id})">
            ${safetyBadge}
            ${nutritionHighlights}
            <div class="ingredient-image">
                ${imageHtml}
            </div>
            <div class="ingredient-name">${ingredient.name}</div>
            <div class="ingredient-info">${nutritionInfo}</div>
            ${categoryBadge}
        </div>
    `;
}

// 处理图片加载错误
function handleImageError(img) {
    const container = img.parentElement;
    container.innerHTML = '<div class="no-image"><i class="fas fa-image"></i><span>No Image</span></div>';
}

// 查看食材详情
function viewIngredientDetail(ingredientId) {
    window.location.href = `/ingredient/${ingredientId}`;
}

// 获取分类名称
function getCategoryName(categoryValue) {
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
        'dangerous': 'Dangerous Foods'  // 新添加危险食材分类
    };
    return categoryNames[categoryValue] || categoryValue;
}

// 更新分页控件
function updatePagination() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const pageInfo = document.getElementById('pageInfo');
    
    // 更新按钮状态
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
    
    // 更新页面信息
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    
    // 显示或隐藏分页控件
    const paginationContainer = document.getElementById('paginationContainer');
    if (totalPages <= 1) {
        paginationContainer.style.display = 'none';
    } else {
        paginationContainer.style.display = 'flex';
    }
}

// 上一页
async function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        await loadIngredients();
        // 滚动到顶部
        document.querySelector('.ingredients-grid').scrollIntoView({ behavior: 'smooth' });
    }
}

// 下一页
async function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        await loadIngredients();
        // 滚动到顶部
        document.querySelector('.ingredients-grid').scrollIntoView({ behavior: 'smooth' });
    }
}

// 键盘快捷键处理
function handleKeyboardShortcuts(event) {
    // 搜索快捷键 (Ctrl/Cmd + K)
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        document.getElementById('searchInput').focus();
    }
    
    // 分页快捷键 (左右箭头键)
    if (event.key === 'ArrowLeft' && event.altKey) {
        event.preventDefault();
        if (currentPage > 1) previousPage();
    }
    
    if (event.key === 'ArrowRight' && event.altKey) {
        event.preventDefault();
        if (currentPage < totalPages) nextPage();
    }
}

// 显示加载状态
function showLoading() {
    document.getElementById('loadingContainer').style.display = 'block';
    document.getElementById('ingredientsGrid').style.display = 'none';
    document.getElementById('noResults').style.display = 'none';
}

// 隐藏加载状态
function hideLoading() {
    document.getElementById('loadingContainer').style.display = 'none';
}

// 显示错误信息
function showError(message) {
    hideLoading();
    
    // 创建错误提示
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center;">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Error:</strong> ${message}
        </div>
    `;
    
    // 插入到食材网格前面
    const grid = document.getElementById('ingredientsGrid');
    grid.parentNode.insertBefore(errorDiv, grid);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

// 工具函数：防抖
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// 工具函数：节流
function throttle(func, delay) {
    let timeoutId;
    let lastExecTime = 0;
    return function (...args) {
        const currentTime = Date.now();
        
        if (currentTime - lastExecTime > delay) {
            func.apply(this, args);
            lastExecTime = currentTime;
        } else {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
                lastExecTime = Date.now();
            }, delay - (currentTime - lastExecTime));
        }
    };
}