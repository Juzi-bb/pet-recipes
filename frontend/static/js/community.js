/**
 * 社区功能JavaScript工具类
 * 处理社区页面的交互和API调用
 */

class CommunityUtils {
    constructor() {
        this.apiBaseUrl = '/api/community';
        this.currentUser = this.getCurrentUser();
    }

    /**
     * 获取当前用户信息
     */
    getCurrentUser() {
        const appData = document.getElementById('app-data');
        if (appData) {
            return {
                isLoggedIn: appData.getAttribute('data-logged-in') === 'true',
                userId: appData.getAttribute('data-user-id'),
                nickname: appData.getAttribute('data-user-nickname')
            };
        }
        return { isLoggedIn: false, userId: null, nickname: null };
    }

    /**
     * 检查用户是否登录
     */
    requireLogin(action = 'perform this action') {
        if (!this.currentUser.isLoggedIn) {
            this.showToast(`Please login to ${action}`, 'info');
            return false;
        }
        return true;
    }

    /**
     * 通用API请求方法
     */
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    /**
     * 点赞食谱
     */
    async likeRecipe(recipeId) {
        if (!this.requireLogin('like recipes')) {
            return null;
        }

        try {
            return await this.apiRequest(`${this.apiBaseUrl}/recipe/${recipeId}/like`, {
                method: 'POST'
            });
        } catch (error) {
            this.showToast('Failed to like recipe', 'error');
            throw error;
        }
    }

    /**
     * 取消点赞食谱
     */
    async unlikeRecipe(recipeId) {
        if (!this.requireLogin('unlike recipes')) {
            return null;
        }

        try {
            return await this.apiRequest(`${this.apiBaseUrl}/recipe/${recipeId}/unlike`, {
                method: 'DELETE'
            });
        } catch (error) {
            this.showToast('Failed to unlike recipe', 'error');
            throw error;
        }
    }

    /**
     * 收藏食谱
     */
    async favoriteRecipe(recipeId) {
        if (!this.requireLogin('favorite recipes')) {
            return null;
        }

        try {
            return await this.apiRequest('/api/recipe/favorite', {
                method: 'POST',
                body: JSON.stringify({ recipe_id: recipeId })
            });
        } catch (error) {
            this.showToast('Failed to favorite recipe', 'error');
            throw error;
        }
    }

    /**
     * 取消收藏食谱
     */
    async unfavoriteRecipe(recipeId) {
        if (!this.requireLogin('unfavorite recipes')) {
            return null;
        }

        try {
            return await this.apiRequest(`/api/recipe/favorite/${recipeId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            this.showToast('Failed to unfavorite recipe', 'error');
            throw error;
        }
    }

    /**
     * 获取社区统计信息
     */
    async getCommunityStats() {
        try {
            return await this.apiRequest(`${this.apiBaseUrl}/stats`);
        } catch (error) {
            console.error('获取社区统计失败:', error);
            return null;
        }
    }

    /**
     * 获取热门食谱
     */
    async getTrendingRecipes(limit = 6) {
        try {
            return await this.apiRequest(`${this.apiBaseUrl}/trending?limit=${limit}`);
        } catch (error) {
            console.error('获取热门食谱失败:', error);
            return null;
        }
    }

    /**
     * 获取社区食谱列表
     */
    async getCommunityRecipes(params = {}) {
        const queryParams = new URLSearchParams({
            page: params.page || 1,
            per_page: params.perPage || 12,
            sort: params.sort || 'hot',
            search: params.search || '',
            author: params.author || ''
        });

        try {
            return await this.apiRequest(`${this.apiBaseUrl}/recipes?${queryParams}`);
        } catch (error) {
            console.error('获取社区食谱失败:', error);
            throw error;
        }
    }

    /**
     * 格式化数字显示
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    /**
     * 格式化日期显示
     */
    formatDate(dateString, options = {}) {
        const date = new Date(dateString);
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        return date.toLocaleDateString('en-US', finalOptions);
    }

    /**
     * 格式化相对时间显示
     */
    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        const intervals = [
            { name: 'year', seconds: 31536000 },
            { name: 'month', seconds: 2592000 },
            { name: 'week', seconds: 604800 },
            { name: 'day', seconds: 86400 },
            { name: 'hour', seconds: 3600 },
            { name: 'minute', seconds: 60 }
        ];

        for (const interval of intervals) {
            const count = Math.floor(diffInSeconds / interval.seconds);
            if (count >= 1) {
                return count === 1 ? `1 ${interval.name} ago` : `${count} ${interval.name}s ago`;
            }
        }

        return 'just now';
    }

    /**
     * HTML转义防止XSS攻击
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 截断文本
     */
    truncateText(text, maxLength = 100) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    }

    /**
     * 显示Toast消息
     */
    showToast(message, type = 'success', duration = 3000) {
        // 移除已存在的toast
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());

        // 创建新的toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const iconMap = {
            success: 'check-circle',
            error: 'exclamation-circle',
            info: 'info-circle',
            warning: 'exclamation-triangle'
        };

        toast.innerHTML = `
            <i class="fas fa-${iconMap[type] || 'info-circle'}"></i>
            <span>${this.escapeHtml(message)}</span>
        `;

        // 确保toast样式存在
        this.ensureToastStyles();

        document.body.appendChild(toast);

        // 自动消失
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }

    /**
     * 确保Toast样式存在
     */
    ensureToastStyles() {
        if (!document.querySelector('#community-toast-styles')) {
            const style = document.createElement('style');
            style.id = 'community-toast-styles';
            style.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 20px;
                    border-radius: 8px;
                    color: white;
                    font-weight: 500;
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    animation: slideInRight 0.3s ease;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    max-width: 400px;
                    font-family: inherit;
                }
                .toast-success { background: #27ae60; }
                .toast-error { background: #e74c3c; }
                .toast-info { background: #5580AD; }
                .toast-warning { background: #f39c12; }
                
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * 节流函数
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * 获取随机食谱图标
     */
    getRandomRecipeIcon(index) {
        const icons = [
            '🥩', '🐟', '🍗', '🥕', '🥬', '🍠', '🌽', '🍎', '🥓', '🍖',
            '🐠', '🦐', '🥦', '🥒', '🍅', '🥔', '🎃', '🍌', '🥚', '🧀',
            '🍊', '🍐', '🍄', '🦪', '🦌', '🐓', '🦆', '🌾', '🌿', '🍓'
        ];
        return icons[index % icons.length];
    }

    /**
     * 滚动到页面顶部
     */
    scrollToTop(smooth = true) {
        window.scrollTo({
            top: 0,
            behavior: smooth ? 'smooth' : 'auto'
        });
    }

    /**
     * 滚动到指定元素
     */
    scrollToElement(element, offset = 0) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const rect = element.getBoundingClientRect();
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const targetPosition = rect.top + scrollTop - offset;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }

    /**
     * 检查元素是否在视窗内
     */
    isElementInViewport(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
}

// 创建全局实例
const communityUtils = new CommunityUtils();

// 为了向后兼容，暴露一些全局函数
window.CommunityUtils = CommunityUtils;
window.communityUtils = communityUtils;