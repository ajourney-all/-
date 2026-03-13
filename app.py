from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models import CarRecommender, UserPreferences, FavoriteManager, db, User, Favorite
from forms import RegistrationForm, LoginForm
import os
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 初始化推荐器和收藏管理器
recommender = CarRecommender(os.path.join(os.path.dirname(__file__), 'data', 'data.json'))
favorite_manager = FavoriteManager(os.path.join(os.path.dirname(__file__), 'data', 'favorites.json'))

def get_car_image_index(target_car_info):
    """获取车辆对应的图片索引"""
    all_cars = [car.format_info() for car in recommender.cars]
    for index, car in enumerate(all_cars):
        if (car["品牌"] == target_car_info["品牌"] and 
            car["车型"] == target_car_info["车型"]):
            return index + 1
    return None

# 创建数据库表
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    # 从URL参数中获取筛选条件
    budget = request.args.get('budget')
    min_price = request.args.get('min_price')
    brand = request.args.get('brand')
    body_type = request.args.get('body_type')
    drive_type = request.args.get('drive_type')
    min_range = request.args.get('min_range')
    energy_type = request.args.get('energy_type')

    # 获取所有可用的筛选选项
    formatted_cars = [car.format_info() for car in recommender.cars]
    all_brands = sorted(list(set(car["品牌"] for car in formatted_cars)))
    all_body_types = sorted(list(set(car["车身结构"] for car in formatted_cars)))
    all_drive_types = sorted(list(set(car["驱动方式"] for car in formatted_cars)))
    all_energy_types = sorted(list(set(car["能源类型"] for car in formatted_cars)))
    
    # 如果有URL参数，自动应用筛选
    if any([budget, min_price, brand, body_type, drive_type, min_range, energy_type]):
        preferences = UserPreferences(
            budget=float(budget) if budget else None,
            min_price=float(min_price) if min_price else None,
            preferred_brands=[brand] if brand else None,
            preferred_body_types=[body_type] if body_type else None,
            preferred_drive_types=[drive_type] if drive_type else None,
            min_range_km=int(min_range) if min_range else None,
            preferred_energy_types=[energy_type] if energy_type else None
        )
        cars_to_show = recommender.recommend(preferences)
    else:
        cars_to_show = recommender.cars

    # 为每个车辆获取图片索引
    cars_with_images = []
    for car in cars_to_show:
        car_info = car.format_info()
        image_index = get_car_image_index(car_info)
        cars_with_images.append({
            'info': car_info,
            'image_index': image_index
        })

    return render_template('index.html',
                         cars=cars_with_images,
                         brands=all_brands,
                         body_types=all_body_types,
                         drive_types=all_drive_types,
                         energy_types=all_energy_types)

@app.route('/filter', methods=['POST'])
def filter_cars():
    try:
        data = request.get_json()
        
        # 创建用户偏好对象
        preferences = UserPreferences(
            budget=float(data['budget']) if data.get('budget') else None,
            min_price=float(data['min_price']) if data.get('min_price') else None,
            preferred_brands=[data['brand']] if data.get('brand') else None,
            preferred_body_types=[data['body_type']] if data.get('body_type') else None,
            preferred_drive_types=[data['drive_type']] if data.get('drive_type') else None,
            min_range_km=int(data['min_range']) if data.get('min_range') else None,
            preferred_energy_types=[data['energy_type']] if data.get('energy_type') else None
        )
        
        # 获取推荐结果
        recommended_cars = recommender.recommend(preferences)
        
        # 保存筛选历史
        if 'history' not in session:
            session['history'] = []
        
        history_entry = {
            'preferences': {
                'budget': data.get('budget'),
                'min_price': data.get('min_price'),
                'brand': data.get('brand'),
                'body_type': data.get('body_type'),
                'drive_type': data.get('drive_type'),
                'min_range': data.get('min_range'),
                'energy_type': data.get('energy_type')
            },
            'results_count': len(recommended_cars),
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        session['history'] = [history_entry] + session['history']
        session.modified = True
        
        # 为每个推荐的车辆找到其图片索引
        results = []
        for rec_car in recommended_cars:
            car_info = rec_car.format_info()
            image_index = get_car_image_index(car_info)
            results.append({
                'info': car_info,
                'image_index': image_index
            })
            
        return jsonify({
            'success': True, 
            'cars': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/details/<brand>/<model>')
def car_details(brand, model):
    # 查找特定车型
    formatted_cars = [car.format_info() for car in recommender.cars]
    car = next((car for car in formatted_cars 
                if car["品牌"] == brand and car["车型"] == model), None)
    
    if car:
        image_index = get_car_image_index(car)
        return render_template('details.html', car=car, image_index=image_index)
    return "Car not found", 404

@app.route('/history')
def view_history():
    history = session.get('history', [])
    return render_template('history.html', history=history)

@app.route('/get_history')
def get_history():
    history = session.get('history', [])
    return jsonify({'success': True, 'history': history})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['history'] = []
    session.modified = True
    return jsonify({'success': True})

@app.route('/favorites')
@login_required
def favorites():
    # 获取当前用户的收藏
    if current_user.is_authenticated:
        user_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.timestamp.desc()).all()
    else:
        # 兼容旧版本，使用文件存储的收藏
        user_favorites = favorite_manager.get_all_favorites()
    
    favorite_cars = []
    
    for fav in user_favorites:
        # 查找对应的车辆信息
        car = next((car for car in recommender.cars 
                    if car.brand == fav.car_brand and car.model == fav.car_model), None)
        if car:
            car_info = car.format_info()
            image_index = get_car_image_index(car_info)
            favorite_cars.append({
                'info': car_info,
                'image_index': image_index,
                'timestamp': fav.timestamp
            })
    
    return render_template('favorites.html', cars=favorite_cars)

@app.route('/api/favorites/<brand>/<model>', methods=['POST', 'DELETE'])
@login_required
def manage_favorite(brand, model):
    try:
        if request.method == 'POST':
            # 添加收藏到数据库
            if current_user.is_authenticated:
                # 检查是否已收藏
                existing = Favorite.query.filter_by(
                    user_id=current_user.id,
                    car_brand=brand,
                    car_model=model
                ).first()
                
                if not existing:
                    new_favorite = Favorite(
                        user_id=current_user.id,
                        car_brand=brand,
                        car_model=model
                    )
                    db.session.add(new_favorite)
                    db.session.commit()
                    success = True
                    message = '收藏成功'
                else:
                    success = False
                    message = '已经收藏过了'
            else:
                # 兼容旧版本
                success = favorite_manager.add_favorite(brand, model)
                message = '收藏成功' if success else '已经收藏过了'
                
            return jsonify({
                'success': success,
                'message': message
            })
        else:
            # 取消收藏
            if current_user.is_authenticated:
                favorite = Favorite.query.filter_by(
                    user_id=current_user.id,
                    car_brand=brand,
                    car_model=model
                ).first()
                
                if favorite:
                    db.session.delete(favorite)
                    db.session.commit()
                    success = True
                    message = '取消收藏成功'
                else:
                    success = False
                    message = '未找到收藏记录'
            else:
                # 兼容旧版本
                success = favorite_manager.remove_favorite(brand, model)
                message = '取消收藏成功' if success else '未找到收藏记录'
                
            return jsonify({
                'success': success,
                'message': message
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/favorites/check/<brand>/<model>')
def check_favorite(brand, model):
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            car_brand=brand,
            car_model=model
        ).first() is not None
    else:
        # 兼容旧版本
        is_favorite = favorite_manager.is_favorite(brand, model)
        
    return jsonify({
        'is_favorite': is_favorite
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！现在您可以登录了。', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('登录成功！', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('登录失败。请检查用户名和密码。', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('您已成功退出登录。', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # 获取用户收藏数量
    favorites_count = Favorite.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户筛选历史数量
    history_count = len(session.get('history', []))
    
    # 获取最近5条收藏记录
    recent_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.timestamp.desc()).limit(5).all()
    
    # 获取最近5条筛选历史
    recent_history = session.get('history', [])[:5]
    
    return render_template('profile.html', 
                          favorites_count=favorites_count,
                          history_count=history_count,
                          recent_favorites=recent_favorites,
                          recent_history=recent_history)

if __name__ == '__main__':
    app.run(debug=True) 