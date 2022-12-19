import json
import os
import re
import time

import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, quote
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.yelp.com/"
SEARCH_PATH = "/v3/businesses/search"
BUSINESS_PATH = "/v3/businesses/"

HEADERS = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}

BUSINESSES_COUNT = 100
"""
Will get BUSINESSES_COUNT results maximum 1000, Should be a multiple of 50
Check API documentation for more information:
https://docs.developer.yelp.com/reference/v3_business_search
"""
# TODO: Add the ability for the user to change the number of results

# CSS selectors used for parsing the required information
WEB_ADDRESS_LINK_CSS_CLASS = "css-1um3nx"

REVIEW_CSS_CLASS = "review__09f24__oHr9V border-color--default__09f24__NPAKY"
REVIEWER_NAME_CSS_CLASS = "css-1m051bw"
REVIEWER_LOCATION_CSS_CLASS = "css-qgunke"
REVIEW_DATE_CSS_CLASS = "css-chan6m"

CLASSES_MAP = {
    REVIEWER_NAME_CSS_CLASS: 'name',
    REVIEWER_LOCATION_CSS_CLASS: 'location',
    REVIEW_DATE_CSS_CLASS: 'date',
}


def get_businesses(category, location):
    businesses_data = []

    for offset in range(0, BUSINESSES_COUNT, 50):  # Will get BUSINESSES_COUNT results
        params = {
            "location": location.replace(" ", "+"),
            "categories": category.replace(" ", "+"),
            "limit": 50,
            "offset": offset,
        }

        response = requests.get(
            urljoin(BASE_URL, SEARCH_PATH), headers=HEADERS, params=params
        )

        if response.status_code == 200:
            businesses_data += response.json()["businesses"]
        elif response.status_code == 400:
            print("400 Bad Request")
            break

    businesses = dict(businesses=list())

    for business in businesses_data:
        businesses["businesses"].append(
            {
                "Business name": business["name"],
                "Business rating": business["rating"],
                "Number of reviews": business["review_count"],
                "Business yelp url": business["url"].split("?adjust")[0],
                "Business website": "",
                "First five reviews": [],
            }
        )

    return businesses


def get_additional_info(url: str) -> list:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    try:
        href = soup.find("a", {
            "class": WEB_ADDRESS_LINK_CSS_CLASS,
            "target": "_blank"
        }).get(
            "href"
        )
        href = unquote(href)
        href = re.search("url=(.*)&cachebuster=", href).group(1)
    except AttributeError:
        href = "No web address"

    all_items = soup.find_all(
        "div", {"class": REVIEW_CSS_CLASS}
    )[:5]

    reviews = []

    for item in all_items:
        fields_to_check = [
            REVIEWER_NAME_CSS_CLASS,
            REVIEWER_LOCATION_CSS_CLASS,
            REVIEW_DATE_CSS_CLASS
        ]

        final_obj = {}

        for field in fields_to_check:

            obj = item.find(["a", "span"], {"class": field})
            if obj is not None:
                value = obj.text
            else:
                value = f'No {CLASSES_MAP[field]}'

            final_obj[f"Reviewer {CLASSES_MAP[field]}"] = value

        reviews.append(final_obj)

    return [href, reviews]


def main():
    business_category = input("Please enter business category: ") or "contractors"
    business_location = input("Please enter business location: ") or "San Francisco, CA"
    print("Please, wait...")

    businesses_dict = get_businesses(business_category, business_location)

    for business in businesses_dict["businesses"]:
        parse = get_additional_info(business["Business yelp url"])

        business["Business website"] = parse[0]
        business["First five reviews"] = parse[1]

    with open("result.json", "w") as result_file:
        json.dump(businesses_dict, result_file, indent=2)

    print("Done! Check results:")
    print(
        f"file://{quote(os.path.dirname(os.path.abspath('result.json')))}/result.json"
    )


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    end = time.perf_counter()

    print("Elapsed:", end - start)
