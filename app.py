# Chefs Companion - Application Entry Point
from flask import Flask, jsonify, request, render_template
from better_profanity import profanity
from textblob import TextBlob
import os
import uuid
from PIL import Image

# You may need to load the default wordlist once
profanity.load_censor_words()

app = Flask(__name__)

# In-memory data store for recipes
recipes_db = {
    "Spaghetti Carbonara": {
        "name": "Spaghetti Carbonara",
        "ingredients": ["Spaghetti", "Eggs", "Pancetta", "Parmesan Cheese", "Black Pepper"],
        "instructions": [
            "Cook spaghetti according to package directions.",
            "While spaghetti is cooking, cook pancetta in a large skillet until crispy.",
            "In a separate bowl, whisk together eggs, Parmesan cheese, and black pepper.",
            "Drain spaghetti and add it to the skillet with the pancetta.",
            "Remove from heat and stir in the egg mixture.",
            "Serve immediately."
        ],
        "ratings": [],
        "image_url": "https://www.fifteenspatulas.com/wp-content/uploads/2012/03/Spaghetti-Carbonara-Fifteen-Spatulas-12.jpg"
    },
    "Chicken Tikka Masala": {
        "name": "Chicken Tikka Masala",
        "ingredients": ["Chicken breast", "Yogurt", "Tomato sauce", "Onion", "Garlic", "Ginger", "Garam masala"],
        "instructions": [
            "Marinate chicken in yogurt and spices for at least 1 hour.",
            "Grill or pan-fry the chicken until cooked through.",
            "In a large saucepan, saute onion, garlic, and ginger until fragrant.",
            "Add tomato sauce and garam masala and simmer for 15 minutes.",
            "Add the cooked chicken to the sauce and simmer for another 10 minutes.",
            "Serve with rice and naan bread."
        ],
        "ratings": [],
        "image_url": "https://assets.bonappetit.com/photos/5b69f163d3d14670539a2174/1:1/w_2560%2Cc_limit/ba-tikka-masala-2.jpg"
    },
    "Classic Lasagna": {
        "name": "Classic Lasagna",
        "ingredients": ["Lasagna noodles", "Ground beef", "Ricotta cheese", "Mozzarella cheese", "Tomato sauce", "Onion", "Garlic"],
        "instructions": [
            "Preheat oven to 375°F (190°C).",
            "Cook lasagna noodles according to package directions.",
            "In a large skillet, cook ground beef and onion until browned. Add garlic and cook for another minute. Stir in tomato sauce.",
            "In a separate bowl, combine ricotta cheese, and half of the mozzarella cheese.",
            "Spread a thin layer of the meat sauce in the bottom of a 9x13 inch baking dish.",
            "Layer with noodles, ricotta mixture, and meat sauce. Repeat layers.",
            "Top with remaining mozzarella cheese.",
            "Bake for 30-40 minutes, or until bubbly and golden brown."
        ],
        "ratings": [],
        "image_url": "https://www.thewholesomedish.com/wp-content/uploads/2018/07/Best-Lasagna-550.jpg"
    },
    "Chocolate Chip Cookies": {
        "name": "Chocolate Chip Cookies",
        "ingredients": ["All-purpose flour", "Baking soda", "Salt", "Unsalted butter", "Granulated sugar", "Brown sugar", "Vanilla extract", "Eggs", "Semi-sweet chocolate chips"],
        "instructions": [
            "Preheat oven to 375°F (190°C).",
            "In a small bowl, whisk together flour, baking soda, and salt.",
            "In a large bowl, beat butter, granulated sugar, brown sugar, and vanilla extract until creamy.",
            "Add eggs, one at a time, beating well after each addition.",
            "Gradually beat in flour mixture.",
            "Stir in chocolate chips.",
            "Drop by rounded tablespoon onto ungreased baking sheets.",
            "Bake for 9 to 11 minutes or until golden brown.",
            "Cool on baking sheets for 2 minutes; remove to wire racks to cool completely."
        ],
        "ratings": [],
        "image_url": "https://cozycravings.com/wp-content/uploads/2024/11/DSC_6451-2.jpg"
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recipe/<string:recipe_name>')
def recipe_page(recipe_name):
    recipe = recipes_db.get(recipe_name)
    if recipe:
        return render_template('recipe.html', recipe=recipe)
    else:
        return jsonify({'error': f'Recipe with name "{recipe_name}" not found.'}), 404

@app.route('/recipes/popular')
def get_popular_recipes():
    """Retrieves the most popular recipes based on average rating."""
    if not recipes_db:
        return jsonify([])

    # Calculate average rating for each recipe
    for recipe in recipes_db.values():
        if recipe['ratings']:
            recipe['average_rating'] = sum(r['rating'] for r in recipe['ratings']) / len(recipe['ratings'])
        else:
            recipe['average_rating'] = 0

    # Sort recipes by average rating in descending order
    popular_recipes = sorted(recipes_db.values(), key=lambda r: r['average_rating'], reverse=True)
    return jsonify(popular_recipes)

@app.route('/recipes', methods=['POST'])
def add_recipe():
    """Adds a new recipe to the cook book"""
    recipe_data = request.get_json()
    if not recipe_data or 'name' not in recipe_data or 'ingredients' not in recipe_data or 'instructions' not in recipe_data:
        return jsonify({'error': 'Invalid recipe data. Required fields: name, ingredients, instructions'}), 400
    
    recipe_name = recipe_data['name']
    if recipe_name in recipes_db:
        return jsonify({'error': f'Recipe with name "{recipe_name}" already exists.'}), 409
    
    recipes_db[recipe_name] = {
        'name': recipe_name,
        'ingredients': recipe_data['ingredients'],
        'instructions': recipe_data['instructions'],
        'ratings': []
    }
    
    return jsonify({'message': f'Recipe "{recipe_name}" added successfully.'}), 201

@app.route('/recipes/<string:recipe_name>', methods=['GET'])
def get_recipe(recipe_name):
    """Retrieves a recipe by name."""
    recipe = recipes_db.get(recipe_name)
    if recipe:
        return jsonify(recipe)
    else:
        return jsonify({'error': f'Recipe with name "{recipe_name}" not found.'}), 404

@app.route('/recipes', methods=['GET'])
def get_all_recipes():
    """Retrieves all recipes."""
    return jsonify(list(recipes_db.values()))

UPLOAD_FOLDER = 'uploads/recipe_ratings'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure the upload directory exists

@app.route('/recipes/<string:recipe_name>/rate', methods=['POST'])
def rate_recipe(recipe_name):
    """Rates a recipe and processes an uploaded image."""
    recipe = recipes_db.get(recipe_name)
    if not recipe:
        return jsonify({'error': f'Recipe "{recipe_name}" not found.'}), 404

    # 1. Get rating and comment from the form fields
    if 'rating' not in request.form:
        return jsonify({'error': 'Invalid data. Required field: rating'}), 400
    
    # 2. Get the uploaded image file
    if 'image' not in request.files:
        return jsonify({'error': 'Invalid data. Required file: image'}), 400

    # 3. Validate rating (it will be a string from the form)
    try:
        rating = int(request.form['rating'])
        if not 1 <= rating <= 5:
            raise ValueError
    except ValueError:
        return jsonify({'error': 'Rating must be an integer between 1 and 5.'}), 400

    image_file = request.files['image']
    comment = request.form.get('comment', '')

    # 4. Process the image with Pillow to create a thumbnail
    try:
        img = Image.open(image_file.stream)
        img.thumbnail((256, 256)) # Create a 256x256 thumbnail
        
        # 5. Save the thumbnail with a unique filename
        _, ext = os.path.splitext(image_file.filename)
        thumbnail_filename = f"{uuid.uuid4().hex}{ext}"
        thumbnail_path = os.path.join(UPLOAD_FOLDER, thumbnail_filename)
        img.save(thumbnail_path)
    except Exception as e:
        return jsonify({'error': f'Failed to process image: {e}'}), 500

    # Sanitize comment and get sentiment
    sanitized_comment = profanity.censor(comment)
    sentiment = TextBlob(sanitized_comment).sentiment

    # 6. Store the rating data, including the path to the thumbnail
    recipe['ratings'].append({
        'rating': rating,
        'comment': sanitized_comment,
        'thumbnail': thumbnail_path, # Store the path to the saved image
        'sentiment': {
            'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity
        }
    })

    return jsonify({'message': f'Thank you for rating "{recipe_name}".'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
