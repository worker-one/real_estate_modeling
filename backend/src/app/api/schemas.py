from typing import List, Optional

from pydantic import BaseModel, Field, conint, constr


class ItemBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    name: str
    items: List[Item] = []

    class Config:
        orm_mode = True

class Message(BaseModel):
    message: str

# Input schema for prediction request
class PredictionRequest(BaseModel):
    metro: str
    okrug: str
    city: str
    category: str
    condition: str
    area: float
    floor: int
    total_floors: int
    time_to_station: int
    transport: str
    latitude: float
    longitude: float
    model: str

class FacilityEligibilityRequest(BaseModel):
    total_area: conint(ge=1) = Field(..., description="Общая площадь объекта недвижимости в квадратных метрах")
    floor: conint(ge=0) = Field(..., description="Этаж объекта (0 - цоколь)")
    near_residential_area: bool = Field(..., description="Находится ли вблизи жилого района с высоким пешеходным трафиком")
    high_pedestrian_traffic: bool = Field(..., description="Имеет ли высокий пешеходный трафик рядом")
    high_vehicle_traffic: bool = Field(..., description="Имеет ли высокий автомобильный трафик рядом")
    nearby_facilities: bool = Field(..., description="Есть ли в пределах 100 метров детские, образовательные, спортивные или медицинские учреждения")
    utilities: bool = Field(..., description="Есть ли все необходимые коммуникации (вода, электричество, канализация и т. д.)")
    sanitary_facility: bool = Field(..., description="Есть ли у объекта санитарный узел (туалет)")
    expected_visitors: bool = Field(..., description="Ожидается ли, что объект будет иметь как минимум 20,000 посетителей в день (для ТЦ)")
    cargo_unloading: bool = Field(..., description="Есть ли возможность разгрузки грузового транспорта на месте")
    ceiling_height: conint(ge=0) = Field(..., description="Высота потолков в метрах")
    parking_available: bool = Field(..., description="Имеется ли парковка у объекта недвижимости")

class LandEligibilityRequest(BaseModel):
    total_area: conint(ge=0) = Field(..., description="Площадь земельного участка (ЗУ) в квадратных метрах")
    near_residential_area: bool = Field(..., description="Близость к жилому сектору с высоким пешеходным трафиком")
    high_vehicle_traffic: bool = Field(..., description="Высокий автомобильный трафик")
    utilities: bool = Field(..., description="Наличие всех коммуникаций")

class LocationRequest(BaseModel):
    latitude: float = Field(..., example=55.735)
    longitude: float = Field(..., example=37.73000)
    radius: float = Field(..., example=1.0, description="Радиус в километрах")