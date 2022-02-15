from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from urllib.parse import parse_qs, urlparse

# import CRUD Operations from Lesson 1
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

__dirname__ = os.path.dirname(__file__)
host = 'http://localhost:8080'

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/restaurants':
            
            response = self.send_ok('index.html')

            restaurants = session.query(Restaurant).all()
            
            restaurants_list = ''
            for restaurant in restaurants:
                restaurants_list += f'\
                <div>\
                    <h2>{restaurant.name}</h2>\
                    <a href="{host}/restaurant/{restaurant.id}/edit">Edit</a>\
                    <a href="{host}/restaurant/{restaurant.id}/delete">Delete</a>\
                </div>\
                <hr>\
                '

            self.wfile.write(response.format(restaurants=restaurants_list).encode())

        elif self.path == ('/restaurant/new'):
            response = self.send_ok('new.html')

            self.wfile.write(response.format(host=host).encode())

        elif self.path.startswith('/restaurant') and self.path.endswith('/edit'):
            restaurant_id = int(self.path[1:].split('/')[1])
            restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

            response = self.send_ok('edit.html')
            self.wfile.write(response.format(host=host, restaurant=restaurant).encode())

        
        elif self.path.startswith('/restaurant') and self.path.__contains__('/delete'):

            if self.path.endswith('/delete'):
                restaurant_id = int(self.path[1:].split('/')[1])
                restaurant = session.get(Restaurant, restaurant_id)

                response = self.send_ok('delete.html')
                self.wfile.write(response.format(host=host, restaurant=restaurant).encode())

            elif self.path.__contains__('/delete?del='):
                restaurant_id = int(self.path[1:].split('/')[1])
                restaurant = session.get(Restaurant, restaurant_id)

                confirm_del = parse_qs(urlparse(self.path).query).get('del', ['False'])[0]
                if confirm_del == 'True':
                    session.delete(restaurant)
                    session.commit()

                    self.send_response(303)
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                    self.wfile.write('Restaurant {restaurant} deleted successfully'.format(restaurant=restaurant.name).encode())

        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        if self.path == ('/restaurant/new'):
            form = self.parse_form()
            
            restaurant_name = form.get('restaurant-name', [''])[0]
            if restaurant_name != ['']:
                new_restaurant = Restaurant(name=restaurant_name)
                session.add(new_restaurant)
                session.commit()
            
            self.send_response(303)
            self.send_header('Location', '/restaurants')
            self.end_headers()
            self.wfile.write('New restaurant {} added successfully'.format(new_restaurant).encode())

        elif self.path.startswith('/restaurant') and self.path.endswith('/edit'):
            form = self.parse_form()
            new_name = form.get('restaurant-name', [''])[0]
            restaurant_id = int(self.path[1:].split('/')[1])
            
            restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
            old_name = restaurant.name
            restaurant.name = new_name
            session.add(restaurant)
            session.commit()

            self.send_response(303)
            self.send_header('Location', '/restaurants')
            self.end_headers()

            self.wfile.write('{old_name} updated, now {new_name}'.format(old_name=old_name, new_name=new_name).encode())

        else:
            self.send_error(400, 'You posted your request to a wrong address.')

    def send_ok(self, file=None, response_code=200):
        self.send_response(response_code)
        self.send_header('content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if file:
            with open(os.path.join(__dirname__, file)) as html:
                    page = html.read()

            return page

    def parse_form(self):
        clength = int(self.headers.get('content-length', 0))
        data = self.rfile.read(clength).decode()
        form = parse_qs(data)
        
        return form

def main():
    try:
        server = HTTPServer(('', 8080), webServerHandler)
        print('Web server running...open localhost:8080/restaurants in your browser')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()
