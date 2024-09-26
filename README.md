# Geocoding and Environmental Proximity Analysis

## Overview

This project is a Flask web application designed to take user-uploaded CSV files containing addresses and provide enhanced geocoded and environmental proximity data. Using various APIs, including Google Maps and custom geographical analysis scripts, the application delivers insights such as proximity to forests, water bodies, wildfire incidents, and flood risks.

The resulting enriched data is available for download as a CSV file.

## Features

- **Address Geocoding**: Converts addresses into latitude, longitude, and detailed address components (e.g., city, state, postal code).
- **Elevation Data**: Fetches elevation information for each geocoded point.
- **Coniferous Forest Proximity**: Determines the distance to the nearest coniferous forest and identifies forest types and ecoregions.
- **Water Body Proximity**: Finds the closest significant water body for locations in the USA and Canada.
- **Flood Risk Analysis**: Provides flood risk information for Canadian locations.
- **Wildfire Data (USA)**: Identifies nearby fire incidents, calculates wildfire risk, and checks historical fire data.
- **Earthquake Alerts (Worldwide)**: Provides recent earthquake alerts and proximity to major historical earthquakes.
- **Landslide Susceptibility (USA)**: Evaluates the risk of landslides for USA locations.
- **Drought Condition (USA)**: Updates drought condition information based on environmental data.
- **Hail Storm Reports (USA)**: Provides live hail storm data near the location.

## Setup and Installation

### Prerequisites

- Python 3.8+
- A Google Cloud API key with access to the Geocoding and Elevation APIs
- Flask
- Pandas
- GeoPandas
- Pyogrio

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/geocoding-environment-analysis.git
   cd geocoding-environment-analysis

2. **Create a Virtual Environment**:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: `env\Scripts\activate`

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Set Up Google Cloud API Key: You will need a Google Cloud API key for the Geocoding and Elevation services. Set the key as an environment variable**:
   ```bash
   export GOOGLE_API_KEY='your-google-api-key'

Alternatively, you can directly edit the API key in app.py by replacing the value of API_KEY.

5. **Run the Flask Application**:
   ```bash
   python app.py

Access the Application: Open your browser and go to http://127.0.0.1:5000/.

## Usage
On the homepage, upload a CSV file with an address column containing the addresses you want to analyze.
Optionally, provide a custom output file name.
The system will geocode the addresses and retrieve environmental proximity data.
After processing, a CSV file with the geocoded and enriched data will be available for download.
