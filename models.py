from app import db
from flask import session


class Dessert(db.Model):
    # See http://flask-sqlalchemy.pocoo.org/2.0/models/#simple-example
    # for details on the column types.

    # We always need an id
    id = db.Column(db.Integer, primary_key=True)

    # A dessert has a name, a price and some calories:
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    calories = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref="desserts")

    def __init__(self, name, price, calories, user_id):
        self.name = name
        self.price = price
        self.calories = calories
        self.user_id = user_id

    def calories_per_dollar(self):
        if self.calories:
            return self.calories / self.price


class Menu(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(250))
    name = db.Column(db.String(100))
    avatar = db.Column(db.String(250))

    def __init__(self, username, password, email, name, avatar):
        self.username = username
        self.password = password
        self.email = email
        self.name = name
        self.avatar = avatar


def get_password(username):
    user = User.query.filter_by(username=username).first()
    return user.password


def list_users():
    return User.query.all()


def get_user(id):
    return User.query.get(id)


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def create_user(username, email, password, realname, avatar):
    user = User(username, email, password, realname, avatar)
    db.session.add(user)
    db.session.commit()
    return user


def update_user(id, username=None, email=None, password=None, realname=None, avatar=None):

    user = User.query.get(id)

    if username:
        user.username = username

    if email:
        user.email = email

    if password:
        user.password = password

    if realname:
        user.realname = realname

    if avatar:
        user.avatar = avatar

    db.session.commit()
    return user


def login(username, password):
    # check if user exists in database
    user = get_user_by_username(username)
    if user is None:
        raise Exception("Sorry, we don't have your username on file.")

    # check if password is correct
    db_password = get_password(username)
    if password != db_password:
        raise Exception("Incorrect password.")

    # store username in Flask session
    session["username"] = username

    
def get_logged_in_user():

    # get stored username from Flask session
    current_user = session["username"]

    # get user object
    user = get_user_by_username(current_user)
    
    # return user object
    return user


def get_desserts_by_user(username):

    # get user object 
    user = get_user_by_username(username)

    # query all desserts matching id of user object
    desserts = Dessert.query.filter_by(user_id=user.id).all()
    return desserts


def edit_dessert(user, new_name, new_price, new_calories):
    
    # we need every piece of input to be provided
    if new_name is None or new_price is None or new_calories is None:
        raise Exception("Need name, price, and calories!")

    if new_name == '' or new_price == '' or new_calories == '':
        raise Exception("Need name, price, and calories!")

    # check reasonable number of calories
    if int(new_calories) < 100:
        raise Exception("That's not enough calories!")
    elif int(new_calories) > 3000:
        raise Exception("That's too many calories!")

    # get dessert from database
    dessert = Dessert.query.filter_by(name=new_name).first()

    # users can only edit their own desserts
    if user.id != dessert.user_id:
        raise Exception("That's not your dessert!")

    dessert.price = new_price
    dessert.calories = new_calories
    db.session.commit()


def create_dessert(new_name, new_price, new_calories, new_user_id):
    # Create a dessert with the provided input.

    # We need every piece of input to be provided.

    # Can you think of other ways to write this following check?
    if new_name is None or new_price is None or new_calories is None or new_user_id is None: 
        raise Exception("Need name, price, calories, and user!")

    # They can also be empty strings if submitted from a form
    if new_name == '' or new_price == '' or new_calories == '' or new_user_id == '':
        raise Exception("Need name, price, calories, and user!")
    
    # check for duplicate items
    name_check = Dessert.query.filter_by(name=new_name).first()
    if name_check:
        if new_name == name_check.name:
            raise Exception("That dessert already exists!")

    # check reasonable number of calories
    if int(new_calories) < 100:
        raise Exception("That's not enough calories!")
    elif int(new_calories) > 3000:
        raise Exception("That's too many calories!")

    # This line maps to line 16 above (the Dessert.__init__ method)
    dessert = Dessert(new_name, new_price, new_calories, new_user_id)
    # Actually add this dessert to the database
    db.session.add(dessert)

    # Save all pending changes to the database

    try:
        db.session.commit()
        return dessert
    except:
        # If something went wrong, explicitly roll back the database
        db.session.rollback()


def delete_dessert(user, id):

    # get dessert from database
    dessert = Dessert.query.get(id)

    # users can only delete desserts they created
    if user.id != dessert.user_id:
        raise Exception("That's not your dessert!")

    if dessert:
        # We store the name before deleting it, because we can't access it
        # afterwards.
        dessert_name = dessert.name
        db.session.delete(dessert)

        try:
            db.session.commit()
            return "Dessert {} deleted".format(dessert_name)
        except:
            # If something went wrong, explicitly roll back the database
            db.session.rollback()
            return "Something went wrong"
    else:
        return "Dessert not found"


if __name__ == "__main__":

    # Run this file directly to create the database tables.
    print "Creating database tables..."
    db.create_all()
    print "Done!"
