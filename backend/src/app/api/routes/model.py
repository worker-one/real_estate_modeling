import logging
import pickle

import pandas as pd
from app.api import schemas
from app.db import crud
from fastapi import APIRouter
from geopy.distance import great_circle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Load models
model_files = {
    "xgb_1": './models/xgb_model_1.pkl',
    "xgb_2": './models/xgb_model_2.pkl',
    "mlp_1": './models/mlp_model_1.pkl'
}

models = {}
for model_name, model_path in model_files.items():
    with open(model_path, 'rb') as model_file:
        models[model_name] = pickle.load(model_file)

# Prediction function
def predict_user_input(user_input: schemas.PredictionRequest):
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

    try:
        # Prediction
        prediction = model.predict(input_df)
        return prediction[0]
    except Exception as e:
        raise e

# Define FastAPI endpoint
@router.post("/predict/")
def get_prediction(user_input: schemas.PredictionRequest):
    try:
        prediction = predict_user_input(user_input)
        logger.info(f"Prediction: {prediction}")
        return {"predicted_price_per_sqm": float(prediction)}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": "Prediction error"}
