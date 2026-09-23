import os
import pandas as pd
from pymongo import MongoClient

# Подключение к локальной СУБД
client = MongoClient("mongodb://localhost:27017/")
db = client["EdTechDB"]

# Путь к папке с CSV относительно корня
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
files = ["lessons.csv", "attendances.csv", "groups.csv"]

for file in files:
    col_name = file.split(".")[0]
    file_path = os.path.join(data_dir, file)
    
    if os.path.exists(file_path):
        # Дропаем старую коллекцию и заливаем новую
        db[col_name].drop()
        df = pd.read_csv(file_path)
        db[col_name].insert_many(df.to_dict(orient="records"))
        print(f"Коллекция '{col_name}' успешно импортирована!")
