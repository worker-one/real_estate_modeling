import pickle

import pandas as pd
from fastapi import FastAPI
from geopy.distance import great_circle
from pydantic import BaseModel
from xgboost import XGBClassifier

# Load models
with open('./models/xgb_model_1.pkl', 'rb') as model_file:
    xgb_model_1 = pickle.load(model_file)

with open('./models/xgb_model_2.pkl', 'rb') as model_file:
    xgb_model_2 = pickle.load(model_file)

with open('./models/mlp_model_1.pkl', 'rb') as model_file:
    mlp_model_1 = pickle.load(model_file)

models = {
    "xgb_1": xgb_model_1,
    "xgb_2": xgb_model_2,
    "mlp_1": mlp_model_1
}

# Define FastAPI app
app = FastAPI()

# Prediction function
def predict_user_input(user_input: PredictionRequest):
    model = models[user_input.model]

    input_data = {feature: 0 for feature in model.feature_names_in_}

    # Map numerical fields
    input_data['общая площадь'] = user_input.area
    input_data['этаж'] = user_input.floor
    input_data['время до станции'] = user_input.time_to_station
    input_data['Этажность дома'] = user_input.total_floors
    input_data['широта'] = user_input.latitude
    input_data['долгота'] = user_input.longitude

    # Set one-hot encoded fields
    state_feature = f"состояние_{user_input.condition}"
    if state_feature in input_data:
        input_data[state_feature] = 1

    district_feature = f"округ_{user_input.okrug}"
    if district_feature in input_data:
        input_data[district_feature] = 1

    metro_feature = f"метро_{user_input.metro}"
    if metro_feature in input_data:
        input_data[metro_feature] = 1

    walk_transit_feature = f"пешком/транспортом_{user_input.transport}"
    if walk_transit_feature in input_data:
        input_data[walk_transit_feature] = 1

    category_feature = f"категория объявления_{user_input.category}"
    if category_feature in input_data:
        input_data[category_feature] = 1

    # Convert dictionary into DataFrame for prediction
    input_df = pd.DataFrame([input_data])

    # Calculate distance from Moscow's center
    moscow_center_coords = (55.7558, 37.6173)
    input_df['distance_from_center'] = input_df.apply(
        lambda row: great_circle((row['широта'], row['долгота']), moscow_center_coords).kilometers, axis=1
    )

    # Prediction
    prediction = model.predict(input_df)
    return prediction[0]

# Define FastAPI endpoint
@app.post("/predict/")
def get_prediction(user_input: PredictionRequest):
    prediction = predict_user_input(user_input)
    return {"predicted_price_per_sqm": prediction}
