import matplotlib.pyplot as plt
from pandas.io.json import json_normalize
from mpl_toolkits.basemap import Basemap
import json

"""
# endpoint

# Get list data from JSON file
d_json = request.get_json()

# Convert djson["accidents"] into a pd.DataFrame
df_joined = json_normalize(d_json, "accidents")

# Extract data for plotting
x = [row["INTPTLAT"] for row in df_joined]
y = [row["INTPTLON"] for row in df_joined]
acc_num = [row["accidents_num"] for row in df_joined]

# Make a map of the United States
plt.figure(figsize=(12, 6))
map_us = Basemap( 
    llcrnrlat=22, 
    llcrnrlon=-119, 
    urcrnrlat=49, 
    urcrnrlon=-64, 
    projection="lcc",
    lat_1=33,
    lat_2=45,
    lon_0=-95
)
map_us.drawmapboundary(fill_color="#A6CAE0", linewidth=0)
map_us.fillcontinents(color="grey", alpha=0.3)
map_us.drawcoastlines(linewidth=0.1, color="white")

# Plot extracted data to the map
plt.scatter(x, y, s=acc_num, alpha=0.5)

# Save image and send to requester
plt.savefig("map.png")


# JSON LOAD TEST
with open('test_data.json') as data:
    djson = json.load(data)
Received JSON data is structured like the following:
{ 
    ...
    "accidents" : 
    [
        {
            "NAME" : "Academy City", 
            "STUSAB" : "OH", 
            "accidents_num" : 34
        },
        {
            "NAME" : "Pasca Garden", 
            "STUSAB" : "NV", 
            "accidents_num" : 34
        }
    ]
    ...
}

# Check if attributes are correct
if djson.get("accidents", None) is None:
    # Fail
    print('return "Your data is either empty of invalid!", 400')
keys = ["NAME", "STUSAB", "accidents_num"]
dcounties = djson["accidents"] 
if not all(key in dcounties for key in keys) and not any(key not in keys for key in dcounties):
    # Fail
    print('return "Your data is invalid!", 400')
# Success

print(dcounties)



# Join to create djoined_list(NAME, STUSAB, accidents_num, INTPTLAT, INTPTLON)
# But in the form of a pandas dataframe
# df_joined = join_specific(dcounties, dcoor)

# Covert to JSON

"""