let menu = document.querySelector('#menu-icon');
let sidenav = document.querySelector('.sidenav');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    sidenav.classList.toggle('active');
}

window.onscroll = () => {
    menu.classList.remove('bx-x');
    sidenav.classList.remove('active');
}

// 等待 ScrollReveal 加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化 ScrollReveal
    const sr = ScrollReveal({
        distance: '60px',
        duration: 2500,
        delay: 400,
        reset: true
    });

    // 添加动效
    sr.reveal('.text', {delay: 200, origin: 'top'});
    sr.reveal('.heading', {delay: 800, origin: 'top'});
    sr.reveal('.services-container .box', {delay: 600, origin: 'top'});
    sr.reveal('.about-container .box', {delay: 600, origin: 'top'});
});

// 修改滚动监听函数
function handleScroll() {
    const servicesSection = document.getElementById('services');
    const homeSection = document.getElementById('home');
    const filterForm = document.querySelector('.filter-form-container');
    
    if (servicesSection && filterForm && homeSection) {
        const servicesRect = servicesSection.getBoundingClientRect();
        const homeRect = homeSection.getBoundingClientRect();
        
        // 检查是否在推荐区域
        const isInServices = servicesRect.top <= window.innerHeight / 2 && 
                           servicesRect.bottom >= window.innerHeight / 2;
        
        // 检查是否在首页区域
        const isInHome = homeRect.top <= window.innerHeight / 2 && 
                        homeRect.bottom >= window.innerHeight / 2;
        
        if (isInServices) {
            filterForm.classList.add('show');
        } else if (isInHome) {
            filterForm.classList.remove('show');
        }
    }
}

// 添加滚动监听
window.addEventListener('scroll', handleScroll);

// 初始检查位置
document.addEventListener('DOMContentLoaded', function() {
    handleScroll();
    
    // 筛选栏显示/隐藏控制（点击按钮时）
    const filterToggle = document.querySelector('.filter-toggle');
    const filterContainer = document.querySelector('.filter-form-container');
    
    if (filterToggle && filterContainer) {
        filterToggle.addEventListener('click', function() {
            filterContainer.classList.toggle('show');
        });
    }
});

// 表单筛选功能
function filterCars(filters) {
    const cars = document.querySelectorAll('.services-container .box');
    
    cars.forEach(car => {
        // 获取汽车的所有属性
        const carData = {
            brand: car.dataset.brand,
            type: car.dataset.type,
            price: parseInt(car.dataset.price),
            body: car.dataset.body,
            drive: car.dataset.drive,
            wheelbase: parseInt(car.dataset.wheelbase),
            trunk: parseInt(car.dataset.trunk),
            energy: car.dataset.energy,
            range: parseInt(car.dataset.range)
        };

        // 检查是否符合所有筛选条件
        let shouldShow = true;

        // 遍历所有筛选条件
        for (let key in filters) {
            if (filters[key]) {  // 如果该筛选条件有值
                if (key === 'price') {
                    const [min, max] = filters[key].split('-').map(Number);
                    if (max) {
                        shouldShow = shouldShow && carData.price >= min && carData.price <= max;
                    } else {
                        shouldShow = shouldShow && carData.price >= min;
                    }
                } else if (key === 'wheelbase') {
                    const [min, max] = filters[key].split('-').map(Number);
                    if (max) {
                        shouldShow = shouldShow && carData.wheelbase >= min && carData.wheelbase <= max;
                    } else {
                        shouldShow = shouldShow && carData.wheelbase >= min;
                    }
                } else if (key === 'trunk') {
                    const [min, max] = filters[key].split('-').map(Number);
                    if (max) {
                        shouldShow = shouldShow && carData.trunk >= min && carData.trunk <= max;
                    } else {
                        shouldShow = shouldShow && carData.trunk >= min;
                    }
                } else if (key === 'range') {
                    const [min, max] = filters[key].split('-').map(Number);
                    if (max) {
                        shouldShow = shouldShow && carData.range >= min && carData.range <= max;
                    } else {
                        shouldShow = shouldShow && carData.range >= min;
                    }
                } else {
                    shouldShow = shouldShow && carData[key] === filters[key];
                }
            }
        }

        // 显示或隐藏汽车卡片
        car.style.display = shouldShow ? 'block' : 'none';
    });

    // 显示筛选结果数量
    const visibleCars = document.querySelectorAll('.services-container .box[style="display: block"]');
    updateFilterResults(visibleCars.length);
}

// 更新筛选结果数量
function updateFilterResults(count) {
    let resultsDiv = document.querySelector('.filter-results');
    if (!resultsDiv) {
        resultsDiv = document.createElement('div');
        resultsDiv.className = 'filter-results';
        document.querySelector('.filter-form-container').appendChild(resultsDiv);
    }
    resultsDiv.textContent = `找到 ${count} 款车型`;
}

// 表单提交处理
document.querySelector('.filter-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // 收集所有筛选条件
    const filters = {
        brand: this.brand.value,
        type: this.type.value,
        price: this.price.value,
        body: this.body.value,
        drive: this.drive.value,
        wheelbase: this.wheelbase.value,
        trunk: this.trunk.value,
        energy: this.energy.value,
        range: this.range.value
    };

    // 应用筛选
    filterCars(filters);
});

// 实时筛选（当任何选项改变时）
document.querySelector('.filter-form')?.addEventListener('change', function(e) {
    // 触发表单提交
    this.dispatchEvent(new Event('submit'));
});

// 详情模态框功能
const modal = document.getElementById('detailsModal');
const closeBtn = document.querySelector('.close');

// 显示详情
function showDetails(button) {
    const car = button.closest('.box');
    const modal = document.getElementById('detailsModal');
    
    // 获取汽车数据
    const carData = {
        image: car.querySelector('img').src,
        name: car.querySelector('h3').textContent,
        brand: car.dataset.brand,
        type: car.dataset.type,
        price: `¥${parseInt(car.dataset.price).toLocaleString()}`,
        body: car.dataset.body,
        drive: car.dataset.drive,
        wheelbase: `${car.dataset.wheelbase}mm`,
        trunk: `${car.dataset.trunk}L`,
        energy: car.dataset.energy,
        range: car.dataset.range === '0' ? '不适用' : `${car.dataset.range}km`
    };
    
    // 更新模态框内容
    modal.querySelector('.car-image img').src = carData.image;
    modal.querySelector('.car-info h2').textContent = carData.name;
    modal.querySelector('.value.brand').textContent = carData.brand;
    modal.querySelector('.value.type').textContent = carData.type;
    modal.querySelector('.value.price').textContent = carData.price;
    modal.querySelector('.value.body').textContent = carData.body;
    modal.querySelector('.value.drive').textContent = carData.drive;
    modal.querySelector('.value.wheelbase').textContent = carData.wheelbase;
    modal.querySelector('.value.trunk').textContent = carData.trunk;
    modal.querySelector('.value.energy').textContent = carData.energy;
    modal.querySelector('.value.range').textContent = carData.range;
    
    // 显示模态框
    modal.style.display = 'block';
}

// 关闭模态框
closeBtn.onclick = function() {
    modal.style.display = 'none';
}

// 点击模态框外部关闭
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// 登录模态框功能
const loginModal = document.getElementById('loginModal');
const loginBtn = document.querySelector('.sign-in');
const loginForm = document.getElementById('loginForm');
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('password');

// 显示登录模态框
loginBtn.onclick = function() {
    loginModal.style.display = 'block';
}

// 关闭登录模态框
loginModal.querySelector('.close').onclick = function() {
    loginModal.style.display = 'none';
}

// 点击模态框外部关闭
window.onclick = function(event) {
    if (event.target == loginModal) {
        loginModal.style.display = 'none';
    } else if (event.target == modal) {  // 保持原有的详情模态框功能
        modal.style.display = 'none';
    }
}

// 切换密码显示/隐藏
togglePassword.onclick = function() {
    const type = passwordInput.type === 'password' ? 'text' : 'password';
    passwordInput.type = type;
    togglePassword.className = `bx ${type === 'password' ? 'bx-hide' : 'bx-show'}`;
}

// 处理登录表单提交
loginForm.onsubmit = function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;

    // 这里添加登录逻辑
    console.log('Login attempt:', { username, password, remember });
    
    // 模拟登录成功
    alert('登录成功！');
    loginModal.style.display = 'none';
}

// 注册模态框功能
const registerModal = document.getElementById('registerModal');
const registerBtn = document.querySelector('.sign-up');
const registerForm = document.getElementById('registerForm');
const toggleRegPassword = document.getElementById('toggleRegPassword');
const toggleRegConfirmPassword = document.getElementById('toggleRegConfirmPassword');
const regPasswordInput = document.getElementById('reg-password');
const regConfirmPasswordInput = document.getElementById('reg-confirm-password');

// 显示注册模态框
registerBtn.onclick = function() {
    registerModal.style.display = 'block';
}

// 关闭注册模态框
registerModal.querySelector('.close').onclick = function() {
    registerModal.style.display = 'none';
}

// 更新点击模态框外部关闭的逻辑
window.onclick = function(event) {
    if (event.target == loginModal) {
        loginModal.style.display = 'none';
    } else if (event.target == registerModal) {
        registerModal.style.display = 'none';
    } else if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// 切换密码显示/隐藏（注册表单）
toggleRegPassword.onclick = function() {
    const type = regPasswordInput.type === 'password' ? 'text' : 'password';
    regPasswordInput.type = type;
    toggleRegPassword.className = `bx ${type === 'password' ? 'bx-hide' : 'bx-show'}`;
}

toggleRegConfirmPassword.onclick = function() {
    const type = regConfirmPasswordInput.type === 'password' ? 'text' : 'password';
    regConfirmPasswordInput.type = type;
    toggleRegConfirmPassword.className = `bx ${type === 'password' ? 'bx-hide' : 'bx-show'}`;
}

// 处理注册表单提交
registerForm.onsubmit = function(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;
    const agreeTerms = document.getElementById('agree-terms').checked;

    // 验证密码是否匹配
    if (password !== confirmPassword) {
        alert('两次输入的密码不一致！');
        return;
    }

    // 验证是否同意条款
    if (!agreeTerms) {
        alert('请同意服务条款和隐私政策！');
        return;
    }

    // 这里添加注册逻辑
    console.log('Register attempt:', { username, email, password, agreeTerms });
    
    // 模拟注册成功
    alert('注册成功！');
    registerModal.style.display = 'none';
}

// 模态框切换功能
document.querySelector('.register-link a').onclick = function(e) {
    e.preventDefault();
    loginModal.style.display = 'none';
    registerModal.style.display = 'block';
}

document.querySelector('.switch-to-login').onclick = function(e) {
    e.preventDefault();
    registerModal.style.display = 'none';
    loginModal.style.display = 'block';
}

// 收藏功能
function toggleFavorite(button) {
    const carBox = button.closest('.box');
    const carData = {
        brand: carBox.dataset.brand,
        type: carBox.dataset.type,
        price: carBox.dataset.price,
        body: carBox.dataset.body,
        drive: carBox.dataset.drive,
        wheelbase: carBox.dataset.wheelbase,
        trunk: carBox.dataset.trunk,
        energy: carBox.dataset.energy,
        range: carBox.dataset.range,
        name: carBox.querySelector('h3').textContent,
        image: carBox.querySelector('img').src
    };

    // 从localStorage获取收藏列表
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    
    // 检查是否已收藏
    const index = favorites.findIndex(item => item.name === carData.name);
    
    if (index === -1) {
        // 添加到收藏
        favorites.push(carData);
        button.classList.add('active');
        button.querySelector('i').className = 'bx bxs-heart';
        showToast('已添加到收藏');
    } else {
        // 取消收藏
        favorites.splice(index, 1);
        button.classList.remove('active');
        button.querySelector('i').className = 'bx bx-heart';
        showToast('已取消收藏');
    }

    // 保存到localStorage
    localStorage.setItem('favorites', JSON.stringify(favorites));
    
    // 如果在收藏页面，立即更新显示
    const isFavoritePage = window.location.pathname.endsWith('favorite.html') || 
                          window.location.href.includes('favorite.html');
    if (isFavoritePage) {
        displayFavorites();
    }
}

// 显示收藏列表
function displayFavorites() {
    console.log('Displaying favorites...');
    const container = document.getElementById('favoriteContainer');
    if (!container) {
        console.log('Container not found');
        return;
    }

    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    console.log('Favorites:', favorites);
    
    if (favorites.length === 0) {
        container.innerHTML = '<div class="empty-message">还没有收藏任何车型</div>';
        return;
    }

    container.innerHTML = favorites.map(car => `
        <div class="box" 
            data-brand="${car.brand}" 
            data-type="${car.type}" 
            data-price="${car.price}" 
            data-body="${car.body}" 
            data-drive="${car.drive}" 
            data-wheelbase="${car.wheelbase}" 
            data-trunk="${car.trunk}" 
            data-energy="${car.energy}" 
            data-range="${car.range}">
            <div class="box-img">
                <img src="${car.image}" alt="${car.name}">
                <button class="favorite-btn active" onclick="toggleFavorite(this)">
                    <i class='bx bxs-heart'></i>
                </button>
            </div>
            <h3>${car.name}</h3>
            <p class="price">¥${parseInt(car.price).toLocaleString()}</p>
            <button class="details-btn" onclick="showDetails(this)">查看详情</button>
        </div>
    `).join('');
}

// 显示提示消息
function showToast(message) {
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    // 添加显示类名
    setTimeout(() => toast.classList.add('show'), 100);

    // 2秒后移除
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 2000);
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否在收藏页面
    const isFavoritePage = window.location.pathname.endsWith('favorite.html') || 
                          window.location.href.includes('favorite.html');

    if (isFavoritePage) {
        console.log('Initializing favorites page...');
        displayFavorites();
    } else {
        // 在主页，初始化收藏按钮状态
        const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        document.querySelectorAll('.box').forEach(box => {
            const name = box.querySelector('h3').textContent;
            const isFavorited = favorites.some(item => item.name === name);
            const favoriteBtn = box.querySelector('.favorite-btn');
            if (isFavorited) {
                favoriteBtn.classList.add('active');
                favoriteBtn.querySelector('i').className = 'bx bxs-heart';
            }
        });
    }
});

// 从后端获取汽车数据
async function fetchCars() {
    try {
        const response = await fetch('/api/cars');  // 更新为相对路径
        const cars = await response.json();
        displayCars(cars);
    } catch (error) {
        console.error('获取汽车数据失败:', error);
        showToast('获取数据失败，请稍后重试');
    }
}

// 显示汽车卡片
function displayCars(cars) {
    const container = document.querySelector('.services-container');
    if (!container) return;

    container.innerHTML = ''; // 清空现有内容

    cars.forEach(car => {
        const box = document.createElement('div');
        box.className = 'box';
        box.dataset.brand = car.品牌;
        box.dataset.type = car.车身结构;
        box.dataset.price = car.价格 * 10000; // 转换为元
        box.dataset.body = car.车身结构;
        box.dataset.drive = car.驱动方式;
        box.dataset.wheelbase = car.轴距;
        box.dataset.trunk = car.行李箱容积;
        box.dataset.energy = car.能源类型;
        box.dataset.range = car.续航里程;

        box.innerHTML = `
            <div class="box-img">
                <img src="/static/img/cars/${car.品牌.toLowerCase()}.jpg" alt="${car.型号}" onerror="this.src='/static/img/default-car.jpg'">
                <button class="favorite-btn" onclick="toggleFavorite(this)">
                    <i class='bx bx-heart'></i>
                </button>
            </div>
            <h3>${car.型号}</h3>
            <h2>${car.价格}<span>万</span></h2>
            <div class="car-info">
                <span><i class='bx bxs-gas-pump'></i>${car.能源类型}</span>
                <span><i class='bx bx-car'></i>${car.车身结构}</span>
            </div>
            <a href="#" class="btn" onclick="showDetails(this.parentElement)">查看详情</a>
        `;

        container.appendChild(box);
    });
}

// 页面加载完成后获取数据
document.addEventListener('DOMContentLoaded', function() {
    fetchCars();
    // ... existing code ...
});