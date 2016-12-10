import numpy as np
import matplotlib.pyplot as plt
import urllib2
import xmltodict
import re
import time
import json
from bs4 import BeautifulSoup

def get_all_aids():
    # Search result page. Change the parameters to specify different cities, etc.
    # Note that activity_type=Run
    url = "https://www.strava.com/activities/search?" + \
        "activity_type=Run&city=Seattle&country=United+States&distance_end=200" + \
        "&distance_start=0&elev_gain_end=15000&elev_gain_start=0&keywords=" + \
        "&lat_lng=47.6062095%2C-122.3320708&location=Seattle&state=Washington" + \
        "&time_end=10.0&time_start=0.0&type=&utf8=%E2%9C%93"
    aids = []
    for page in range(1, 5):
        html = ""
        data = urllib2.urlopen(url + "&page=" + str(page))
        for line in data:
            html += line
        # print html
        parsed_html = BeautifulSoup(html, "html.parser")
        links = parsed_html.body.findAll('a', attrs={'href': lambda L: L and re.match(r"^/activities/\d+$", L)})
        for link in links:
            aids += [ link["href"].split("/")[2] ]
    return aids

def scraper_api_url(aid):
    scraper_api = "http://raceshape.com/strava.export.php?ride="
    return scraper_api + aid + "&type=CRS"

def read_crs_as_dict(aid):
    res = ""
    data = urllib2.urlopen(scraper_api_url(aid))
    for line in data:
        # Filter out error messages that might be present even if the data is valid.
        if re.match(r"^\s*<.*$", line): 
            res += line
    # print res
    return xmltodict.parse(res)

def get_points_from_crs(crs):
    points = []
    for track_point in crs["TrainingCenterDatabase"]["Courses"]["Course"]["Track"]["Trackpoint"]:
        lat = float(track_point["Position"]["LatitudeDegrees"])
        lng = float(track_point["Position"]["LongitudeDegrees"])
        points += [(lat, lng)]
    return points

if __name__ == "__main__":
    aids = get_all_aids()
    all_points = []
    for aid in aids:
        print aid
        try:
            crs = read_crs_as_dict(aid)
        except:
            print "failure"
            continue

        points = get_points_from_crs(crs)
        print str(len(points)) + " points added"
        all_points += points

        lats = [point[0] for point in points]
        lngs = [point[1] for point in points]
        plt.scatter(lats, lngs)

    pretty_json =  json.dumps(all_points, indent=2, separators=(',', ': '))
    output_file = open('all_points.json', 'w')
    output_file.write(pretty_json)

    plt.show()
