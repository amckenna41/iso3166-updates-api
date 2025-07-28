<a name="TOP"></a>

# iso3166-updates-api 🌎

<!-- ![Vercel](https://vercelbadge.vercel.app/api/amckenna41/iso3166-updates-frontend) -->
<!-- ![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-updates-frontend) -->
![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-2-api)
[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates)
[![pytest](https://github.com/amckenna41/iso3166-updates-api/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates-api/actions?query=workflowBuilding%20and%20Testing)
[![Documentation Status](https://readthedocs.org/projects/iso3166-updates/badge/?version=latest)](https://iso3166-updates.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-updates-api)](https://github.com/amckenna41/iso3166-updates-api/issues)

<div alt="images" style="justify-content: center; display:flex; margin-left=50px;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Flag-map_of_the_world_%282017%29.png" alt="globe" height="200" width="500"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="200" width="300"/>
</div>

> Frontend API for the [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) repo that returns the latest updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui) 🌎. Built using the Python Flask framework and hosted on the Vercel platform. 

Quick Start 🏃
-------------
* The main **iso3166-updates** software is available [here][iso3166_updates].
* A <b>demo</b> of the API and Python software is available [here][demo_iso3166_updates].
* A <b>Medium</b> article that dives deeper into `iso3166-updates` is available [here][medium].
* The **documentation** for the API is available [here](https://iso3166-updates.readthedocs.io/en/latest/).

The main API homepage and documentation is available via the URL:

> https://iso3166-updates.vercel.app/api

Table of Contents
-----------------
- [Introduction](#introduction)
- [Documentation](#documentation)
- [Usage](#usage)
- [Staying up to date](#staying-up-to-date)
- [Other ISO 3166 Repositories](#other-iso-3166-repositories)
- [Issues](#issues)
- [Contact](#contact)
- [References](#references)
- [Support](#support)

Introduction
------------
This repo forms the front-end of the API created for the [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) repository. The API returns the latest updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and naming conventions, as per the ISO 3166 newsletters (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Built using the Python [Flask][flask] framework and hosted on the [Vercel][vercel] platform.

[`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) is a software and accompanying API that consists of a series of scripts that check for any updates/changes to the ISO 3166 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). The ISO 3166 standard by the ISO (International Organization for Standardisation) defines codes for the names of countries, dependent territories, special areas of geographical interest, consolidated into the ISO 3166-1 standard [[1]](#references), and their principal subdivisions (e.g., provinces, states, departments, regions), which comprise the ISO 3166-2 standard [[2]](#references). 

The ISO 3166-1 was first published in 1974 and currently comprises 249 countries, 193 of which are sovereign states that are members of the United Nations 🇺🇳 [[1]](#references). The ISO 3166-2 was first published in 1998 and as of November 2023 there are **5,039** codes defined in it [[2]](#references).

### Problem Statement

The ISO is a very dynamic organisation and regularly change/update/remove entries within its library of standards, including the ISO 3166. Additions, changes and deletions to country/territorial codes occur less often in the ISO 3166-1, but changes are more frequent for the ISO 3166-2 codes due to there being thousands more entries, thus it can be difficult to keep up with and track these changes. These changes can occur for a variety of geopolitical and administrative reasons. Previously these changes were communicated via newsletters, but as of July 2013 these changes are now communicated via their online catalogue/Online Browsing Platform (OBP), or via a database, which usually costs money to subscribe to [[3]](#references). Usually these updates are conveyed at the end of the year, with amendments and updates occasionally published at various times throughout the year [[4]](#references). 

This software and accompanying API make it extremely easy to check for any new or historic updates to a country or set of country's ISO 3166-2 codes for free; with an easy-to-use interface and Python package and API, ensuring that you get the most **up-to-date** and **accurate** ISO 3166-2 codes and naming conventions.

<!-- <strong> The earliest date for any ISO 3166 updates is 2000-06-21, and the most recent is 2022-11-29. </strong> -->

### Intended Audience

This software and accompanying API is for anyone working with country data at the ISO 3166 level. It's of high importance that the data that you are working with is correct and up-to-date, especially with consistent changes being posted every year since 2000 (excluding 2001 and 2006). Also, it's aimed not just at developers of ISO 3166 applications but for anyone working in that space, hence the creation of this easy-to-use API and frontend (https://iso3166-updates.vercel.app/api). 


Documentation
-------------
Documentation for the API is available on the software's [readthedocs](https://iso3166-updates.readthedocs.io/en/latest/) page as well as the API's [homepage](https://iso3166-updates.vercel.app/api).

Usage
-----
The main API endpoint and homepage is:

> https://iso3166-updates.vercel.app/

The other endpoints available in the API are:
* https://iso3166-updates.vercel.app/api/all
* https://iso3166-updates.vercel.app/api/alpha/<input_alpha>
* https://iso3166-updates.vercel.app/api/year/<input_year>
* https://iso3166-updates.vercel.app/api/search/<input_search>
* https://iso3166-updates.vercel.app/api/date_range/<input_date_range>
* https://iso3166-updates.vercel.app/api/alpha/<input_alpha>/year/<input_year>
* https://iso3166-updates.vercel.app/api/date_range/<input_date_range>/alpha/<input_alpha>
* https://iso3166-updates.vercel.app/api/date_range/<input_date_range>/year/<input_year>

The main paths/endpoints available in the API are - `/api/all`, `/api/alpha`, `/api/year`, `/api/country_name`, `/api/search` and `/api/date_range`.

* `/api/all`: get all of the ISO 3166 updates/changes data for all countries and publication years.

* `/api/alpha`: get all the ISO 3166 updates/changes data for one or more countries according to their ISO 3166-1 alpha-2, alpha-3 or numeric country codes. A single alpha code or a list of them can be passed to the API e.g. `/api/alpha/AL`, `/api/alpha/BWA`, `/api/alpha/FR,DE,HUN,IDN,504`. If an invalid alpha code is input then an error will be returned. This endpoint can be used in conjunction with the **year** and **date_range** endpoints to get the country updates for a specific country and year, and the country updates over a specific date range, respectively. This will be in the format: `/api/alpha/<input_alpha>/year/<input_year>` and `/api/alpha/<input_alpha>/date_range/<input_date_range>`, respectively.

* `/api/year`: get all the ISO 3166 updates/changes data for one or more countries according to a specific year, year range, a cut-off year to get updates less than/more than a year or all updates except for a year, e.g. `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002` and `/api/year/<>2020`. If an invalid year is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** endpoint to get the country updates for a specific country and year. This will be in in the format `/api/alpha/<input_alpha>/year/<input_year>`.

* `/api/country_name`: get all the ISO 3166 updates/changes data for one or more countries according to their name, as it is commonly known in English, e.g. `/api/country_name/Tajikistan`, `/api/country_name/Benin,Togo`, `/api/country_name/Russia,Sudan,Swaziland`. If an invalid country name is input then an error will be returned. This endpoint can be used in conjunction with the **year** endpoint to get the country updates for a specific country and year. This will be in in the format `/api/country_name/<input_country_name>/year/<input_year>`.

* `/api/search`: get all the ISO 3166 updates/changes data for one or more countries that have the inputted search terms. A single keyword/term or list of them can be passed to the API e.g. `/api/search/Brazil`, `/api/search/Addition,deletion`, `/api/search/2017-11-23`. A closeness function is used to search through the updates objects, finding any applicable matches to the keywords input via the Change and Description of Change attributes. If a date is explicitly input then the Date Issued attributes will also be searched. If no matching objects found then an error will be returned. 

* `/api/date_range`: get all the ISO 3166 updates/changes data for one or more countries that were published within a specified input date range e.g. `/api/date_range/2011-12-09,2014-01-10`, `/api/date_range/2013-08-02,2015-07-10`, `/api/date_range/2018-05-12`. If a single date is input it will act as the starting date within the date range, with the end of the range being the current day. If an invalid date type/format value is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** endpoint to get the country updates for a specific country and date range. This will be in in the format `/api/alpha/<input_alpha>/date_range/<input_date_range>`.

* `/api`: main homepage and API documentation.

### Attributes
There are three main query string parameters that can be passed through several of the endpoints of the API:

* <b>Change</b>: overall summary of change/update made.
* <b>Description of Change</b>: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* <b>Date Issue</b>: date that the change was communicated.
* <b>Source</b>: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.

### Query String Parameters
There are three main query string parameters that can be passed through several of the endpoints of the API:

* <b>sortBy</b>: sort the output results by publication date (Date Issued), either descending or ascending. By default, 
the updates data will be returned alphabetically, according to ISO 3166 2 letter country code, but you can order 
by date. The parameter accepts two values: dateDesc and dateAsc - sorting the output by date descending or 
ascending, respectively. If an invalid value input then the output is sorted by country code. This can be appended 
to all of the endpoints, e.g ``/api/all?sortBy=dateDesc``, ``/api/year/2010-2015?sortBy=dateAsc``, 
``/api/date_range/2019-01-01?sortBy=""`` (sorted by country code).
* <b>likeness</b>: this is a value between 1 and 100 that increases or reduces the % of similarity/likeness that the 
inputted search terms have to match to the updates data in the Change and Desc of Change attributes. This can 
only be used in the /api/search endpoint. Having a higher value should return more exact and less matches and 
having a lower value will return less exact but more matches, e.g ``/api/search/Paris?likeness=50``, 
``/api/search/canton?likeness=90`` (default=100).
* <b>excludeMatchScore</b>: exclude the matchScore attribute from the search results when using the /api/search endpoint. 
The match score is the % of a match each returned updates data object is to the search terms, with 100% being an 
exact match. By default the match score is returned for each object, e.g ``/api/search/addition?excludeMatchScore=1``, 
``/api/search/New York?excludeMatchScore=1`` (default=0).

Staying up to date
------------------
The list of ISO 3166 updates was last updated on <strong>Nov 2024</strong>.

The dataset of ISO 3166 updates is regularly checked and updated via a custom-built Google Cloud Run microservice ([iso3166-check-for-updates](https://github.com/amckenna41/iso3166-updates/tree/main/iso3166_check_for_updates)). The application is built using a custom Docker container that uses the [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) Python software to pull all the latest updates/changes from the various data sources, to check for the latest updates within a certain period e.g. the past 6-12 months (this month range is used as the ISO usually publishes their updates at the end of the year with occasional mid-year updates). The app compares the generated output with that of the updates JSON currently utilised within the software package. A Cloud Scheduler is used to call the application, within the specified cadence. 

Additionally, a GitHub Issue in the custom-built [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates), [`iso3166-2`](https://github.com/amckenna41/iso3166-2) and [`iso3166-flag-icons`](https://github.com/amckenna41/iso3166-flag-icons) repositories will be automatically created that formats and tabulates all updates/changes that need to be implemented into the JSONs on the aforementioned repos.

Ultimately, this Cloud Run microservice ensures that the software and associated APIs are **up-to-date** with the **latest** and **most accurate** ISO 3166-2 information for all countries/territories/subdivisions etc.

Running Flask app locally
-------------------------
The Flask app can be run locally for testing/development directly via Flask command or via Python.

```bash
export FLASK_APP=index.py
export FLASK_ENV=development
flask run
```

```python
python index.py
```

Other ISO 3166 repositories
---------------------------
Below are some of my other custom-built repositories that relate to the ISO 3166 standard.

* [iso3166-updates](https://github.com/amckenna41/iso3166-update): software and accompanying API that checks for any updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui).
* [iso3166-2](https://github.com/amckenna41/iso3166-2): a lightweight custom-built Python package, and accompanying API, that can be used to access all of the world's ISO 3166-2 subdivision data. A plethora of data attributes are available per country and subdivision including: name, local name, code, parent code, type, lat/longitude and flag. Currently, the package and API supports data from 250 countries/territories, according to the ISO 3166-1 standard.
* [iso3166-2-api](https://github.com/amckenna41/iso3166-2-api): frontend API for iso3166-2.
* [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons): a comprehensive library of over 3500 country and regional flags from the ISO 3166-1 and ISO 3166-2 standards.

Issues
------
Any issues, errors/bugs or enhancements can be raised via the [Issues](Issues) tab in the repository.

Contact
-------
If you have any questions or comments, please contact amckenna41@qub.ac.uk or raise an issue on the [Issues][Issues] tab. <br><br>
<!-- [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adam-mckenna-7a5b22151/) -->

References
----------
\[1\]: ISO3166-1: https://en.wikipedia.org/wiki/ISO_3166-1 <br>
\[2\]: ISO3166-2: https://en.wikipedia.org/wiki/ISO_3166-2 <br>
\[3\]: ISO Country Codes Collection: https://www.iso.org/publication/PUB500001 <br>
\[4\]: ISO Country Codes: https://www.iso.org/iso-3166-country-codes.html <br>
\[5\]: ISO3166-1 flag-icons repo: https://github.com/lipis/flag-icons <br>
\[6\]: ISO3166-2 flag-icons repo: https://github.com/amckenna41/iso3166-flag-icons <br>

Support
-------
[<img src="https://img.shields.io/github/stars/amckenna41/iso3166-updates-api?color=green&label=star%20it%20on%20GitHub" width="132" height="20" alt="Star it on GitHub">](https://github.com/amckenna41/iso3166-updates-api) <br><br>
<a href="https://www.buymeacoffee.com/amckenna41" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

[Back to top](#TOP)

[demo_iso3166_updates]: https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing
[flask]: https://flask.palletsprojects.com/en/2.3.x/
[python]: https://www.python.org/downloads/release/python-360/
[requests]: https://requests.readthedocs.io/
[iso3166]: https://github.com/deactivated/python-iso3166
[iso3166_updates]: https://github.com/amckenna41/iso3166-updates
[python-dateutil]: https://pypi.org/project/python-dateutil/
[thefuzz]: https://pypi.org/project/thefuzz/
[google-auth]: https://cloud.google.com/python/docs/reference
[google-cloud-storage]: https://cloud.google.com/python/docs/reference
[google-api-python-client]: https://cloud.google.com/python/docs/reference
[Issues]: https://github.com/amckenna41/iso3166-updates-api/issues
[vercel]: https://vercel.com/
[medium]: https://medium.com/@ajmckenna69/iso3166-updates-d06b817af3a7