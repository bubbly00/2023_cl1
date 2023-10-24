# Interacting with Web APIs
# Problem Statement: Analyzing Weather Data from OpenWeatherMap API

import requests
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import folium

# Register and Obtain API Key from OpenWeatherMap
api_key = 'fb365aa6104829b44455572365ff3b4e'  # Replace with your API key

# Interact with the OpenWeatherMap API
lat = 18.184135
lon = 74.610764
api_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
response = requests.get(api_url)
weather_data = response.json()

# Extract Relevant Weather Attributes
temperatures = [item['main']['temp'] for item in weather_data['list']]
timestamps = [pd.to_datetime(item['dt'], unit='s') for item in weather_data['list']]
humidity = [item['main']['humidity'] for item in weather_data['list']]
wind_speed = [item['wind']['speed'] for item in weather_data['list']]
weather_description = [item['weather'][0]['description'] for item in weather_data['list']]

# Creating a pandas DataFrame with the extracted weather data
weather_df = pd.DataFrame({
    'Timestamp': timestamps,
    'Temperature': temperatures,
    'Humidity': humidity,
    'Wind Speed': wind_speed,
    'Weather Description': weather_description,
})

# Setting the Timestamp column as the DataFrame's index
weather_df.set_index('Timestamp', inplace=True)

# Data Aggregation for summary statistics
daily_mean_temp = weather_df['Temperature'].resample('D').mean()
daily_mean_humidity = weather_df['Humidity'].resample('D').mean()
daily_mean_wind_speed = weather_df['Wind Speed'].resample('D').mean()

# Data Visualization
# Plotting the mean daily temperature over time (Line plot)
plt.figure(figsize=(10, 6))
daily_mean_temp.plot(color='red', linestyle='-', marker='o')
plt.title('Mean Daily Temperature')
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.grid(True)
plt.show()

# Creating a heatmap to visualize the relationship between temperature and humidity
heatmap_data = weather_df[['Temperature', 'Humidity']]
sns.heatmap(heatmap_data, annot=True, cmap='coolwarm')
plt.title('Temperature vs Humidity Heatmap')
plt.show()

# Geo-spatial Visualization
locations = ['London', 'Paris', 'New York']
weather_df = pd.DataFrame()

for location in locations:
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}'
    response = requests.get(api_url)
    weather_data = response.json()

    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    latitude = weather_data['coord']['lat']
    longitude = weather_data['coord']['lon']

    location_df = pd.DataFrame({
        'Location': [location],
        'Temperature': [temperature],
        'Humidity': [humidity],
        'Wind Speed': [wind_speed],
        'Latitude': [latitude],
        'Longitude': [longitude]
    })

    weather_df = pd.concat([weather_df, location_df], ignore_index=True)

world_map = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))
world_map.rename(columns={'name': 'Location'}, inplace=True)
weather_map = world_map.merge(weather_df, on='Location')

map_center = [weather_df['Latitude'].mean(), weather_df['Longitude'].mean()]
weather_map_folium = folium.Map(location=map_center, zoom_start=2)

for index, row in weather_map.iterrows():
    location = [row['Latitude'], row['Longitude']]
    temperature = row['Temperature']
    marker_text = f'Temperature: {temperature} K'
    folium.Marker(location, popup=marker_text, icon=folium.Icon(icon='cloud', color='red')).add_to(weather_map_folium)

weather_map_folium