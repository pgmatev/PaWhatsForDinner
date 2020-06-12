from flask import Flask, redirect, render_template, request, url_for, Blueprint, flash
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from .user import User
from .product import Product
from .recipes import Recipe
from .ingredient import Ingredient
from .database import DB

main = Blueprint('main', __name__)
upload_folder = "/home/vesko/Desktop/subd/PaWhatsForDinner/app/static/img/uploads"


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

@main.route('/recipes')
def recipes():
    return render_template('recipes.html', recipes=Recipe.all())

@main.route('/create_recipe', methods=['GET', 'POST'])
@login_required
def create_recipe():
    if request.method == 'GET':
        products = Product.all()
        return render_template('create_recipe.html', products=products)
    elif request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            filename = secure_filename("/default.jpeg")
            filepath = os.path.join("/static/img", filename)
        if file and Recipe.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
            filepath = os.path.join("/static/img/uploads", filename)
        values = (
            None,
            request.form['recipe_name'],
            current_user.id,
            request.form['description'],
            0.0,
            request.form['time'],
            filepath
        )
        Recipe(*values).create()

        recipe_id = Recipe.find_last_id()[0]

        ingredients = [
            None,
            recipe_id,
            None,
            None
        ]
        i = 1
        while(request.form.get('id_of_product' + str(i)) is not None):
            ingredients[2] = request.form.get('id_of_product' + str(i))
            ingredients[3] = request.form.get('quantity_of_product' + str(i))
            Ingredient(*ingredients).create()
            i += 1

        return redirect(url_for('main.recipes'))

@main.route('/recipes/<int:id>', methods=['GET', 'POST'])
def show_recipe(id):
    if request.method == 'GET':
        if current_user.is_authenticated:
            recipe = Recipe.find(id)
            user_id = str(current_user.id)
            ingredients = Ingredient.find_by_recipe_id(recipe.id)

            recipe_ingredients_names = []
            fridge_products_names = []

            for ingredient in ingredients:
                recipe_ingredients_names.append(Product.find(ingredient.product_id).name)

            missing_products = []
            missing_products_names = []

            for index, ingredient_name in enumerate(recipe_ingredients_names):
                if ingredient_name in fridge_products_names:
                        missing_products.append(ingredients[index])
                        missing_products_names.append(ingredient_name)

                else:
                    missing_products.append(ingredients[index])
                    missing_products_names.append(ingredient_name)

                    
            return render_template('view_recipe.html', recipe=recipe, user_id=user_id, ingredients=ingredients, product=Product, missing_products=missing_products, missing_products_names=missing_products_names)
        else:
            recipe = Recipe.find(id)
            ingredients = Ingredient.find_by_recipe_id(recipe.id)
            missing_products_names = []
            for ingredient in ingredients:
                missing_products_names.append(Product.find(ingredient.product_id).name)
            return render_template('view_recipe.html', recipe=recipe, ingredients=ingredients, product=Product, missing_products_names=missing_products_names)

    elif request.method == 'POST':
        recipe = Recipe.find(id)
        if current_user.is_authenticated:
            rate = request.form['rate']
            recipe.set_rating(rate, current_user.id)
            recipe.set_overall_rating()


        return redirect(url_for('main.show_recipe', id=recipe.id))

@main.route('/recipes/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(id):
    recipe = Recipe.find(id)
    ingredients = Ingredient.find_by_recipe_id(recipe.id)
    number_of_ingredients = len(ingredients)
    products = Product.all()
    if request.method == 'GET':
        return render_template('edit_recipe.html', recipe=recipe, ingredients=ingredients, number_of_ingredients=number_of_ingredients, Product=Product, products=products)
    elif request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            filename = recipe.picture
        if file and Recipe.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            recipe.remove_picture()
            file.save(os.path.join(upload_folder, filename))

        recipe.name = request.form['recipe_name']
        recipe.description = request.form['description']
        recipe.time = request.form['time']
        recipe.picture = os.path.join("/static/img/uploads", filename)

        with DB() as db:
            # recipe.save()
            values = (recipe.name, recipe.description, recipe.time, recipe.picture, recipe.id)
            db.execute('UPDATE recipes SET name = ?, description = ?, time = ?, picture = ? WHERE id = ?', values)

            # Ingredient.delete_by_recipe(recipe.id)
            db.execute('DELETE FROM ingredients WHERE recipe_id = ?', (recipe.id,))


            ingredients = [
                None,
                recipe.id,
                None,
                None
            ]

            i = 1
            while(request.form.get('id_of_product' + str(i)) is not None):
                ingredients[2] = request.form.get('id_of_product' + str(i))
                ingredients[3] = request.form.get('quantity_of_product' + str(i))
                # Ingredient(*ingredients).create()
                values = (recipe.id, ingredients[2], ingredients[3])
                db.execute('INSERT INTO ingredients(recipe_id, product_id, quantity) VALUES (?, ?, ?)', values)
                i += 1
        
        return redirect(url_for('main.show_recipe', id=recipe.id))

@main.route('/my_recipes/<int:id>/delete', methods=['POST'])
@login_required
def delete_recipe(id):
    recipe = Recipe.find(id)
    if int(recipe.user_id) == current_user.id:
        recipe.remove_picture()
        recipe.delete()
        Ingredient.delete_by_recipe(recipe.id)

    return redirect(url_for('main.recipes'))




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
