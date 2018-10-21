from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_content = db.Column(db.String(500))
    
    def __init__(self, blog_title, blog_content):
        self.blog_title = blog_title
        self.blog_content = blog_content

        
@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        
        blog_title = request.form['blog_title']
        blog_content = request.form['blog_content']

        blog_title_error = ''
        blog_content_error = ''

        if len(blog_title) < 1:
            blog_title_error = 'Blog post must have title'

        if len(blog_content) < 1:
            blog_content_error = 'Blog post must have content'

        if not blog_title_error and not blog_content_error:
            blog = Blog(blog_title, blog_content)
            db.session.add(blog)
            db.session.commit()
            return redirect('/all_posts?id='+str(blog.id))
        else:
            return render_template('new_post_form.html', title='New Post', blog_title=blog_title, blog_title_error=blog_title_error, blog_content=blog_content, blog_content_error=blog_content_error)

    blogs = Blog.query.all()

    return render_template('all_posts.html', title='Build a Blog!', blogs=blogs)

@app.route('/new_post_form', methods=['POST', 'GET'])
def new_post():

    return render_template('new_post_form.html', title='New Post')


@app.route('/all_posts', methods=['POST', 'GET'])
def blog_post():

    if request.args:
        id_num = request.args.get('id')
        blog = Blog.query.get(id_num)

        return render_template('indiposts.html', blog=blog)
    

if __name__ == '__main__':
    app.run()