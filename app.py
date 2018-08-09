from flask import Flask , request, render_template , redirect , url_for , jsonify , session ,g
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict as od
from wtforms import Form, StringField, validators
import unicodedata
import os
from functools import wraps



# Constants

POST = ["POST"]
PUT = ["PUT"]
GET = ["GET"]
DELETE = ["DELETE"]

# APP CONFIGURATIONS
app = Flask(__name__,static_url_path="/static", static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/store'
app.secret_key = os.urandom(24)


# Connecting to Sqlalchemy # it handles db connections very 
db = SQLAlchemy(app)

Bootstrap(app)



#Models

class User(db.Model):
	__tablename__ = 'user'
	username = db.Column(db.String(20) , primary_key=True)
	password=  db.Column(db.String(50))
	email  = db.Column(db.String(50))
	role = db.Column(db.Boolean())




class Inventory_(db.Model):
	__tablename__ = 'inventory'
	productId = db.Column(db.String(20) , primary_key=True)
	productName  = db.Column(db.String(50))
	vendor = db.Column(db.String(50))
	MRP = db.Column(db.Integer())
	batchNum = db.Column(db.String(50)) 
	batchDate = db.Column(db.String(50)) # can be datetime object 
	quantity = db.Column(db.String(50))
	status = db.Column(db.String(50))  # can be store as enum type for simplicity using string


# Forms

class InventoryForm(Form):
    productId = StringField('Product Id')
    productName = StringField('Product Name')
    vendor = StringField('Vendor')
    MRP = StringField('MRP')
    batchNum = StringField('Batch Number')
    batchDate = StringField('BatchDate')
    quantity = StringField('Quantity')






# Endpoints - User



@app.route('/')
def index():
	if "username" in session:
		user = User.query.filter_by(username=session['username']).first()
		if user is not None and user.role :
			return redirect(url_for('approval'))
		elif user is not None and user.role==False:
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))

@app.before_request
def before_request():
	g.username = None
	g.role = None

	if 'username' in session :
		g.username = session['username']
	if 'role' in session :
		g.role = session['role']

	pass

@app.route("/login" , methods=POST+GET)
def login():
	if request.method == 'POST':
		pwd = request.form["pwd"]
		email = request.form["email"]
		user = User.query.filter_by(email=email.strip()).first()
		if user is not None and user.password == pwd:
			session["username"]  = user.username
			session["role"] = user.role
			role = user.role
			if role == True :
				return redirect(url_for('approval'))
			else : return redirect(url_for("dashboard"))
	return render_template("login.html")



# Endpoints - Inventory


@app.route("/add_product", methods=["POST" , "GET"])
def add_product():
	form = InventoryForm(request.form)
	if request.method == "POST":
		data = request.form
		productId=data['productId'],
		productName=data['productName']
		vendor=data['vendor']
		MRP=data['MRP']
		batchNum=data['batchNum']
		batchDate=data['batchDate']
		quantity=data['quantity']
		status="PENDING"
		#print  productId, productName, vendor, MRP, batchNum, batchDate, quantity, status
		new_product =  Inventory_(
			 productId=productId,
			 productName=productName,
			 vendor=vendor,
			 MRP=MRP,
			 batchNum=batchNum,
			 batchDate=batchDate,
			 quantity=quantity,
			 status=status
			 )
		db.session.add(new_product)
		db.session.commit()
		return redirect(url_for('dashboard'))
		
	return render_template("add_product.html",form=form)


@app.route("/edit_product/<string:_id>", methods=["POST" , "GET"])

def edit_product_(_id):

	#('batchNum', u'asdk'), ('vendor', u'ME'), ('productId', u'pr3'), ('quantity', u'39'), ('MRP', u'203'), ('batchDate', u'123490921'), ('productName', u'pr3')
	_id  = unicodedata.normalize('NFKD', _id).encode('ascii','ignore')
	product = Inventory_.query.filter_by(productId=_id).first()	
	form = InventoryForm(request.form)
	form.productName.data = unicodedata.normalize('NFKD', product.productName).encode('ascii','ignore')
	form.vendor.data=product.vendor
	form.MRP.data=product.MRP
	form.batchNum.data=product.batchNum
	form.batchDate.data=product.batchDate
	form.quantity.data=product.quantity

	# print "----------------------- :",product.productId

	if request.method == "POST":
		data = request.form		
		productName=data['productName']
		vendor=data['vendor']
		MRP=data['MRP']
		batchNum=data['batchNum']
		batchDate=data['batchDate']
		quantity=data['quantity']
		status="PENDING"
		
		if data.has_key('productName'):product.productName = productName
		if data.has_key('vendor'):product.vendor = vendor
		if data.has_key('MRP'):product.MRP = MRP
		if data.has_key('batchNum'):product.batchNum = batchNum
		if data.has_key('batchDate'):product.batchDate = batchDate
		if data.has_key('quantity'):product.quantity = quantity

		db.session.commit()
		return redirect(url_for('dashboard'))
		
	return render_template("edit_product_item.html",form=form)







@app.route("/dashboard")

def dashboard():
	return render_template("dashboard.html")


@app.route("/edit_product")
def get_product_list():
	inventory_data = Inventory_.query.filter_by(status="PENDING").all()
	data = []
	ids=  []
	for item in inventory_data:		
		tmp = item.productId + " - "+ item.productName
		id_ = item.productId		
		data.append(tmp)
		ids.append(id_)
	len_ = len(data)
	return render_template("product_dashboard.html", data=data, ids=ids, len=len_)
	


@app.route("/approval")
def approval():

	print g
	if g.username is None :
		return redirect(url_for('login'))

	elif g.role == False :
		return redirect(url_for('dashboard'))

	else:
		return render_template('Approval.html' , data=get_approval_data())



@app.route("/update", methods=["PUT"])
def update():
	data = request.get_json()
	try:		
		for i in Inventory_.query.filter(Inventory_.productId.in_(data)).all() :
			i.status = "APPROVED"
		db.session.commit()
	except Exception as e:
		jsonify( {
			'status' : 500,
			'message' : 'Bulk update failed'
			})
	finally:
		pass

	return jsonify({})



	 #.update({Inventory_.status : 'APPROVED'})

	db.session.commit()


# Utils & Debug endpoints

def get_inventory_data():
	inventory_data = Inventory_.query.filter_by(status="PENDING").all()
	data = []
	for inv in inventory_data:
		item = {}
		item['productId'] = inv.productId
		item['productName'] = inv.productName
		item['vendor'] = inv.vendor
		item['quantity'] = inv.quantity
		item['status'] = inv.status 
		data.append(item)
	return data

@app.route("/data") 
def get_approval_data():
	data = get_inventory_data()
	return jsonify(data)



if __name__=='__main__':
	app.run(port=80 , threaded=True,debug=True)