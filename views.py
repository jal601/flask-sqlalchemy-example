from flask import render_template, request, session

from models import Dessert, create_dessert, delete_dessert, edit_dessert, login, get_logged_in_user
from app import app


@app.route('/', methods=["GET", "POST"])
def index():

    if request.method == 'GET':
        # if user is logged in, show only their desserts
        if "username" in session:
            user = get_logged_in_user()
            desserts = Dessert.query.filter_by(user_id=user.id).all()
            return render_template("menu.html", user=user.name, desserts=desserts)
        # if no user is logged in, show all desserts
        else:
            desserts = Dessert.query.all()
            return render_template("menu.html", user=None, desserts=desserts)

    # post method is user attempting to log in
    # get username and password from posted login form
    username = request.form.get('username_field')
    password = request.form.get('password_field')

    try:
        # login() from models.py
        login(username, password)
    except Exception as e:
        return render_template("index.html", error=e.message)

    # once logged in, show only user's desserts
    user = get_logged_in_user()
    desserts = Dessert.query.filter_by(user_id=user.id).all()
    return render_template("menu.html", user=user.name, desserts=desserts)
    

@app.route("/login")
def login_user():
    return render_template("index.html")


@app.route("/menu")    
def menu():
    user = get_logged_in_user()

    desserts = Dessert.query.filter_by(user_id=user.id).all()

    return render_template('menu.html', user=user.name, desserts=desserts)


@app.route("/logout")
def logout():
    session.pop('username',None)
    return index()

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):

    dessert = Dessert.query.get(id)

    if request.method == 'GET':
        if "username" in session:
            user = get_logged_in_user()
            return render_template('edit.html', user=user.name, dessert=dessert)
        else: 
            return render_template('details.html', user=None, dessert=dessert, error="You must be logged in to edit a dessert.")

    user = get_logged_in_user()

    dessert_name = dessert.name
    dessert_price = request.form.get('price_field')
    dessert_cals = request.form.get('cals_field')
    
    try:
        dessert = edit_dessert(user, dessert_name, dessert_price, dessert_cals)
        desserts = Dessert.query.filter_by(user_id=user.id).all()
        return render_template('menu.html', user=user.name, desserts=desserts)
    except Exception as e:
        return render_template('edit.html', user=user.name, dessert=dessert, error=e.message)
    

@app.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'GET':
        if "username" in session:
            user = get_logged_in_user()
            return render_template('add.html', user=user.name)
        else:
            desserts = Dessert.query.all()
            return render_template("menu.html", user=None, desserts=desserts, message="You must be logged in to add a dessert.")

    # Because we 'returned' for a 'GET', if we get to this next bit, we must
    # have received a POST

    # Get the incoming data from the request.form dictionary.
    # The values on the right, inside get(), correspond to the 'name'
    # values in the HTML form that was submitted.

    user = get_logged_in_user()
    dessert_name = request.form.get('name_field')
    dessert_price = request.form.get('price_field')
    dessert_cals = request.form.get('cals_field')
    
    # Now we are checking the input in create_dessert, we need to handle
    # the Exception that might happen here.

    # Wrap the thing we're trying to do in a 'try' block:
    try:
        dessert = create_dessert(dessert_name, dessert_price, dessert_cals, user.id)
        return render_template('add.html', user=user.name, dessert=dessert)
    except Exception as e:
        # Oh no, something went wrong!
        # We can access the error message via e.message:
        return render_template('add.html', error=e.message)


@app.route('/desserts/<id>')
def view_dessert(id):

    dessert = Dessert.query.get(id)

    if "username" in session:
        user = get_logged_in_user()
        return render_template('details.html', user=user.name, dessert=dessert)
    else:
        return render_template('details.html', user=None, dessert=dessert)


@app.route('/delete/<id>')
def delete(id):

    if "username" in session:
        user = get_logged_in_user()
        message = delete_dessert(user, id)
        return index()
    else:
        dessert = Dessert.query.get(id)
        return render_template('details.html', user=None, dessert=dessert, error="You must be logged in to delete a dessert.")
   

app.secret_key = "desserts_app!"
