import logging
import os
from collections import defaultdict

import gradio as gr
import requests
from dotenv import find_dotenv, load_dotenv
from omegaconf import OmegaConf, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
env_path = find_dotenv(usecwd=True)
if env_path:
    load_dotenv(env_path)
else:
    logging.warning(".env file not found. Using default environment variables.")

# Retrieve environment variables with validation
base_url = os.getenv("BASE_URL", "http://localhost:8000")
if not base_url:
    logging.error("BASE_URL environment variable is not set.")
    raise EnvironmentError("BASE_URL environment variable is not set.")

# Load configuration with error handling
try:
    config = OmegaConf.load("./src/app/conf/config.yaml")
except FileNotFoundError:
    logging.error("Configuration file config.yaml not found.")
    raise
except ValidationError as e:
    logging.error(f"Configuration validation error: {e}")
    raise

def generate_chain_html(chain, pattern_type: str) -> str:
    """
    Generate HTML for a single chain based on the pattern type.
    """
    min_area = chain.get('min_area')
    max_area = chain.get('max_area')
    area_info = ""
    if min_area is not None and max_area is not None:
        area_info = f"<p><strong>Площадь:</strong> от {min_area} до {max_area} м²</p>"
    elif min_area is not None:
        area_info = f"<p><strong>Площадь:</strong> от {min_area} м²</p>"
    elif max_area is not None:
        area_info = f"<p><strong>Площадь:</strong> до {max_area} м²</p>"

    additional_info = ""
    if pattern_type == "facility":
        min_floor = chain.get('min_floor')
        max_floor = chain.get('max_floor')
        if min_floor == max_floor and max_floor is not None:
            additional_info += f"<p><strong>Этаж:</strong> {int(max_floor)}</p>"
        elif min_floor is not None and max_floor is not None:
            additional_info += f"<p><strong>Этажи:</strong> от {int(min_floor)} до {int(max_floor)}</p>"
        elif min_floor is not None:
            additional_info += f"<p><strong>Этажи:</strong> от {int(min_floor)}</p>"
        elif max_floor is not None:
            additional_info += f"<p><strong>Этажи:</strong> до {int(max_floor)}</p>"

        facility_fields = [
            ('high_vehicle_traffic', 'Высокий автомобильный трафик'),
            ('utilities', 'Наличие всех коммуникаций'),
            ('sanitary_facility', 'Наличие санитарного узла'),
            ('expected_visitors', 'Ожидаемое количество посетителей'),
            ('cargo_unloading', 'Возможность разгрузки грузового транспорта'),
            ('parking_available', 'Наличие парковки')
        ]
        for key, label in facility_fields:
            if chain.get(key):
                additional_info += f"<p><strong>{label}:</strong> Да</p>"
    elif pattern_type == "land":
        additional_info += f"<p><strong>Близость к жилому сектору:</strong> {'Да' if chain.get('near_residential_area') else 'Нет'}</p>"
        additional_info += f"<p><strong>Высокий автомобильный трафик:</strong> {'Да' if chain.get('high_vehicle_traffic') else 'Нет'}</p>"
        additional_info += f"<p><strong>Наличие всех коммуникаций:</strong> {'Да' if chain.get('utilities') else 'Нет'}</p>"

    return f"""
        <div style='border: 1px solid #ddd; border-radius: 10px; padding: 15px; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); transition: transform 0.3s;'>
            <h3 style='margin: 0; color: #333; font-size: 1.5em; font-weight: bold;'>{chain.get('chain', 'Unnamed Chain')}</h3>
            {area_info}
            {additional_info}
        </div>
    """

def format_eligible_chains(eligible_chains, pattern_type: str):
    if not eligible_chains:
        return "<h3 style='color: #555;'>Нет подходящих сетевых арендаторов</h3>"

    formatted_data = """
    <div style='margin-top: 20px; padding: 10px; background-color: #f9f9f9; 
                border: 1px solid #ddd; border-radius: 10px;'>
        <p>Для получения помощи в сдаче в аренду/продаже сетевым арендаторам - отправьте запрос на почту
            <a href='mailto:2049122@gmail.com'>2049122@gmail.com</a>
        </p>
    """

    category_dict = defaultdict(list)
    for chain in eligible_chains:
        category = chain.get('category', 'Uncategorized')
        category_dict[category].append(chain)

    formatted_data += "<div style='font-family: Arial, sans-serif;'>"
    for category in sorted(category_dict.keys()):
        formatted_data += f"<h2 style='color: #555;'>{category}</h2>"
        formatted_data += "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;'>"
        
        for chain in category_dict[category]:
            formatted_data += generate_chain_html(chain, pattern_type)
        formatted_data += "</div>"  # Close the chains grid for this category
    formatted_data += "</div>"  # Close the main container

    return formatted_data

def display_eligible_chains(eligible_chains, pattern_type: str):
    return gr.HTML(format_eligible_chains(eligible_chains, pattern_type))

def process_eligibility(user_input, endpoint: str, pattern_type: str):
    try:
        response = requests.post(f"{base_url}{endpoint}", json=user_input)
        response.raise_for_status()  # Raises HTTPError for bad responses
        eligible_chains = response.json().get("eligible_chains", [])
        logging.info(f"Eligible chains received: {eligible_chains}")
        return display_eligible_chains(eligible_chains, pattern_type)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return gr.HTML("<h3 style='color: red;'>Ошибка при проверке требований. Пожалуйста, попробуйте позже.</h3>")

def check_facility_eligibility(total_area, floor, ceiling_height, selected_criteria):
    user_input = {
        "total_area": total_area,
        "floor": floor,
        "ceiling_height": ceiling_height,
        "near_residential_area": "Находится ли вблизи жилого района с высоким пешеходным трафиком" in selected_criteria,
        "high_pedestrian_traffic": "Имеет ли высокий пешеходный трафик рядом" in selected_criteria,
        "high_vehicle_traffic": "Имеет ли высокий автомобильный трафик рядом" in selected_criteria,
        "nearby_facilities": "Есть ли в пределах 100 метров детские, образовательные, спортивные или медицинские учреждения" in selected_criteria,
        "utilities": "Есть ли все необходимые коммуникации (вода, электричество, канализация и т. д.)" in selected_criteria,
        "sanitary_facility": "Есть ли у объекта санитарный узел (туалет)" in selected_criteria,
        "expected_visitors": "Ожидается ли, что объект будет иметь как минимум 20,000 посетителей в день (для ТЦ)" in selected_criteria,
        "cargo_unloading": "Есть ли возможность разгрузки грузового транспорта на месте" in selected_criteria,
        "parking_available": "Имеется ли парковка у объекта недвижимости" in selected_criteria
    }
    logging.debug(f"Facility user input: {user_input}")
    return process_eligibility(user_input, "/eligibility/check/facility", "facility")

def check_land_eligibility(total_area, selected_criteria):
    user_input = {
        "total_area": total_area,
        "near_residential_area": "Близость к жилому сектору с высоким пешеходным трафиком" in selected_criteria,
        "high_vehicle_traffic": "Высокий автомобильный трафик" in selected_criteria,
        "utilities": "Наличие всех коммуникаций" in selected_criteria
    }
    logging.debug(f"Land user input: {user_input}")
    return process_eligibility(user_input, "/eligibility/check/land", "land")

def create_facility_tab():
    facility_inputs = [
        gr.Slider(label='Общая площадь (м²)', minimum=1, maximum=5000, value=100),
        gr.Slider(label='Этаж', minimum=0, maximum=100, value=1),
        gr.Slider(label='Высота потолков (м)', minimum=0, maximum=10, value=3),
        gr.CheckboxGroup(
            choices=[
                "Находится ли вблизи жилого района с высоким пешеходным трафиком",
                "Имеет ли высокий пешеходный трафик рядом",
                "Имеет ли высокий автомобильный трафик рядом",
                "Есть ли в пределах 100 метров детские, образовательные, спортивные или медицинские учреждения",
                "Есть ли все необходимые коммуникации (вода, электричество, канализация и т. д.)",
                "Есть ли у объекта санитарный узел (туалет)",
                "Ожидается ли, что объект будет иметь как минимум 20,000 посетителей в день (для ТЦ)",
                "Есть ли возможность разгрузки грузового транспорта на месте",
                "Имеется ли парковка у объекта недвижимости"
            ],
            label='Выберите соответствующие критерии',
            value=[]
        )
    ]
    facility_output = gr.HTML(label="Результат проверки")
    facility_submit_btn = gr.Button("Проверить объект")
    facility_submit_btn.click(fn=check_facility_eligibility, inputs=facility_inputs, outputs=facility_output)

    return gr.Column([
        *facility_inputs,
        facility_submit_btn,
        facility_output
    ])

def create_land_tab():
    land_inputs = [
        gr.Slider(
            label='Площадь земельного участка (м²)', minimum=0, maximum=10000,
            value=1000
        ),
        gr.CheckboxGroup(
            choices=[
                "Близость к жилому сектору с высоким пешеходным трафиком",
                "Высокий автомобильный трафик",
                "Наличие всех коммуникаций"
            ],
            label='Выберите соответствующие критерии',
            value=[]
        )
    ]
    land_output = gr.HTML(label="Результат проверки")
    land_submit_btn = gr.Button("Проверить участок")
    land_submit_btn.click(fn=check_land_eligibility, inputs=land_inputs, outputs=land_output)

    return gr.Column([
        *land_inputs,
        land_submit_btn,
        land_output
    ])

def create_eligibility_tab():
    with gr.TabItem("Проверка требований сетевых арендаторов"):
        gr.Markdown("## Проверка требований сетевых арендаторов")

        with gr.Tabs():
            with gr.TabItem("Проверка объекта недвижимости"):
                create_facility_tab()

            with gr.TabItem("Проверка земельного участка"):
                create_land_tab()
