# Yelp Crawler
## Scraps businesses from [Yelp](https://www.yelp.com/) website.

## Features:

* You can get information about 1000 businesses registered on Yelp.
* The crawler should be given category of business and location as an input.
* Returns a result.json file, representing a business from the given search results

## JSON file will look like this:

<img width="751" alt="Screenshot 2022-12-17 at 16 51 25" src="https://user-images.githubusercontent.com/111114742/208247757-c0bac924-6581-4a0e-bcd6-c7daa819ebaf.png">

# Installation

### [Python 3](https://www.python.org/downloads/) must be already installed

```shell
git clone https://github.com/VadymShkarbul/Yelp-Crawler.git
cd Yelp-Crawler
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Create .env file in the project directory and put there your API_KEY in next format: 
```shell
API_KEY = YOUR_API_KEY
```
### Get API key on this page https://www.yelp.com/developers/v3/manage_app
