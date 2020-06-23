# Project Description
This is a book review website where users can search and review books.

## Website Features

1. Users can register and log in.

2. Search books from a database of 5000 books using book name, author name or ISBN number.

3. Search results show book title, author name, publication year, ISBN Number and reviews by website users.

4. Search results also show book reviews from Goodreads website pulled using Goodreads API.

5. Review books by giving rating out of 5 and writing reviews. A user can review a book only once.

6. Make a GET request to the website's API route /api/<isbn>, the website returns a json response containing the book’s title, author, publication date, ISBN number, review count, and average score.
  
## Technologies Used

1. Website is built using Flask, a python based web framework which allows making dynamic web applications.
2. For front end HTML and CSS is used along with Bootstrap framework.
3. For backend a Postgres Database is built on Heroku which contains books data, users information and book reviews.
4. Python SQL Alchemy is used to write SQL queries and interact with the database.

## Website Demo
Demo Link: https://youtu.be/5eaUaYYfs1U
