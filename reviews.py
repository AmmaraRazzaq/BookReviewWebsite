import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute('CREATE TABLE reviews (id SERIAL PRIMARY KEY,\
	user_id INTEGER REFERENCES users,\
	book_id INTEGER REFERENCES books,\
	user_email VARCHAR NOT NULL,\
	rating INTEGER NOT NULL,\
	comment VARCHAR)')
db.commit()