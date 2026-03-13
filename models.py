import json
from typing import List, Optional
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化SQLAlchemy
db = SQLAlchemy()

# 用户模型
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Car:
    def __init__(self, brand: str, model: str, price: float, body_type: str, 
                 drive_type: str, wheelbase: int, trunk_volume: float, energy_type: str):
        self.brand = brand
        self.model = model
        self.price = price
        self.body_type = body_type
        self.drive_type = drive_type
        self.wheelbase = wheelbase
        self.trunk_volume = trunk_volume
        self.energy_type = energy_type

    def format_info(self) -> dict:
        return {
            "品牌": self.brand,
            "车型": self.model,
            "价格(万元)": self.price,
            "车身结构": self.body_type,
            "驱动方式": self.drive_type,
            "轴距(mm)": self.wheelbase,
            "行李箱容积(L)": self.trunk_volume,
            "能源类型": self.energy_type
        }

class ElectricCar(Car):
    def __init__(self, brand: str, model: str, price: float, body_type: str,
                 drive_type: str, wheelbase: int, trunk_volume: float,
                 energy_type: str, range_km: int):
        super().__init__(brand, model, price, body_type, drive_type,
                        wheelbase, trunk_volume, energy_type)
        self.range_km = range_km

    def format_info(self) -> dict:
        info = super().format_info()
        info["续航里程(km)"] = self.range_km
        return info

class UserPreferences:
    def __init__(self, budget: Optional[float] = None, min_price: Optional[float] = None,
                 preferred_brands: List[str] = None, preferred_body_types: List[str] = None,
                 min_range_km: Optional[int] = None, preferred_drive_types: List[str] = None,
                 preferred_energy_types: List[str] = None):
        self.budget = budget
        self.min_price = min_price
        self.preferred_brands = preferred_brands or []
        self.preferred_body_types = preferred_body_types or []
        self.min_range_km = min_range_km
        self.preferred_drive_types = preferred_drive_types or []
        self.preferred_energy_types = preferred_energy_types or []

class CarRecommender:
    def __init__(self, cars_data_path: str):
        self.cars = self._load_cars(cars_data_path)

    def _load_cars(self, data_path: str) -> List[Car]:
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cars = []
            for car_data in data:
                if car_data.get("能源类型") == "电动":
                    car = ElectricCar(
                        brand=car_data["品牌"],
                        model=car_data["车型"],
                        price=car_data["价格(万元)"],
                        body_type=car_data["车身结构"],
                        drive_type=car_data["驱动方式"],
                        wheelbase=car_data["轴距(mm)"],
                        trunk_volume=car_data["行李箱容积(L)"],
                        energy_type=car_data["能源类型"],
                        range_km=car_data.get("续航里程(km)", 0)
                    )
                else:
                    car = Car(
                        brand=car_data["品牌"],
                        model=car_data["车型"],
                        price=car_data["价格(万元)"],
                        body_type=car_data["车身结构"],
                        drive_type=car_data["驱动方式"],
                        wheelbase=car_data["轴距(mm)"],
                        trunk_volume=car_data["行李箱容积(L)"],
                        energy_type=car_data["能源类型"]
                    )
                cars.append(car)
            return cars
        except Exception as e:
            print(f"Error loading cars data: {e}")
            return []

    def recommend(self, preferences: UserPreferences) -> List[Car]:
        recommended_cars = []
        
        try:
            for car in self.cars:
                matches = True
                
                if preferences.budget and car.price > preferences.budget:
                    matches = False
                
                if preferences.min_price and car.price < preferences.min_price:
                    matches = False
                    
                if preferences.preferred_brands and car.brand not in preferences.preferred_brands:
                    matches = False
                    
                if preferences.preferred_body_types and car.body_type not in preferences.preferred_body_types:
                    matches = False
                    
                if preferences.preferred_drive_types and car.drive_type not in preferences.preferred_drive_types:
                    matches = False

                if preferences.preferred_energy_types and car.energy_type not in preferences.preferred_energy_types:
                    matches = False
                    
                if preferences.min_range_km and isinstance(car, ElectricCar):
                    if car.range_km < preferences.min_range_km:
                        matches = False
                
                if matches:
                    recommended_cars.append(car)
                    
        except Exception as e:
            print(f"Error during recommendation: {e}")
            
        return recommended_cars 

# 将收藏与用户关联
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_brand = db.Column(db.String(64), nullable=False)
    car_model = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "car_brand": self.car_brand,
            "car_model": self.car_model,
            "timestamp": self.timestamp.isoformat()
        }

# 保留旧的Favorite类用于兼容
class FavoriteOld:
    def __init__(self, car_brand: str, car_model: str, timestamp: datetime = None):
        self.car_brand = car_brand
        self.car_model = car_model
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        return {
            "car_brand": self.car_brand,
            "car_model": self.car_model,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FavoriteOld':
        return cls(
            car_brand=data["car_brand"],
            car_model=data["car_model"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

class FavoriteManager:
    def __init__(self, favorites_file: str):
        self.favorites_file = favorites_file
        self.favorites: List[FavoriteOld] = self._load_favorites()

    def _load_favorites(self) -> List[FavoriteOld]:
        try:
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [FavoriteOld.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_favorites(self):
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump([fav.to_dict() for fav in self.favorites], f, ensure_ascii=False, indent=2)

    def add_favorite(self, car_brand: str, car_model: str) -> bool:
        # 检查是否已经收藏
        if not self.is_favorite(car_brand, car_model):
            self.favorites.append(FavoriteOld(car_brand, car_model))
            self._save_favorites()
            return True
        return False

    def remove_favorite(self, car_brand: str, car_model: str) -> bool:
        initial_length = len(self.favorites)
        self.favorites = [f for f in self.favorites 
                         if not (f.car_brand == car_brand and f.car_model == car_model)]
        if len(self.favorites) < initial_length:
            self._save_favorites()
            return True
        return False

    def is_favorite(self, car_brand: str, car_model: str) -> bool:
        return any(f.car_brand == car_brand and f.car_model == car_model 
                  for f in self.favorites)

    def get_all_favorites(self) -> List[FavoriteOld]:
        return sorted(self.favorites, key=lambda x: x.timestamp, reverse=True) 