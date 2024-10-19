from app.api import schemas
import pandas as pd


facility_column_mapping = {
    "Сеть": "chain",
    "Категория": "category",
    "min S кв м": "min_area",
    "max S кв м": "max_area",
    "Близость жилогого сектрора, высокий пешеходный трафик": "high_pedestrian_traffic",
    "Высокий автомобильный трафик": "high_vehicle_traffic",
    "В 100 метрах отсутствуют детские, образовательные, спортивные, медецинские объекты": "nearby_facilities",
    "Наличие всех коммуникации": "utilities",
    "Наличие сан. Узла": "sanitary_facility",
    "От 20 тыс. посетителей в день (для торговых центров)": "expected_visitors",
    "Возможность разгрузки грузового транспорта": "cargo_unloading",
    "Минимальная высота потолков в м.": "min_ceiling_height",
    "Наличие парковки": "parking_available",
    "Min floor": "min_floor",
    "Max floor": "max_floor"
}

facility_eligibility_table = pd.read_excel("./backend/data/facility.xlsx")
facility_eligibility_table.columns = [facility_column_mapping[column.strip()] for column in facility_eligibility_table.columns]
facility_eligibility_table.replace({'да': True}, inplace=True)


land_column_mapping = {
    "Сеть": "chain",
    "Категория": "category",
    "min S кв м": "min_area",
    "max S кв м": "max_area",
    "Близость жилогого сектора, высокий пешеходный трафик": "near_residential_area",
    "Высокий автомобильный трафик": "high_vehicle_traffic",
    "Наличие всех коммуникации": "utilities"
}

land_eligibility_table = pd.read_excel("./backend/data/land.xlsx")
land_eligibility_table.columns = [land_column_mapping[column.strip()] for column in land_eligibility_table.columns]
land_eligibility_table.replace({'да': True}, inplace=True)


def check_eligibility_facility(user_input: schemas.FacilityEligibilityRequest) -> list[dict[str, str]]:
    eligible_categories = []

    for _, criteria in facility_eligibility_table.iterrows():
        # Check each criterion only if the value is not NaN (None)
        is_eligible = True

        if pd.notna(criteria["min_area"]) and not (criteria["min_area"] <= user_input.total_area):
            is_eligible = False
        if pd.notna(criteria["max_area"]) and not (user_input.total_area <= criteria["max_area"]):
            is_eligible = False
        if pd.notna(criteria["min_floor"]) and not (criteria["min_floor"] <= user_input.floor):
            is_eligible = False
        if pd.notna(criteria["max_floor"]) and not (user_input.floor <= criteria["max_floor"]):
            is_eligible = False
        if pd.notna(criteria["high_pedestrian_traffic"]) and user_input.near_residential_area != criteria["high_pedestrian_traffic"]:
            is_eligible = False
        if pd.notna(criteria["high_vehicle_traffic"]) and user_input.high_vehicle_traffic != criteria["high_vehicle_traffic"]:
            is_eligible = False
        if pd.notna(criteria["nearby_facilities"]) and user_input.nearby_facilities != criteria["nearby_facilities"]:
            is_eligible = False
        if pd.notna(criteria["utilities"]) and user_input.utilities != criteria["utilities"]:
            is_eligible = False
        if pd.notna(criteria["sanitary_facility"]) and user_input.sanitary_facility != criteria["sanitary_facility"]:
            is_eligible = False
        if pd.notna(criteria["cargo_unloading"]) and user_input.cargo_unloading != criteria["cargo_unloading"]:
            is_eligible = False
        if pd.notna(criteria["min_ceiling_height"]) and user_input.ceiling_height < criteria["min_ceiling_height"]:
            is_eligible = False
        if pd.notna(criteria["parking_available"]) and user_input.parking_available != criteria["parking_available"]:
            is_eligible = False

        if is_eligible:
            # replace nan with None
            for key, value in criteria.items():
                if pd.isna(value):
                    criteria[key] = None
            eligible_categories.append(criteria)

    return eligible_categories


def check_eligibility_land(user_input: schemas.LandEligibilityRequest) -> list[dict[str, str]]:
    eligible_categories = []

    for _, criteria in land_eligibility_table.iterrows():
        is_eligible = True

        if pd.notna(criteria["min_area"]) and not (criteria["min_area"] <= user_input.total_area):
            is_eligible = False
        if pd.notna(criteria["near_residential_area"]) and user_input.near_residential_area != criteria["near_residential_area"]:
            is_eligible = False
        if pd.notna(criteria["high_vehicle_traffic"]) and user_input.high_vehicle_traffic != criteria["high_vehicle_traffic"]:
            is_eligible = False
        if pd.notna(criteria["utilities"]) and user_input.utilities != criteria["utilities"]:
            is_eligible = False

        if is_eligible:
            # replace nan with None
            for key, value in criteria.items():
                if pd.isna(value):
                    criteria[key] = None
            eligible_categories.append(criteria)

    return eligible_categories
