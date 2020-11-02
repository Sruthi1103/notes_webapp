from flask import Flask, render_template, redirect, url_for,session
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import jsonify,request
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

app.secret_key="secret"
cluster=MongoClient("mongodb+srv://test:test@cluster0.duiwl.mongodb.net/User?retryWrites=true&w=majority")
#app.config['MONGO_URI'] = "mongodb://localhost:27017/User"
db=cluster.get_database('User')
mongo=db.user
n=db.notes
#mongo=PyMongo(app)

@app.route('/')
def index():
    if 'name' in session:
        notes = n.find({'name': session['name']})
        return render_template('index.html',notes=notes)
    else:
        return render_template('login.html')

##############################################################################################

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        _name = request.form['name']
        _password = request.form['pwd']
        exist = mongo.find_one({'name':_name})
        if exist:
            if check_password_hash(exist['pwd'],_password):
                session['name']=_name

                return redirect(url_for('index'))
    return render_template('login.html')

##############################################################################################

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':

        _name=request.form['name']
        _email = request.form['email']
        _password = request.form['pwd']
        users=mongo
        exist=users.find_one({'name':_name})
        if exist is None:
            #h_p = bcrypt.hashpw(_password.encode('utf-8'),bcrypt.genSalt())
            _hashed = generate_password_hash(_password)
            mongo.insert_one({'name': _name, 'email': _email, 'pwd': _hashed})
            session['name']=_name
            #return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
        return redirect(url_for('index'))
    return render_template('register.html')

##########################################################################################

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': "not found"+request.url
    }
    res=jsonify(message)
    res.status_code=404
    return res
############################################################################################

#####################################################################################################

@app.route('/add_notes',methods=['POST'])
def add_notes():
    _note = request.form['msg']
    if _note and request.method=='POST':
        n.insert_one({'name':session['name'],'note':_note})
    return redirect(url_for('index'))

#######################################################################################################

@app.route('/logout',methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))
##########################################################################################################

@app.route('/remove')
def remove_note():
    key=request.args.get("_id")
    n.remove({"_id":ObjectId(key)})
    return redirect(url_for('index'))


###################################################################################

if __name__ == '__main__':
    app.run(debug=True)