from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import requests
from fpdf import FPDF

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
    instructions = data["meals"][0]["strInstructions"].encode('latin-1', 'replace').decode('latin-1')


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
        pdf.output("instructions.pdf")
        return render_template('recipe.html', name=name, category=category, area=area, ingredients=ingredients, instructions=instructions)
    get_recipe()
    return render_template('recipe.html', name=name, category=category, area=area, ingredients=ingredients, instructions=instructions)


if __name__ == "__main__":
    app.run(debug=True)
