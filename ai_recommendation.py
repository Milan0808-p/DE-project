from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

app = Flask(__name__)

# Sample dataset (Expanded for better predictions)
data = [
    # Loamy Soil Crops
    ["Loamy", 20, 50, "Corn"], ["Loamy", 22, 60, "Wheat"], ["Loamy", 25, 100, "Tomato"],
    ["Loamy", 26, 120, "Potato"], ["Loamy", 24, 90, "Maize"], ["Loamy", 28, 110, "Carrot"],
    ["Loamy", 30, 150, "Soybean"], ["Loamy", 27, 80, "Lettuce"], ["Loamy", 21, 55, "Spinach"],
    ["Loamy", 23, 70, "Cabbage"], ["Loamy", 29, 130, "Onion"], ["Loamy", 19, 45, "Peas"],

    # Clay Soil Crops
    ["Clay", 18, 180, "Rice"], ["Clay", 22, 200, "Sugarcane"], ["Clay", 25, 160, "Cotton"],
    ["Clay", 27, 140, "Soybean"], ["Clay", 23, 190, "Wheat"], ["Clay", 20, 170, "Lentil"],
    ["Clay", 29, 210, "Banana"], ["Clay", 24, 175, "Barley"], ["Clay", 26, 155, "Chickpea"],
    ["Clay", 21, 185, "Jute"], ["Clay", 30, 220, "Paddy"], ["Clay", 28, 200, "Peanuts"],

    # Sandy Soil Crops
    ["Sandy", 35, 50, "Millet"], ["Sandy", 38, 70, "Barley"], ["Sandy", 30, 65, "Chili"],
    ["Sandy", 32, 80, "Groundnut"], ["Sandy", 37, 55, "Watermelon"], ["Sandy", 34, 60, "Pumpkin"],
    ["Sandy", 33, 75, "Tomato"], ["Sandy", 36, 85, "Cassava"], ["Sandy", 40, 45, "Sesame"],
    ["Sandy", 39, 90, "Sunflower"], ["Sandy", 31, 100, "Sweet Potato"], ["Sandy", 29, 110, "Pineapple"],

    # Mixed Soil Crops (Combination of all soil types)
    ["Loamy", 24, 85, "Apple"], ["Clay", 26, 175, "Orange"], ["Sandy", 32, 95, "Mango"],
    ["Loamy", 21, 60, "Strawberry"], ["Clay", 28, 200, "Peach"], ["Sandy", 30, 75, "Grapes"],
    ["Loamy", 22, 70, "Avocado"], ["Clay", 25, 180, "Pomegranate"], ["Sandy", 33, 80, "Papaya"],
    ["Loamy", 20, 55, "Blueberries"], ["Clay", 27, 190, "Coconut"], ["Sandy", 38, 65, "Dragon Fruit"],

    # More Variety of Crops
    ["Loamy", 23, 100, "Pear"], ["Clay", 19, 170, "Guava"], ["Sandy", 35, 60, "Kiwi"],
    ["Loamy", 28, 110, "Almond"], ["Clay", 21, 200, "Cashew"], ["Sandy", 37, 50, "Cactus Pear"],
    ["Loamy", 24, 95, "Blackberry"], ["Clay", 30, 210, "Tamarind"], ["Sandy", 40, 55, "Dates"],
    ["Loamy", 22, 75, "Fig"], ["Clay", 29, 205, "Apricot"], ["Sandy", 36, 90, "Jackfruit"],

    # Special Cases
    ["Loamy", 20, 50, "Cucumber"], ["Clay", 26, 150, "Green Beans"], ["Sandy", 33, 100, "Lime"],
    ["Loamy", 27, 120, "Pumpkin"], ["Clay", 25, 180, "Melon"], ["Sandy", 30, 75, "Chia Seeds"],
    ["Loamy", 29, 140, "Rye"], ["Clay", 22, 175, "Teff"], ["Sandy", 35, 65, "Amaranth"],
    ["Loamy", 24, 95, "Triticale"], ["Clay", 31, 200, "Oats"], ["Sandy", 38, 85, "Buckwheat"]
]

df = pd.DataFrame(data, columns=["Soil", "Temperature", "Rainfall", "Crop"])

# Convert categorical data
df["Soil"] = df["Soil"].astype("category").cat.codes
df["Crop"] = df["Crop"].astype("category")  # Ensure it's categorical
df["Crop_Code"] = df["Crop"].cat.codes  # Store the corresponding category codes


X = df[["Soil", "Temperature", "Rainfall"]]
y = df["Crop_Code"]  # Use numerical crop labels for training


# Train model every time script runs
model = DecisionTreeClassifier()
model.fit(X, y)

# Save the model (overwrite old file)
joblib.dump(model, "crop_recommendation.pkl")

@app.route("/", methods=["GET"])
def home():
    return "Flask AI API is running!"


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json
        soil_type = data["soil"]
        temperature = data["temperature"]
        rainfall = data["rainfall"]

        # Load the trained model
        model = joblib.load("crop_recommendation.pkl")

        # Convert input soil type to numeric code
        soil_codes = {"Loamy": 0, "Clay": 1, "Sandy": 2}
        soil_input = soil_codes.get(soil_type, 0)

        # Predict using the model
        prediction = model.predict([[soil_input, temperature, rainfall]])[0]  # Get single prediction

        # Ensure Crop column is categorical before mapping
        df["Crop"] = df["Crop"].astype("category")

        # Create a mapping from category numbers to crop names
        crop_mapping = dict(enumerate(df["Crop"].cat.categories))

        # Convert predicted number to crop name
        predicted_crop = crop_mapping.get(int(prediction), "Unknown Crop")

        print("Crop categories mapping:", crop_mapping)  # Debugging
        print("Raw prediction output (number):", prediction)
        print("Final predicted crop (name):", predicted_crop)

        return jsonify({"recommended_crop": predicted_crop})  # Send crop name

    except Exception as e:
        print("Error:", str(e))  # Debugging
        return jsonify({"error": str(e)})





if __name__ == "__main__":
    app.run(debug=True, port=5000)
