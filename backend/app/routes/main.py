# 在
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/base')
def base():
    return render_template('base.html')

@main_bp.route('/add_pet')
def add_pet():
    return render_template('add_pet.html')

@main_bp.route('/user_center')
def user_center():
    return render_template('user_center.html')
