from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import bitly_api


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///links.db'
db = SQLAlchemy(app)
con = bitly_api.Connection(access_token="f0e935e6d2a8898e26acc2323b7ca1b7296e32ae")


class Elem(db.Model):
    ident = db.Column(db.Integer, primary_key=True)
    old_url = db.Column(db.String(500), nullable=False)
    new_url = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return '<Table %r>' % self.ident


def change_url(old_url):
    new_url = con.shorten(old_url)['url']
    return new_url


@app.route('/', methods=['POST', 'GET'])
def index():
    elem = None
    if request.method == "POST":
        input_url = request.form['url']
        if input_url == "":
            return redirect(url_for('error'))
        output_url = change_url(input_url)
        elem = Elem(old_url=input_url, new_url=output_url)
        try:
            db.session.add(elem)
            db.session.commit()
            elem = output_url
        except:
            error()
    articles = Elem.query.order_by(Elem.ident.desc()).all()
    return render_template("index.html", articles=articles, elem=elem)


@app.route('/info')
def post():
    articles = Elem.query.order_by(Elem.ident.desc()).all()
    return render_template("post.html", articles=articles)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/Error')
def error():
    return 'Error! You have entered a blank line!'


if __name__ == "__main__":
    app.run(debug=False)