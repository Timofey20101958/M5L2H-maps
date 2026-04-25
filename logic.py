import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities


    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities):
    # Создаём проекцию
        ax = plt.axes(projection=ccrs.PlateCarree())

        # Заливка океанов единым цветом (например, светло‑синий)
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue', zorder=0)

        # Получаем данные о границах стран
        countries = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_0_countries',
            scale='50m'
        )

        # Добавляем страны на карту с индивидуальной заливкой
        self._add_colored_countries(ax, countries)

        # Границы государств (тонкая чёрная линия поверх заливки)
        ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=0.3, zorder=2)

        # Сетка параллелей и меридианов
        ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--', zorder=3)

        # Отмечаем города
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates

                # Точка на карте
                plt.plot([lng], [lat],
                        color='red', linewidth=2, marker='o', markersize=6,
                        transform=ccrs.Geodetic(), zorder=4)

                # Подпись города рядом с точкой
                plt.text(lng + 0.5, lat + 0.5, city,
                        horizontalalignment='left',
                        verticalalignment='bottom',
                        transform=ccrs.Geodetic(),
                        fontsize=9, color='darkblue',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                        zorder=5)

        # Сохраняем изображение
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()

        def _add_colored_countries(self, ax, countries):
            """Добавляет страны на карту с разными цветами заливки."""
            # Список цветов для стран (можно расширить)
            colors = [
                'lightgreen', 'wheat', 'lightyellow', 'peachpuff',
                'mistyrose', 'honeydew', 'lavender', 'aliceblue'
            ]

            patches = []
            color_list = []

            # Перебираем все страны в данных
            for country in countries.geometries():
                # Преобразуем геометрию в полигон matplotlib
                if country.geom_type == 'Polygon':
                    coords = np.array(country.exterior.coords)
                    polygon = Polygon(coords, closed=True)
                    patches.append(polygon)
                    # Выбираем цвет циклически из списка
                    color_list.append(np.random.choice(colors))
                elif country.geom_type == 'MultiPolygon':
                    for subpolygon in country.geoms:
                        coords = np.array(subpolygon.exterior.coords)
                        polygon = Polygon(coords, closed=True)
                        patches.append(polygon)
                        color_list.append(np.random.choice(colors))

            # Создаём коллекцию полигонов с цветами
            p = PatchCollection(patches, facecolor=color_list, edgecolor='none', zorder=1)
            ax.add_collection(p)
            
        
    def draw_distance(self, city1, city2):
        pass


if __name__=="__main__":
    
    m = DB_Map(DATABASE)
    m.create_user_table()
