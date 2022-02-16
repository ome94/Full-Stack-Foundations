from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id=None):
    output = ''

    if restaurant_id is None:
        restaurants = session.query(Restaurant).all()
        output += '<h1>All restaurants</h1>'

        for restaurant in restaurants:
            output += f'<h2>{restaurant.name}</h2>'
            
            items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
            for i in items:
                output += i.name
                output += '</br>'
                output += i.price
                output += '</br>'
                output += i.description
                output += '</br>'
                output += '</br>'
        
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        output += f'<h1>{restaurant.name}</h2>'
        items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
        for i in items:
            output += i.name
            output += '</br>'
            output += i.price
            output += '</br>'
            output += i.description
            output += '</br>'
            output += '</br>'

    return output

# Task 1: Create route for newMenuItem function here

@app.route('/restaurant/new/')
def newMenuItem():
    return "page to create a new menu item. Task 1 complete!"

# Task 2: Create route for editMenuItem function here

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    return "page to edit a menu item. Task 2 complete!"

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
