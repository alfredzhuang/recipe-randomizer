from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import requests
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time

MEAL_DB_URL = "https://www.themealdb.com/api/json/v1/1/random.php"

app = Flask(__name__)
app.config['SECRET_KEY'] = '908oajsfoafh129y41298h4r12'
Bootstrap(app)

name = ""
category = ""
area = ""
ingredients = []
instructions = ""


def get_recipe():
    response = requests.get(MEAL_DB_URL)
    data = response.json()
    global name, category, area, ingredients, instructions
    name = data["meals"][0]["strMeal"]
    category = data["meals"][0]["strCategory"]
    area = data["meals"][0]["strArea"]
    ingredients = []
    for i in range(1, 21):
        if data["meals"][0]["strIngredient" + str(i)] == "":
            break
        else:
            ingredients.append(data["meals"][0]["strMeasure" + str(i)] + " " + data["meals"][0]["strIngredient" + str(i)])
    instructions = data["meals"][0]["strInstructions"]
    instructions = instructions.replace(u'\u2013', '-')
    instructions = instructions.replace(u'\u2014', '-')
    instructions = instructions.replace(u'\u2019', "'")


def automated_cart(list_of_ingredients):
    chrome_drive_path = "C:\Development\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=chrome_drive_path)
    driver.maximize_window()
    driver.get("https://www.walmart.com/grocery")
    time.sleep(2)
    close_button = driver.find_element_by_xpath("html/body/div[2]/div/div/div/button")
    close_button.click()
    for ingredient in list_of_ingredients:
        try:
            search_field = driver.find_element_by_xpath("//*[@id='searchForm']/input")
            search_field.send_keys(str(ingredient))
            search_field.send_keys(Keys.ENTER)

            time.sleep(2)
            first_item = driver.find_element_by_class_name("AddToCart__addToCart___D6vAa")
            first_item.click()

            clear_button = driver.find_element_by_xpath("//*[@id='searchForm']/button[1]")
            clear_button.click()
        except NoSuchElementException:
            print("Couldn't find the ingredient")
            continue
    time.sleep(600)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/recipe", methods=["GET", "POST"])
def recipe():
    global name, category, area, ingredients, instructions
    if request.method == "POST":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 5, txt=instructions, align="C")
        pdf.output(name="instructions.pdf")
        return render_template('recipe.html', name=name, category=category, area=area, ingredients=ingredients, instructions=instructions)
    get_recipe()
    return render_template('recipe.html', name=name, category=category, area=area, ingredients=ingredients, instructions=instructions)


@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    global name, category, area, ingredients, instructions
    automated_cart(ingredients)
    return render_template('recipe.html', name=name, category=category, area=area, ingredients=ingredients, instructions=instructions)


if __name__ == "__main__":
    app.run(debug=True)
