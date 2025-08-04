import requests

house = {
    "Property_Type"             : "house", 
    "Bedrooms"                  : 5, 
    "Bathrooms"                 : 3, 
    "Parking_Spaces"            : 3, 
    "Land_Size"                 : 1532, 
    "Primary_School_Distance"   : 418, 
    "Secondary_School_Distance" : 418, 
    "Distance_to_CBD"           : 9983, 
    "Distance_to_Coast"         : 1539.28, 
    "Secondary_ICSEA"           : 1067, 
    "Primary_ICSEA"             : 1043, 
    "Year_Sold"                 : 2016, 
    "Month_Sold"                : 6
}


url = "http://localhost:9696/predict"
response = requests.post(url, json=house)
print(response.json())