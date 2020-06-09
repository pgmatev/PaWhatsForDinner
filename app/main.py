from flask import Flask, redirect, render_template, request, url_for, Blueprint, flash
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from .user import User
from .product import Product


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.find_by_id(current_user.id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.password = generate_password_hash(request.form['password'], method='sha256')

        flash('Updated success')

        user.update()

    return render_template('profile.html', user=user)


@main.route('/products')
def products():
    return render_template('products.html', products=Product.all())


@main.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        values = (
            None,
            request.form['name'],
            request.form['unit']
        )

        Product(*values).create()

        return redirect(url_for('main.products'))

    return render_template('create_product.html')


@main.route('/products/<int:id>')
@login_required
def view_product(id):
    return render_template('product.html', product = Product.find(id))


@main.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.find(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.unit = request.form['unit']

        product.update()

        return redirect(url_for('main.products'))

    return render_template('edit_product.html', product = product)


@main.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.find(id)
    product.delete()

    return redirect(url_for('main.products'))


if __name__ == '__main__':
    main.app.run()
