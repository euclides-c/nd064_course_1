import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from logging.config import dictConfig


# Function to get a database connection.
# This function connects to database with the name `database.db`

DB_CONNECTION_COUNTER = 0

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global DB_CONNECTION_COUNTER
    DB_CONNECTION_COUNTER+=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    # app.logger.info('Status request successfull')
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info('Article with id "%s" not found', post_id)
        return render_template('404.html'), 404
    else:
        app.logger.info('Article "%s" retrieved', post['title'])
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The "About" page is retrived')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('Article "%s" Created', title)

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthz():
    # check the connection object: try and catch loop, finally 

    try:
        connection = get_db_connection()
        posts = connection.execute('SELECT * FROM posts').fetchone()
        connection.close()
        response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
        return response

    except:
        response = app.response_class(
                response=json.dumps({"result":"ERROR - Unhealthy"}),
                status=500,
                mimetype='application/json'
        )
        return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()

    # connection count 
    response = app.response_class(
            response=json.dumps({"db_connection_count": DB_CONNECTION_COUNTER , "post_count": len(posts)}),
            status=200,
            mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
    dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(levelname)s %(name)s [%(asctime)s]:  %(message)s'
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },
    'stdout_handler': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    },
        'stderr_handler': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stderr',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi', 'stdout_handler', 'stderr_handler']
    }
})

#     ## stream logs to app.log file

#     loglevel = os.getenv("LOGLEVEL", "DEBUG").upper()
#     loglevel = (
#       getattr(logging, loglevel)
#       if loglevel in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
#       else logging.DEBUG
#   )

#   # Set logger to handle STDOUT and STDERR
#     stdout_handler = logging.StreamHandler(sys.stdout) # STDOUT handler
#     stderr_handler = logging.StreamHandler(sys.stderr) # STDERR handler
#     handlers = [stderr_handler, stdout_handler]

#   # format output
#     format_output = ('%(asctime)s - %(name)s - %(message)s') # formatting output here
#     logging.basicConfig(format=format_output, level=loglevel, handlers=handlers)
    app.run(host='0.0.0.0', port='3111')
