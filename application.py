import os

import requests
import statistics
from flask import Flask, session, render_template, request, jsonify, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

KEY = os.getenv("KEY")

@app.route("/")
def index():
	if session.get('email'):
		return render_template("login.html")

	return render_template("index.html", registerError="", loginError="")



@app.route("/register", methods=["POST"])
def register():
	name = request.form.get("name")
	email = request.form.get("email")
	password = request.form.get("password")
	# A user should not be able to register with the same email again, same name or password should be no problem
	if db.execute("SELECT * FROM users WHERE email=:email",{"email":email}).rowcount!=0:
		return render_template("index.html",registerError="User Already Exists: Try Logging In", loginError="")

	db.execute("INSERT INTO users (name,email,password) VALUES(:name,:email,:password)",{"name":name,"email":email,"password":password})
	db.commit()

	session['email'] = email
	session['username'] = name
	return render_template("login.html", username=name, logout="LogOut")




@app.route("/hello", methods=["POST","GET"])
def login():
	if request.method == "GET":
		return redirect(url_for('home'))

	email = request.form.get("email")
	password = request.form.get("password")

	#when someone logs in using their email and password, maybe recover their username from data base to show
	# in header bar and also in comments section. 

	session['email'] = email

	# if db.execute("SELECT * FROM users WHERE email=:email AND password=:password",{"email":email,"password":password}).rowcount==0:
	# 	return render_template("error.html", message="Email or password is incorrect")

	user = db.execute('SELECT * FROM users WHERE email=:email AND password=:password',{"email":email,"password":password}).fetchone()
	if user is None:
		return render_template("index.html", registerError="", loginError="Email or password is incorrect")
	# otherwise, user is found so log them in
	session['username'] = user.name
	return render_template("login.html", message="", username=user.name, logout="LogOut")


@app.route("/logout")
def logout():
	session.clear()
	return redirect(url_for('home'))


@app.route("/home")
def home():
	if session.get('email'):
		return render_template("login.html", username=session.get('username'), logout="LogOut")

	return render_template("index.html") 	
	



@app.route("/searchforbooks")
def search():
	if session.get('email'):
		return render_template("login.html", username=session.get('username'), logout="LogOut")

	return render_template("index.html", loginError="Log In or register to search for books")




@app.route("/searchresult", methods=["POST","GET"])
def result():
	if request.method == "GET":
		return redirect(url_for('home'))

	isbn_number = request.form.get("isbn")
	book_title = request.form.get("title")
	author_name = request.form.get("author")

	if isbn_number:
		books = db.execute("SELECT * FROM books WHERE ISBN LIKE :isbn",{"isbn":f'%{isbn_number}%'}).fetchall()
		if books:
			return render_template("result.html", books=books, username=session.get('username'), logout="LogOut")
		return render_template("login.html",message="Book Not Found", username=session.get('username'), logout="LogOut")
		

	if book_title:
		books = db.execute("SELECT * FROM books WHERE title LIKE :title",{"title":f'%{book_title}%'}).fetchall()
		if books:
			return render_template("result.html", books=books, username=session.get('username'), logout="LogOut")
		return render_template("login.html",message="Book Not Found", username=session.get('username'), logout="LogOut")
		

	if author_name:
		books = db.execute("SELECT * FROM books WHERE author LIKE :author",{"author":f'%{author_name}%'}).fetchall()
		if books:
			return render_template("result.html", books=books, username=session.get('username'), logout="LogOut")
		return render_template("login.html",message="Book Not Found", username=session.get('username'), logout="LogOut")
		





@app.route("/book/<int:book_id>", methods=["GET","POST"])
def book(book_id):
	
	user_email = session.get('email')
	#the book exists this check is being performed to avoid the website to crash and display some sort of error message
	book = db.execute("SELECT * FROM books WHERE id=:id",{"id":book_id}).fetchone()
	if book is None:
		return render_template("login.html", message="Book Not Found", username=session.get('username'), logout="LogOut")
	#book is found, fetch its reviews
	reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book_id}).fetchall() 
	#fetch reviews from Good Reads API as well
	#JSON has key,value pairs. books is the key, its value is a list, the only list, so it can be accessed with index 0.
	#in that list are many key, value pairs, which can be accesses using keys
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": book.isbn})
	if res.status_code!=200:
		raise Exception("Error: API request unsuccessful")
	data = res.json()
	avg_rating = data['books'][0]['average_rating']
	num_rating = data['books'][0]['work_ratings_count']
	

	#If user reviews a book
	if request.method == "POST":		
		rating = request.form.get('rating')
		comment = request.form.get('comment')
		
		#check if user has reviewed this book before
		if db.execute("SELECT * FROM reviews WHERE book_id=:book_id AND user_email=:user_email",{"book_id":book_id,"user_email":user_email}).rowcount==0:
			#user has not reviewed this book before

			db.execute('INSERT INTO reviews (user_email,book_id,rating,comment) VALUES(:user_email,:book_id,:rating,:comment)',\
			{"user_email":user_email,"book_id":book_id,"rating":rating,"comment":comment} )
			db.commit()
			reviews1 = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book_id}).fetchall()
			return render_template("bookinfo.html",reviews=reviews1, book=book, message="review added successfully",num_rating=num_rating,avg_rating=avg_rating, username=session.get('username'), logout="LogOut")

		#otherwise, user has already reviewed the book so can't review again
		return render_template("bookinfo.html",reviews=reviews, book=book, message="you have already reviewed this book before",data=data,num_rating=num_rating,avg_rating=avg_rating, username=session.get('username'), logout="LogOut")

	#user did not review the book
	return render_template("bookinfo.html",reviews=reviews,book=book, message="User reviews are displayed here",data=data,num_rating=num_rating,avg_rating=avg_rating,username=session.get('username'), logout="LogOut")




#creating an api
@app.route("/api/<string:isbn>")
def bookapi(isbn):
	book = db.execute("SELECT * FROM books WHERE ISBN=:isbn",{"isbn":isbn}).fetchone()
	if book is None:
		return jsonify({"error": "Book with this isbn does not exist"}), 404
	
	reviews = db.execute("SELECT * FROM reviews JOIN books ON reviews.book_id=books.id").fetchall()
	if reviews is None:
		review_count=0
		avg_score=0

	rating = []
	for review in reviews:
		rating.append(review.rating)

	#avg_score = statistics.mean(rating)
	review_count = len(rating)

	#return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.
	return jsonify({
		"title":book.title,
		"author":book.author,
		"publication date":book.year,
		"ISBN number":book.isbn,
		"review count":review_count
		})