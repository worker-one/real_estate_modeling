import pandas as pd

# Input data as a list
data = [
    "Алкомаркеты", "Алкотека", "Краное и белое", "Бристоль", "Винлаб", "Норман", "Ароматный мир", "Мильстрим",
    "Аптеки", "Апрель", "Ригла", "36.6", "Горздрав", "Юнифарма", "Максавит", "Мелодия здоровья", 
    "Планета здоровья", "Нео-фарм", "Вита", 
    "Кофейни", "One and double", "Stars coffe", "cofix", "one price coffee", 
    "Пункты выдачи", "Яндекс", "Ozon", "Wildberries", "СДЭК", "Ситилинк пункт выдачи", 
    "Салоны связи", "Мегафон", "Билайн", "Теле2", "МТС", 
    "Супермаркеты", "Магнит у дома", "Магнит - косметик", "Пятерочка", "Дикси"
]

# Create an empty dataframe with columns 'Категория' and 'Сеть'
df = pd.DataFrame(columns=['Категория', 'Сеть'])

# Define categories
categories = ["Алкомаркеты", "Аптеки", "Кофейни", "Пункты выдачи", "Салоны связи", "Супермаркеты"]

# Initialize category to None
current_category = None

# Loop through the data and assign categories to corresponding networks
for item in data:
    if item in categories:
        current_category = item  # Update category
    else:
        df = df.append({'Категория': current_category, 'Сеть': item}, ignore_index=True)

# Display the dataframe
df.to_excel("output.xlsx", index=False)