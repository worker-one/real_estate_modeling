import logging
import os

import gradio as gr
import requests
from constants import category_values, city_values, condition_values, metro_values, okrug_values, transport_values
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf

# Load configuration from config.yaml
config = OmegaConf.load("./src/app/conf/config.yaml")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv(usecwd=True))  # Load environment variables from .env file
base_url = os.getenv("BASE_URL", "http://localhost:8000")

def convert_address_to_coordinates(city, okrug, street, house_number, postal_code: str = None):
    if postal_code is None:
        postal_code = ""
    string_address = f"{city}, {okrug}, {street}, {house_number}, {postal_code}"
    key = "e048c59c-0358-470a-aaea-22f25b17b7f7"
    url = "https://catalog.api.2gis.com/3.0/items/geocode"
    params = {
        "q": string_address,
        "fields": "items.point,items.geometry.centroid",
        "key": key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "address_name" in data["result"]["items"][0].keys():
            print(logger.info(data["result"]["items"]))
            return {
                "address_name": data['result']['items'][0]['full_name'],
                "latitude": data['result']['items'][0]['point']['lat'],
                "longitude": data['result']['items'][0]['point']['lon']
            }
        else:
            return gr.Warning(f"Не удалось распознать адрес: {string_address}")
    else:
        return gr.Warning(f"Request failed with status code {response.status_code}. Please re-enter the address.")

def predict_user_input(*user_input_values):
    user_input_keys = [
        "category", "condition", "total_area", "floor", "floors_total",
        "time_to_station", "transport", "city", "okrug", "street", "house_number",
        "postal_code", "metro", "model", "radius"
    ]
    coordinates = convert_address_to_coordinates(*user_input_values[7:11])
    if not isinstance(coordinates, dict):
        return None, None, None, coordinates
    user_input = dict(zip(user_input_keys, user_input_values))

    user_input["latitude"] = coordinates["latitude"]
    user_input["longitude"] = coordinates["longitude"]
    request_data = {
        "metro": user_input["metro"],
        "okrug": user_input["okrug"],
        "city": user_input["city"],
        "category": user_input["category"],
        "condition": user_input["condition"],
        "area": user_input["total_area"],
        "floor": user_input["floor"],
        "total_floors": user_input["floors_total"],
        "time_to_station": user_input["time_to_station"],
        "transport": user_input["transport"],
        "latitude": user_input["latitude"],
        "longitude": user_input["longitude"],
        "model": user_input["model"]
    }

    # TODO: request the closest metro station if not provided
    if not request_data["metro"]:
        request_data["metro"] = "Полянка"

    # Request the predicted price
    response = requests.post(f"{base_url}/model/predict/", json=request_data)
    predicted_price = response.json()["predicted_price_per_sqm"]
    predicted_price = f"{predicted_price:.2f}".replace(".", ",") + " руб"

    location_request = {
        "latitude": user_input["latitude"],
        "longitude": user_input["longitude"],
        "radius": user_input["radius"]
    }

    # Request prices in the specified radius
    response = requests.post(f"{base_url}/data/prices_in_radius", json=location_request)
    data = response.json()
    if not data:
        return predicted_price, None, None, gr.Warning("Не удалось получить данные о ценах в радиусе")

    prices = [item["price_per_meter"] for item in data]

    max_price = max(prices)
    min_price = min(prices)
    max_price = f"{max_price:.2f}".replace(".", ",") + " руб"
    min_price = f"{min_price:.2f}".replace(".", ",") + " руб"

    return predicted_price, max_price, min_price, gr.Info(f"Адрес распознан: {coordinates['address_name']}")

def create_price_prediction_tab():
    with gr.TabItem("Стоимость недвижимости"):
        gr.Markdown(f"""
        # {config.TITLE}
        ### {config.DESCRIPTION}
        """)

        inputs = []
        with gr.Row():
            with gr.Column():
                with gr.Accordion(config.DETAILS_SECTION):
                    inputs.append(
                        gr.Dropdown(
                            choices=category_values,
                            label="Категория объявления",
                            value=category_values[0]
                        )
                    )
                    inputs.append(
                        gr.Dropdown(
                            choices=condition_values,
                            label="Состояние",
                            value=condition_values[0]
                            )
                        )
                    inputs.append(gr.Slider(label='Общая площадь (м²)', minimum=10, maximum=800, value=30, step=1))
                    inputs.append(gr.Slider(label='Этаж', minimum=1, maximum=100, value=2, step=1))
                    inputs.append(gr.Slider(label='Этажность дома', minimum=1, maximum=100, value=5, step=1))
                    inputs.append(gr.Slider(label='Время до станции (минуты)', minimum=1, maximum=60, value=5, step=1))
                    inputs.append(gr.Dropdown(choices=transport_values, value="пешком", label='До станции'))

            with gr.Column():
                with gr.Accordion(config.LOCATION_SECTION):
                    inputs.append(gr.Dropdown(choices=city_values, label="Город", value="Москва"))
                    inputs.append(gr.Dropdown(choices=okrug_values, label="Округ", value="ЦАО"))
                    inputs.append(gr.Textbox(label='Улица'))
                    inputs.append(gr.Number(label='Номер дома'))
                    inputs.append(gr.Textbox(label='Почтовый индекс', value=None, placeholder="Необязательно"))
                    inputs.append(gr.Dropdown(choices=metro_values, label="Метро"))

        with gr.Accordion(config.MODEL_SELECTION_SECTION):
            model_selection = gr.Radio(choices=["xgb_1", "xgb_2", "mlp_1"], label="Выберите модель")

        gr.Markdown("---")
        radius_slider = gr.Slider(label='Радиус (км)', minimum=0.5, maximum=2, value=1, step=0.1)
        submit_btn = gr.Button(config.PREDICT_BUTTON_LABEL, variant="primary")
        output_max_price = gr.Textbox(label="Максимальная цена за м² в радиусе")
        output_min_price = gr.Textbox(label="Минимальная цена за м² в радиусе")
        output_price = gr.Textbox(label="Предполагаемая цена за м²")
        submit_btn.click(
            fn=lambda *args: predict_user_input(*args[:-1], args[-1]),
            inputs=inputs + [model_selection, radius_slider],
            outputs=[output_price, output_max_price, output_min_price]
        )
