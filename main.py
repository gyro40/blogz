from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password2@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_content = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_username = db.Column(db.String(20))

    def __init__(self, blog_title, blog_content, owner, owner_username):
        self.blog_title = blog_title
        self.blog_content = blog_content
        self.owner = owner
        self.owner_username = owner_username

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():

    allowed_routes = ['login', 'register', 'blog', 'index', 'blog_post']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':

        owner = User.query.filter_by(username=session['username']).first()
        owner_username = owner.username

        blog_title = request.form['blog_title']
        blog_content = request.form['blog_content']

        blog_title_error = ''
        blog_content_error = ''

        if len(blog_title) < 1:
            blog_title_error = 'Blog must have a title'

        if len(blog_content) < 1:
            blog_content_error = 'Blog post must have content'

        if not blog_title_error and not blog_content_error:
            blog = Blog(blog_title, blog_content, owner, owner_username) 
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog_post?id='+ str(blog.id))
        else:
            return render_template('newpost.html', title='New Post', blog_title=blog_title, blog_title_error=blog_title_error, blog_content=blog_content, blog_content_error=blog_content_error)   

    blogs = Blog.query.all()

    if request.args:
        user_id = request.args.get('user_id')
        blogs = Blog.query.filter_by(owner_id=user_id).all()


    return render_template('blog.html', title="Blogz!!", blogs=blogs)

@app.route('/')
def index():

    authors = User.query.all()

    return render_template('index.html', authors=authors)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    return render_template('newpost.html', title='New Post')

@app.route('/blog_post', methods=['POST', 'GET'])
def blog_post():
        
    if request.args:
        id_num = request.args.get('id')
        blog = Blog.query.get(id_num)

        return render_template('indypost.html', blog=blog)

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        if user and user.password != password:
            flash('Incorrect password', 'error')
            return redirect('/login')
        else: 
            flash('User does not exist', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/register', methods=['POST', 'GET'])
def register():
    
    if request.method == 'POST':
        
        invalid_char = ' '

        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''

        # TODO validate user's data

        if len(username) == 0:
            username = ''
            username_error = "Username cannot be blank"

        if len(username) > 0:

            if len(username) < 3 or len(username) > 20:
                username = ''
                username_error = "Username must be between 3 and 20 characters"
            for char in username:
                if char in invalid_char:
                    username = ''
                    username_error = "Invalid Username"
        
        if len(password) == 0:
            password = ''
            password_error = "Error: Password cannot be blank"

        for char in password:
            if char in invalid_char:
                password = ''
                password_error = "Error: Password cannot contain spaces"

        if len(verify) == 0:
            verify = ''
            verify_error = "Error: Field cannot be blank"
        elif verify != password:
            verify = ''
            verify_error = "Error: Passwords don't match"

        if username_error or password_error or verify_error:
            return render_template('register.html', username=username, username_error=username_error, password=password, password_error=password_error, verify_error=verify_error)



        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            flash('Success!')
            return redirect('/newpost')
        else:
            return '<h1>Duplicate User</h1>'

    return render_template('register.html')

if __name__ == '__main__':
    app.run()