import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("CREATE TABLE books (\
	id SERIAL PRIMARY KEY,\
	ISBN VARCHAR NOT NULL,\
	title VARCHAR NOT NULL,\
	author VARCHAR NOT NULL,\
	year INTEGER NOT NULL)")

f = open('books.csv')
reader = csv.reader(f)
next(reader)

for ISBN,title,author,year in reader:
	db.execute("INSERT INTO books (ISBN,title,author,year) VALUES (:ISBN, :title, :author, :year)",\
		{"ISBN":ISBN, "title":title, "author":author, "year":year})
print("Data inserted into table")
db.commit()