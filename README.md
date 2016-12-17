# Sidewalk Location Inference with OpenStreetMap and Strava Data

This project aims to explore how well we can predict sidewalk locations in urban areas only based on OpenStreetMap road data and Strava GPS traces. It's part of the https://opensidewalks.com/ effort. The sidewalks predicted can be served as guidelines for manully edited sidewalks.
The code here is just a proof-of-concept demo. There's lots of spaces for improvement in terms of efficiency and prediction quality.
![alt text](https://s30.postimg.org/gmim4iqs1/demo.png "sidewalk inference")

## Algorithm
To generate the sidewalks based on the map data, we want to know for each "way" segment, how far is the sidewalk from the centerline.  The assumptions made are
- Each OSM “way” has the same centerline-sidewalk distance throughout.
- Same centerline-sidewalk distance for both sides (symmetric).

To find the best such distance (let's call it d), we can do a MAP esimation to find the d for each "way" that maximizes the poteri pobability: 
```d_hat = argmax P(d|data) = argmax P(data|d) P(d) 	= argmax log(P(d)) + log(P(data|d))```
To estimate P(d) and P(data|d), We first assume d has a gaussian distribution, and given a d, the data points along the sidewalk is also normally distributed. That is, ```log(P(data|d)) = \sum log N(x_i, | d, sigma)```.
After an iteration of the algorithm, we will have the distribution of the d_hat over a collection of "ways". It's also possible to fine-tune the prior based on the resulting histogram and get better results (In the fashion of EM algorithm). Once we have the distance distribution, we can just do some vector math to calculate the sidewalk lines.

Other  details:
- Only GPS traces for running are considered for now since walking invoces too much noise and indoor trances to be useful.
- KD-tree is used to speed-up querying points near a "way". Only the top k points within a bounding box are considered for inference.

## Usage
##### strava_scraper.py
This script scrapes location points from Strava GPS traces, from an "activities" search results url specified in the script. A json file will be created containing all the points as a 2d arrary.
The current configuration scrapes all points in Seattle where the activitiy type is "Run". The url can be changed for different cities, etc. The actual CRS traces for the selected activities are fetched from an unofficial Strava API: http://raceshape.com/strava.export.php

##### generate_sidewalks.py
Usage: ```generate_sidewalks.py <osm_json_file>```
This script analyzes the input file (osm json format) and creates a similar osm json file containing all the predicted sidewalk segments, using the algorithm shown above. It also create visualizations to show how the datapoints are used in the prediction and how the predicted sidewalk distances from road centerlines are distribited. For now the parameters are hard-coded in the code.

## Log
- v1. Only based on road centerlines. (Done)
- v2. Gaussian MAP estimation based on strava data. (Done)
- TODO: Use better preprocessing before applying the alogrithm. e.g. Connecting the fragmented OSM "ways" together, and spltting by crossroad intersections.
- TODO: Take buidling contours into consideration.

## Useful Tools
- http://overpass-turbo.eu - Interactive query tool for Overpass API of OpenStreetMap data.
- http://geojson.io - Geojson visulization tool.
- http://tyrasd.github.io/osmtogeojson/ - Converting OSM json to geojson.
