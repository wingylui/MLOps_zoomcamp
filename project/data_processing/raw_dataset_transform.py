import pandas as pd
from prefect import flow, task

def cal_coastline(df, lat_col_name, lng_col_name):
    """
    calculate the distance between house and coast line
    df: the dataframe that need to calculate the distance between coastline and house
    lat_col_name, lng_col_name: the column name of Latitude and Longitude
    """
    
    import json
    from geopy.distance import distance

    # ---------------------------- arranage coordinate from geojson ----------------------------
    # import coastline geojson
    with open("../dataset/Coastline.geojson", "r") as f:
        json_file = json.load(f)

    json_file = json_file["features"][0]["geometry"]["coordinates"]

    coastline = [] # create an empty list for calculation
    # arrange the lat and long in the list and put it as a tuple in coastline list for calcualtion
    for coordinate in json_file:
        lat = coordinate[1]
        lng = coordinate[0]
        coastline.append(tuple([lat,lng])) 
    # ---------------------------- arranage coordinate from geojson ----------------------------

    # ---------------------------- coastal distance calculation ----------------------------
    coast_distance = [] # store the calculated coastal distance

    for index, row in df.iterrows():
        row_ls = [] # temp store for all the distance between coastal distance
        for coastline_coordinate in coastline:
            
            house_coordinate = tuple([row[lat_col_name],row[lng_col_name]])
            # calculate the distance from coast
            dum_dis = distance(coastline_coordinate, house_coordinate).m

            row_ls.append(dum_dis)
        # calculate the shortest distance between house and coastline and append into the coast distance
        coast_distance.append(min(row_ls))
    # ---------------------------- coastal distance calculation ----------------------------

    return coast_distance


def property_mapping(df, col_name):
    """
    mapping the property type with number rank based on the median price
    """
    property_type_map = {
        'house'                 : 1,
        'duplex-semi-detached'  : 2,
        'villa'                 : 3,
        'townhouse'             : 4,
        'terrace'               : 5,
        'apartment'             : 6,
        'flat'                  : 6,  # Same as apartment
        'unit'                  : 6,  # Same as apartment
        'acreage'               : 7,  # Based on land median
        'residential-other'     : 8
    }

    # Apply the mapping
    df[col_name] = df[col_name].map(property_type_map)

    return df

@flow(name = "raw_data_ingestion")
def ingest(path):
    """
    data ingestion and transformation
    """
    raw_dataset = pd.read_csv(path, chunksize=5000)
    # --------------------------- calculate / simple transformation ------------------------
    df = pd.DataFrame()
    for chunk_df in raw_dataset:

        chunk_df = property_mapping(chunk_df, "Property_Type")

        coast_distance = cal_coastline(chunk_df, "Latitude", "Longitude")
        chunk_df["Distance_to_Coast"] = coast_distance

        # convert to datetime type
        chunk_df["Date_Sold"] = pd.to_datetime(chunk_df["Date_Sold"], format="%d/%m/%Y")

        # append the complete dataframe
        df = pd.concat([df, chunk_df], axis = 0, ignore_index=True)
    # --------------------------- calculate / simple transformation ------------------------

    # --------------------------- merge school icsea data ---------------------------------- 
    icsea_df = pd.read_csv("../dataset/school_ICSEA.csv")
    icsea_df.head(2)

    second_icsea_df = icsea_df.loc[(icsea_df["Type"] == "S"), :]
    primary_icsea_df = icsea_df.loc[(icsea_df["Type"] == "P"), :]

    # merge secondary school ICSEA data included into this dataset
    full_df = pd.merge(df, second_icsea_df, how = "left", right_on = "School_Name", left_on = "Secondary_School_Name")
    full_df = full_df.rename(columns= {"ICSEA" : "Secondary_ICSEA"}).drop(columns = ["School_Name", "Type"])

    # merge primary school ICSEA data included into this dataset
    full_df = pd.merge(full_df, primary_icsea_df, how = "left", right_on = "School_Name", left_on = "Primary_School_Name") 
    full_df = full_df.rename(columns= {"ICSEA" : "Primary_ICSEA"}).drop(columns = ["School_Name", "Type"])
    # --------------------------- merge school icsea data ---------------------------------- 

    full_df.to_csv("../dataset/output/completed_dataset.csv", index = False)



if __name__ == "__main__":
    ingest("../dataset/perth_property_data.csv")
