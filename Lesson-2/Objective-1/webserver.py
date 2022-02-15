from asyncore import read
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import os

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

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/restaurants':
            self.send_response(200)
            self.send_header('content-type', 'text/html; charset=utf-8')
            self.end_headers()

            restaurants = session.query(Restaurant).all()
            with open(os.path.join(__dirname__, './index.html')) as page:
                res = page.read()

            res_list = ''
            for restaurant in restaurants:
                res_list += f'<li>{restaurant.name}</li>'

            self.wfile.write(res.format(res_list).encode())

        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

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
