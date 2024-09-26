from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
import os
import requests
from conif_forest_dist import get_coniferous_forest_proximity  # Import the proximity script
from waterway_can import get_nearest_water_body  # Import the waterway analysis for Canada
from waterway_usa import get_nearest_water_body_usa  # Import the waterway analysis for USA
from nri_index import get_NRI_Index  # Import the NRI Index script
from flood_risk_areas_can import flood_risk_areas_can  # Import the flood risk analysis for Canada
from current_wildfires_usa import get_nearest_fire_incident  # Import the wildfire analysis for USA
from recent_earthquakes_world import get_world_recent_earthquakes  # Import the earthquake analysis for worldwide
from drought_intensity_usa import update_drought_condition  # Import the drought intensity analysis for USA
from active_floods_can import is_point_within_flood  # Import the active flood analysis for Canada
from current_wildfire_perimeters_bc_can import is_point_within_wildfire_perimeter  # Import the wildfire perimeters for BC, Canada
from landslide_susceptibility_usa import landslide_susceptibility_analysis  # Import landslide susceptibility analysis for USA
from world_major_earthquakes import check_near_historical_earthquake  # Import the historical earthquake analysis script
from live_hail_report_usa import get_closest_hail_storm  # Import the live hail storm report analysis script
from wildfire_risk_usa import check_USA_Wildfire_Risk  # Import the USA wildfire risk analysis script
from historical_fire_burned_areas_usa import get_historical_fire_info  # Import the historical fire burned areas analysis script

app = Flask(__name__)
app.secret_key = '4350'  # Secret key for session management

# Google API keys
API_KEY = 'AIzaSyAgCWM5ofwRusyoQYH8_npyg9xNRXeqLUk'

# Function to interact with Google Geocoding API and get latitude, longitude, and address components
def geocode_address(address, api_key):
    print(f"Geocoding address: {address}", flush=True)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        # Extract latitude and longitude
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']

        # Extract address components
        components = {comp['types'][0]: comp['long_name'] for comp in data['results'][0]['address_components']}
        street_address = components.get('street_number', '') + ' ' + components.get('route', '')
        city = components.get('locality', '')
        state = components.get('administrative_area_level_1', '')
        postal_code = components.get('postal_code', '')
        country = components.get('country', '')

        return lat, lng, street_address, city, state, postal_code, country
    else:
        print(f"Failed to geocode address: {address}, Status: {data['status']}", flush=True)
        return None, None, '', '', '', '', ''  # Return empty values if geocoding fails

# Function to get elevation from the Google Elevation API
def get_elevation(lat, lng, api_key):
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lng}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        elevation = data['results'][0]['elevation']
        return elevation
    else:
        print(f"Failed to get elevation for {lat}, {lng}. Status: {data['status']}", flush=True)
        return None

# Route to handle file upload, geocoding, and adding proximity data
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        try:
            print("Form submitted", flush=True)
            file = request.files.get("file")
            output_filename = request.form.get("output_filename", "geocoded_output") + '.csv'  # Append .csv extension

            if file and output_filename:
                # Read the uploaded CSV file
                print("Reading uploaded CSV", flush=True)
                df = pd.read_csv(file)

                # Normalize column names to lowercase to handle case-insensitivity
                df.columns = df.columns.str.lower()

                # Check if the "address" column exists, regardless of case
                if 'address' not in df.columns:
                    flash("The CSV file must contain an 'address' column.", "error")
                    print("Missing 'address' column in CSV", flush=True)
                    return redirect(url_for('upload_file'))

                # Check if "latitude", "longitude", "country", and "elevation" columns exist (case-insensitive)
                lat_column = [col for col in df.columns if col.lower() == 'latitude']
                lon_column = [col for col in df.columns if col.lower() == 'longitude']
                elevation_column = [col for col in df.columns if 'elevation' in col.lower()]
                country_column = [col for col in df.columns if col.lower() == 'country']
                forest_proximity_column = [col for col in df.columns if col.lower() == 'coniferous forest proximity']
                forest_type_column = [col for col in df.columns if col.lower() == 'coniferous forest type']
                ecoregion_column = [col for col in df.columns if col.lower() == 'ecoregion name']
                water_proximity_column = [col for col in df.columns if col.lower() == 'body of water proximity']
                nri_rating_column = [col for col in df.columns if col.lower() == 'fema risk rating (usa only)']
                flood_risk_column = [col for col in df.columns if col.lower() == 'flood risk level (can only)']
                fire_incident_column = [col for col in df.columns if col.lower() == 'fire incident nearby (usa only)']
                earthquake_alert_column = [col for col in df.columns if col.lower() == 'earthquake alert (worldwide)']
                drought_condition_column = [col for col in df.columns if col.lower() == 'drought condition (usa only)']
                flood_status_column = [col for col in df.columns if col.lower() == 'flood status (canada only)']
                wildfire_status_column = [col for col in df.columns if col.lower() == 'wildfire status (bc canada)']
                landslide_susceptibility_column = [col for col in df.columns if col.lower() == 'landslide susceptibility (usa only)']
                historical_earthquake_column = [col for col in df.columns if col.lower() == 'near historical major earthquake']
                hail_storm_column = [col for col in df.columns if col.lower() == 'recent hail storm']
                hail_storm_datetime_column = [col for col in df.columns if col.lower() == 'hail storm date/time']
                hail_report_column = [col for col in df.columns if col.lower() == 'hail report']
                wildfire_risk_column = [col for col in df.columns if col.lower() == 'wildfire risk']
                wildfire_risk_value_column = [col for col in df.columns if col.lower() == 'wildfire risk value']
                historical_fire_column = [col for col in df.columns if col.lower() == 'historical fire']
                historical_fire_type_column = [col for col in df.columns if col.lower() == 'historical fire type']
                historical_fire_date_column = [col for col in df.columns if col.lower() == 'historical fire date']
                

                # If columns exist, use them; otherwise, create new ones
                lat_column = lat_column[0] if lat_column else "latitude"
                lon_column = lon_column[0] if lon_column else "longitude"
                elevation_column = elevation_column[0] if elevation_column else "Elevation"
                country_column = country_column[0] if country_column else "country"  # Create country column if not present
                forest_proximity_column = forest_proximity_column[0] if forest_proximity_column else "Coniferous Forest Proximity"
                forest_type_column = forest_type_column[0] if forest_type_column else "Coniferous Forest Type"
                ecoregion_column = ecoregion_column[0] if ecoregion_column else "Ecoregion Name"
                water_proximity_column = water_proximity_column[0] if water_proximity_column else "Body of Water Proximity"
                nri_rating_column = nri_rating_column[0] if nri_rating_column else "FEMA Risk Rating (USA Only)"
                flood_risk_column = flood_risk_column[0] if flood_risk_column else "Flood Risk Level (CAN Only)"
                fire_incident_column = fire_incident_column[0] if fire_incident_column else "Fire Incident Nearby (USA Only)"
                earthquake_alert_column = earthquake_alert_column[0] if earthquake_alert_column else "Earthquake Alert (Worldwide)"
                drought_condition_column = drought_condition_column[0] if drought_condition_column else "Drought Condition (USA Only)"
                flood_status_column = flood_status_column[0] if flood_status_column else "Flood Status (Canada Only)"
                wildfire_status_column = wildfire_status_column[0] if wildfire_status_column else "Wildfire Status (BC Canada)"
                landslide_susceptibility_column = landslide_susceptibility_column[0] if landslide_susceptibility_column else "Landslide Susceptibility (USA Only)"
                historical_earthquake_column = historical_earthquake_column[0] if historical_earthquake_column else "Near Historical Major Earthquake"
                hail_storm_column = hail_storm_column[0] if hail_storm_column else "Recent Hail Storm"
                hail_storm_datetime_column = hail_storm_datetime_column[0] if hail_storm_datetime_column else "Hail Storm Date/Time"
                hail_report_column = hail_report_column[0] if hail_report_column else "Hail Report"
                wildfire_risk_column = wildfire_risk_column[0] if wildfire_risk_column else "Wildfire Risk"
                wildfire_risk_value_column = wildfire_risk_value_column[0] if wildfire_risk_value_column else "Wildfire Risk Value"
                historical_fire_column = historical_fire_column[0] if historical_fire_column else "Historical Fire"
                historical_fire_type_column = historical_fire_type_column[0] if historical_fire_type_column else "Historical Fire Type"
                historical_fire_date_column = historical_fire_date_column[0] if historical_fire_date_column else "Historical Fire Date"

                # Geocode each address and extract address components
                for i, row in df.iterrows():
                    print(f"Processing row {i + 1}", flush=True)
                    lat, lng, street_address, city, state, postal_code, country = geocode_address(row['address'], API_KEY)
                    if lat is not None and lng is not None:
                        df.at[i, lat_column] = lat
                        df.at[i, lon_column] = lng
                        df.at[i, 'street_address'] = street_address
                        df.at[i, 'city'] = city
                        df.at[i, 'state'] = state
                        df.at[i, 'postal_code'] = postal_code
                        df.at[i, country_column] = country  # Add the country to the dataframe

                        # Get the elevation and add it to the existing Elevation column
                        elevation = get_elevation(lat, lng, API_KEY)
                        if elevation is not None:
                            df.at[i, elevation_column] = elevation

                        # Call the coniferous forest proximity script
                        point = {"x": lng, "y": lat}
                        forest_distance, forest_type, ecoregion_name = get_coniferous_forest_proximity(point)
                        df.at[i, forest_proximity_column] = forest_distance
                        df.at[i, forest_type_column] = forest_type
                        df.at[i, ecoregion_column] = ecoregion_name

                        # Call the Canada only scripts
                        if country == "Canada":
                            print(f"Calculating nearest water body for Canada (Province: {state})")
                            water_proximity = get_nearest_water_body(point, state)
                            df.at[i, water_proximity_column] = water_proximity

                            # Call the flood risk analysis script for Canada
                            flood_risk = flood_risk_areas_can(point["x"], point["y"])
                            df.at[i, flood_risk_column] = flood_risk

                            # Call the active floods analysis script for Canada
                            flood_status = is_point_within_flood(point["x"], point["y"])
                            if flood_status:
                                df.at[i, flood_status_column] = flood_status.get("Flood Status", "Not within an active flood area.")

                            # Call the wildfire perimeter analysis for BC, Canada if state is British Columbia
                            if state == "British Columbia":
                                print(f"Checking wildfire perimeter for BC, Canada")
                                wildfire_status = is_point_within_wildfire_perimeter(point["x"], point["y"])
                                if wildfire_status:
                                    df.at[i, wildfire_status_column] = wildfire_status.get("Wildfire Status", "Not within a wildfire perimeter.")

                        # Call the USA only scripts
                        if country == "United States":
                            print(f"Calculating nearest water body for USA (State: {state})")
                            water_proximity = get_nearest_water_body_usa(point, state.lower())  # Use lowercase for the state
                            df.at[i, water_proximity_column] = water_proximity

                            # Call the NRI Index script for points in the U.S.
                            print(f"Calculating NRI Risk Rating for USA (State: {state})")
                            nri_rating = get_NRI_Index(point)
                            df.at[i, nri_rating_column] = nri_rating

                            # Reset wildfire, drought, and landslide information for each row before checking
                            df.at[i, fire_incident_column] = "No"
                            df.at[i, drought_condition_column] = "Not currently affected by drought."
                            df.at[i, landslide_susceptibility_column] = "Not within a landslide feature."
                            df.at[i, 'Fire Incident Name'] = ''
                            df.at[i, 'Fire Incident Type'] = ''
                            df.at[i, 'Fire Discovery Date Time'] = ''
                            df.at[i, 'Fire Percent Contained'] = ''
                            df.at[i, 'Fire Incident Cause'] = ''
                            df.at[i, 'Fire Primary Fuel'] = ''
                            df.at[i, 'Residences Destroyed'] = ''
                            df.at[i, 'Other Structures Destroyed'] = ''
                            df.at[i, 'Fire Incident Injuries'] = ''
                            df.at[i, 'Fire Incident Fatalities'] = ''

                            # Call the wildfire proximity analysis for the U.S.
                            print(f"Checking wildfire proximity for USA (State: {state})")
                            fire_incident_info = get_nearest_fire_incident(point["x"], point["y"])
                            if fire_incident_info and fire_incident_info["Current Wildfire Nearby"] == "Yes":
                                df.at[i, fire_incident_column] = fire_incident_info["Current Wildfire Nearby"]
                                df.at[i, 'Fire Incident Name'] = fire_incident_info.get("Fire Incident Name", '')
                                df.at[i, 'Fire Incident Type'] = fire_incident_info.get("Fire Incident Type", '')
                                df.at[i, 'Fire Discovery Date Time'] = fire_incident_info.get("Fire Discovery Date Time", '')
                                df.at[i, 'Fire Percent Contained'] = fire_incident_info.get("Fire Percent Contained", '')
                                df.at[i, 'Fire Incident Cause'] = fire_incident_info.get("Fire Incident Cause", '')
                                df.at[i, 'Fire Primary Fuel'] = fire_incident_info.get("Fire Primary Fuel", '')
                                df.at[i, 'Residences Destroyed'] = fire_incident_info.get("ResidencesDestroyed", '')
                                df.at[i, 'Other Structures Destroyed'] = fire_incident_info.get("OtherStructuresDestroyed", '')
                                df.at[i, 'Fire Incident Injuries'] = fire_incident_info.get("Injuries", '')
                                df.at[i, 'Fire Incident Fatalities'] = fire_incident_info.get("Fatalities", '')

                            # Call the drought condition analysis for the U.S.
                            print(f"Checking drought condition for USA (State: {state})")
                            drought_condition_info = update_drought_condition(point["x"], point["y"])
                            if drought_condition_info:
                                df.at[i, drought_condition_column] = drought_condition_info.get("Drought Condition", "Not currently affected by drought.")

                            # Call the landslide susceptibility analysis for USA
                            print(f"Checking landslide susceptibility for USA")
                            landslide_status = landslide_susceptibility_analysis(point["x"], point["y"])
                            if landslide_status:
                                df.at[i, landslide_susceptibility_column] = landslide_status

                            # Call the live hail storm report analysis script for USA
                                print(f"Checking for recent hail storms near the location (State: {state})")
                                hail_storm_info = get_closest_hail_storm(point["x"], point["y"])
                                if hail_storm_info:
                                    df.at[i, 'Recent Hail Storm'] = hail_storm_info.get("Recent Hail Storm", "No")
                                    df.at[i, 'Hail Storm Date/Time'] = hail_storm_info.get("Date/Time", "N/A")
                                    df.at[i, 'Hail Report'] = hail_storm_info.get("Hail Report", "N/A")

                            # Call the wildfire risk analysis for USA
                                    print(f"Checking wildfire risk for USA (State: {state})")
                                    wildfire_risk_info = check_USA_Wildfire_Risk(point["x"], point["y"])
                                    if wildfire_risk_info:
                                        df.at[i, wildfire_risk_column] = wildfire_risk_info.get("Wildfire Risk", "No")
                                        df.at[i, wildfire_risk_value_column] = wildfire_risk_info.get("Wildfire Risk Value", "N/A")

                            # Call the historical fire burned areas analysis for USA
                                    print(f"Checking historical fire burned areas for USA (State: {state})")
                                    historical_fire_info = get_historical_fire_info(point["x"], point["y"])
                                    if historical_fire_info:
                                        df.at[i, historical_fire_column] = historical_fire_info.get("Historical Fire", "No")
                                        df.at[i, historical_fire_type_column] = historical_fire_info.get("Historical Fire Type", "N/A")
                                        df.at[i, historical_fire_date_column] = historical_fire_info.get("Historical Fire Date", "N/A")

                        # Call the recent earthquake analysis script
                        print(f"Checking recent earthquake proximity worldwide")
                        earthquake_info = get_world_recent_earthquakes(point["x"], point["y"])
                        if earthquake_info:
                            df.at[i, earthquake_alert_column] = earthquake_info.get("Earthquake Alert", "No")
                            df.at[i, 'Earthquake Magnitude'] = earthquake_info.get("Magnitude", "N/A")

                        # Call the historical earthquake proximity analysis script
                        print(f"Checking historical earthquake proximity worldwide")
                        historical_earthquake_info = check_near_historical_earthquake(point["x"], point["y"])
                        if historical_earthquake_info:
                            df.at[i, 'Near Historical Major Earthquake'] = historical_earthquake_info.get("Near Historical Major Earthquake", "No")
                            df.at[i, 'HE Magnitude'] = historical_earthquake_info.get("HE Magnitude", "N/A")
                            df.at[i, 'HE Intensity'] = historical_earthquake_info.get("HE Intensity", "N/A")
                            df.at[i, 'HE Deaths'] = historical_earthquake_info.get("HE Deaths", "N/A")
                            df.at[i, 'HE Damage'] = historical_earthquake_info.get("HE Damage", "N/A")
                            df.at[i, 'HE Date'] = historical_earthquake_info.get("HE_Date", "N/A")

                # Save the processed file with the custom name
                output_file = os.path.join(os.getcwd(), output_filename)
                print(f"Saving output to {output_file}", flush=True)
                df.to_csv(output_file, index=False)

                # Return the file as an attachment for download
                return send_file(output_file, as_attachment=True)

        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            print(f"An error occurred: {e}", flush=True)
            return redirect(url_for('upload_file'))

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(threaded=True)  # Enable threaded execution for concurrent requests
