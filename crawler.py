import json
import os
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote, unquote
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.yelp.com/v3/businesses/"
HEADERS = {
    "accept": "application/json",
    "Authorization": os.getenv("API_KEY")
}


def get_businesses_info(category: str, location: str, limit: str) -> None:
    """
    Using Yelp API Search businesses endpoint I get all the basic information
    and scrape all the additional information with get_web_address and
    get_reviewers_info functions.
    """
    url = urljoin(
        BASE_URL,
        "search?"
        f"location={quote(location)}"
        f"&categories={quote(category)}"
        "&sort_by=best_match"
        f"&limit={limit}"
    )

    response = requests.get(url, headers=HEADERS)
    businesses_data = response.json()

    businesses = dict(
        businesses=list()
    )

    for business in businesses_data["businesses"]:
        businesses["businesses"].append({
            "Business name": business["name"],
            "Business rating": business["rating"],
            "Number of reviews": business["review_count"],
            "Business yelp url": business["url"].split("?adjust")[0],
            "Business website": get_web_address(business["url"]),
            "First five reviews": get_reviewers_info(business["url"])
        })

    with open("result.json", "w") as result_file:
        json.dump(businesses, result_file, indent=2)


def get_web_address(url: str) -> str:
    """
    Yelp API search endpoints return a lot of useful information,
    but the business website can only be accessed from the detail view
    endpoint. I do it with the help of this function.
    """
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    href = soup.find("a", {"class": "css-1um3nx", "target": "_blank"}).get("href")
    href = unquote(href)
    href = re.search("url=(.*)&cachebuster=", href)
    return href.group(1)


def get_reviewers_info(url: str) -> list:
    """
    According to the terms of the task, need to extract 5 reviews,
    with the help of the Yelp API, only three are possible:
    https://docs.developer.yelp.com/reference/v3_business_reviews
    So I used the BeautifulSoup here
    """
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    all_items = soup.find_all("div", {"class": "review__09f24__oHr9V border-color--default__09f24__NPAKY"})

    reviews = []

    for i in all_items[:5]:
        name = i.find("a", {"class": "css-1m051bw"}).text
        reviewer_location = i.find("span", {"class": "css-qgunke"}).text
        review_date = i.find("span", {"class": "css-chan6m"}).text

        reviews.append({
            "Reviewer name": name,
            "Reviewer location": reviewer_location,
            "Review date": review_date
        })

    return reviews


if __name__ == '__main__':
    business_category = input("Please enter business category: ")
    business_location = input("Please enter business location: ")
    sample_limit = input("Please enter sample limit: ")
    get_businesses_info(business_category, business_location, sample_limit)
