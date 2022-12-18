import asyncio
import json
import os
import re

import aiohttp
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, quote
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.yelp.com/"
SEARCH_PATH = "/v3/businesses/search"
BUSINESS_PATH = "/v3/businesses/"

HEADERS = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}


def get_businesses(category, location):
    businesses_data = []

    # It is possible to get 1000 results, but it will take some time...
    # for offset in range(0, 1000, 50):
    for offset in range(0, 50, 50):  # Will get 50 results
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


async def get_web_address(url: str, session: aiohttp.ClientSession) -> str:
    try:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")

            href = soup.find("a", {"class": "css-1um3nx", "target": "_blank"}).get(
                "href"
            )
            href = unquote(href)
            href = re.search("url=(.*)&cachebuster=", href)

            return href.group(1)
    except AttributeError:
        return "No web address"


async def get_reviewers_info(url: str, session: aiohttp.ClientSession) -> list:
    async with session.get(url) as response:
        soup = BeautifulSoup(await response.text(), "html.parser")

        all_items = soup.find_all(
            "div", {"class": "review__09f24__oHr9V border-color--default__09f24__NPAKY"}
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

        reviews.append(
            {
                "Reviewer name": name,
                "Reviewer location": reviewer_location,
                "Review date": review_date,
            }
        )

    return reviews


async def main():
    business_category = input("Please enter business category: ") or "contractors"
    business_location = input("Please enter business location: ") or "San Francisco, CA"
    print("Please, wait...")

    businesses_dict = get_businesses(business_category, business_location)

    async with aiohttp.ClientSession() as session:
        for business in businesses_dict["businesses"]:
            (
                business["Business website"],
                business["First five reviews"],
            ) = await asyncio.gather(
                get_web_address(business["Business yelp url"], session),
                get_reviewers_info(business["Business yelp url"], session),
            )

    with open("result.json", "w") as result_file:
        json.dump(businesses_dict, result_file, indent=2)

    print("Done! Check results:")
    print(
        f"file://{quote(os.path.dirname(os.path.abspath('result.json')))}/result.json"
    )


if __name__ == "__main__":
    asyncio.run(main())
