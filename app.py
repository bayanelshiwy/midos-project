from flask import Flask, render_template, request, redirect, session, flash
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml
from werkzeug.security import generate_password_hash, check_password_hash
from _mysql_exceptions import IntegrityError



app = Flask(__name__)
Bootstrap(app)

#configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        userDetails = request.form
        useremail = userDetails['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(email, password) "\
        "VALUES(%s,%s)",(userDetails['email'],userDetails['password']))
        mysql.connection.commit()
        resultValue = cur.execute("SELECT * FROM user WHERE email = %s", ([useremail]))
        if resultValue > 0:
            user = cur.fetchone()
            if check_password_hash(user['password'], userDetails['password']):
                session['login'] = True
                session['email'] = user['email']
                return render_template('body.html')
            except IntegrityError:
            redirect(url_for('body.html'))
            else:
                cur.close()
                flash('Password does not match', 'danger')
                return render_template('home.html')
        else:
            cur.close()
            flash('User not found', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')
@app.route("/body/")
def body():
    db_records = range(1, 50)
    return render_template("body.html", db_records= db_records)

@app.route('/edit/')
def edit():
    return render_template('edit.html')

@app.route('/create/')
def create():
    return render_template('create.html')

if __name__ == '__main__':
    app.secret_key = '1234567'
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, port=8000)