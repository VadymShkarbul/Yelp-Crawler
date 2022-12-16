import json
import os
import re
import time

# import httpx as httpx
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.yelp.com/"
SEARCH_PATH = "/v3/businesses/search"
BUSINESS_PATH = "/v3/businesses/"

HEADERS = {
    "Authorization": f"Bearer {os.getenv('API_KEY')}"
}


def get_businesses(category, location):
    businesses_data = []

    for offset in range(0, 1000, 50):
        params = {
            'location': location.replace(' ', '+'),
            'categories': category.replace(' ', '+'),
            'limit': 50,
            'offset': offset
        }

        response = requests.get(
            urljoin(BASE_URL, SEARCH_PATH),
            headers=HEADERS,
            params=params
        )

        if response.status_code == 200:
            businesses_data += response.json()['businesses']
        elif response.status_code == 400:
            print('400 Bad Request')
            break

    businesses = dict(
        businesses=list()
    )

    for business in businesses_data:
        businesses["businesses"].append({
            "Business name": business["name"],
            "Business rating": business["rating"],
            "Number of reviews": business["review_count"],
            "Business yelp url": business["url"].split("?adjust")[0],
            "Business website": "",
            "First five reviews": []
        })

    return businesses
    # with open("result.json", "w") as result_file:
    #     json.dump(businesses, result_file, indent=2)


def get_web_address(url: str) -> str:
    """
    Yelp API search endpoints return a lot of useful information,
    but the business website can only be accessed from the detail view
    endpoint. I do it with the help of this function.
    """
    # resp = await session.get(
    #
    # )

    try:
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")

        href = soup.find("a", {"class": "css-1um3nx", "target": "_blank"}).get("href")
        href = unquote(href)
        href = re.search("url=(.*)&cachebuster=", href)

        return href.group(1)
    except AttributeError:
        return "No web address"


#
#
def get_reviewers_info(url: str) -> list:
    """
    According to the terms of the task, need to extract 5 reviews,
    with the help of the Yelp API, only three are possible:
    https://docs.developer.yelp.com/reference/v3_business_reviews
    So I used the BeautifulSoup here
    """
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    all_items = soup.find_all(
        "div",
        {"class": "review__09f24__oHr9V border-color--default__09f24__NPAKY"}
    )[:5]

    reviews = []

    for item in all_items:

        try:
            name = item.find("a", {"class": "css-1m051bw"}).text
        except AttributeError:
            name = "No name"

        try:
            reviewer_location = item.find("span", {"class": "css-qgunke"}).text
        except AttributeError:
            reviewer_location = "No location"

        try:
            review_date = item.find("span", {"class": "css-chan6m"}).text
        except AttributeError:
            review_date = "No date"

        reviews.append({
            "Reviewer name": name,
            "Reviewer location": reviewer_location,
            "Review date": review_date
        })

    return reviews


if __name__ == '__main__':
    business_category = input("Please enter business category: ") or "contractors"
    business_location = input("Please enter business location: ") or "San Francisco, CA"
    # sample_limit = input("Please enter sample limit: ")
    start = time.perf_counter()
    businesses_dict = get_businesses(business_category, business_location)
    for business in businesses_dict["businesses"]:
        business["Business website"] = get_web_address(business["Business yelp url"])
        business["First five reviews"] = get_reviewers_info(business["Business yelp url"])
    with open("result.json", "w") as result_file:
        json.dump(businesses_dict, result_file, indent=2)
    end = time.perf_counter()
    print("Elapsed:", end - start)
