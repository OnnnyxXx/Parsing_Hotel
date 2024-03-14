import sqlite3

import requests
import pymysql
from bs4 import BeautifulSoup
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""

Тут у меня проблема с MySql, времени было мало, поэтому будет Sqlite3 :)

"""


# Функция для создания базы данных SQLite и таблиц
def create_database():
    conn = sqlite3.connect('hotel_reviews.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS main_page_data (
                        id INTEGER PRIMARY KEY,
                        rating TEXT,
                        num_reviews TEXT,
                        num_ratings TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
                        id INTEGER PRIMARY KEY,
                        main_page_id INTEGER,
                        author TEXT,
                        rating TEXT,
                        review_text TEXT,
                        review_date TEXT)''')

    conn.commit()
    conn.close()


# Функция для внесения данных в базу данных SQLite
def insert_data_to_db(reviews_data, main_page_data):
    conn = sqlite3.connect('hotel_reviews.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO main_page_data (rating, num_reviews, num_ratings) VALUES (?, ?, ?)",
                   (main_page_data[0], main_page_data[1], main_page_data[2]))

    main_page_id = cursor.lastrowid

    for review_data in reviews_data:
        cursor.execute(
            "INSERT INTO reviews (main_page_id, author, rating, review_text, review_date) VALUES (?, ?, ?, ?, ?)",
            (main_page_id, review_data.get('author'), review_data.get('rating'), review_data.get('review_text'),
             review_data.get('date')))

    conn.commit()
    conn.close()


# Функция для получения всех авторов, отзывов и их время
def get_reviews_data(url):
    # Запускаем браузер
    driver = webdriver.Chrome()

    driver.get(url)

    show_all_reviews_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.button.button-yellow.button-black-text.toggle-reviews'))
    )
    show_all_reviews_button.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'review-item'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    reviews_data = []
    reviews = soup.find_all(class_='review-item')

    for review in reviews:
        author = review.find('div', class_='reviewer').text.strip().split('\n')[2].strip()
        rating = review.find('div', class_='rating')
        review_text = review.find('div', class_='review-pro').text
        review_date = review.find(class_='review-date')

        reviews_data.append({'author': author, 'rating': rating, 'review_text': review_text, 'date': review_date})

    for review_data in reviews_data:
        print(f"Author: {review_data['author']}")
        print(f"Rating: {review_data['rating']}")
        print(f"Review Text: {review_data['review_text']}")
        print(f"Date: {review_data['date']}")

    return reviews_data

    # Закрываем браузер
    driver.quit()


# Функция для получения рейтинга, количества отзывов и оценок
def get_main_page_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    rating = soup.find('span', class_='score').text
    num_reviews = soup.find('div', class_='count').find('span').text
    num_ratings = soup.find('div', class_='count').find_all('span')[1].text

    print(f'Гостиница Ахтуба (Рейтинг {rating} Кол-Отзывов {num_reviews} Оценок {num_ratings})')

    return f'Гостиница Ахтуба (Рейтинг {rating} Кол-Отзывов {num_reviews} Оценок {num_ratings})'


# Функция для вывода таблиц в консоль
def display_tables():
    conn = sqlite3.connect('hotel_reviews.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM main_page_data")
    print("Main Page Data:")
    for row in cursor.fetchall():
        print(row)

    cursor.execute("SELECT * FROM reviews")
    print("\nReviews:")
    for row in cursor.fetchall():
        print(row)

    conn.close()


create_database()

url = 'https://101hotels.com/main/cities/volzhskiy/gostinitsa_ahtuba.html'

reviews_data = get_reviews_data(url)

main_page_data = get_main_page_data(url)

insert_data_to_db(reviews_data, main_page_data)

display_tables()
