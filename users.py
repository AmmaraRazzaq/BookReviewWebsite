import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("CREATE TABLE users (\
	id SERIAL PRIMARY KEY,\
	name VARCHAR NOT NULL,\
	email VARCHAR NOT NULL,\
	password VARCHAR NOT NULL)")
db.commit()