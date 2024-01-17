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

> Frontend API for the [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) repo that returns the latest updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui) 🌎. Built using the Python Flask framework and hosted on the Vercel platform. A demo of the API and Python software are available [here][demo_iso3166_updates].

The main API homepage and documentation is available via the URL:

> https://iso3166-updates.com/api

## Table of Contents
- [iso3166-updates-api 🌎](#iso3166-updates-api-)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
    - [Problem Statement](#problem-statement)
    - [Intended Audience](#intended-audience)
  - [Usage](#usage)
  - [Staying up to date](#staying-up-to-date)
  - [Requirements](#requirements)
  - [Issues](#issues)
  - [Contact](#contact)
  - [References](#references)
  - [Support](#support)

Introduction
------------
This repo forms the front-end of the API created for the [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) repository. The API returns the latest updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and naming conventions, as per the ISO 3166 newsletters (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Built using the Python [Flask][flask] framework and hosted on the [Vercel][vercel] platform.

[`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) is a software and accompanying API that consists of a series of scripts that check for any updates/changes to the ISO 3166 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). The ISO 3166 standard by the ISO (International Organization for Standardisation) defines codes for the names of countries, dependent territories, special areas of geographical interest, consolidated into the ISO 3166-1 standard [[1]](#references), and their principal subdivisions (e.g., provinces, states, departments, regions), which comprise the ISO 3166-2 standard [[2]](#references). 

The ISO 3166-1 was first published in 1974 and currently comprises 249 countries, 193 of which are sovereign states that are members of the United Nations 🇺🇳 [[1]](#references). The ISO 3166-2 was first published in 1998 and as of November 2023 there are 5,039 codes defined in it [[2]](#references).

### Problem Statement

The ISO is a very dynamic organisation and regularly change/update/remove entries within its library of standards, including the ISO 3166. Additions/changes/deletions to country/territorial codes occur less often in the ISO 3166-1, but changes are more frequent for the ISO 3166-2 codes due to there being thousands more entries, thus it can be difficult to keep up with and track these changes. These changes can occur for a variety of geopolitical and administrative reasons. Previously these changes were communicated via newsletters; but as of July 2013 these changes are now communicated via their online catalogue/Online Browsing Platform (OBP), or via a database, which usually costs money to subscribe to [[3]](#references). Usually these updates are conveyed at the end of the year, with amendments and updates occasionally published at various times throughout the year [[4]](#references). 

This software and accompanying API make it extremely easy to check for any new or historic updates to a country or set of country's ISO 3166-2 codes for free; with an easy-to-use interface and Python package and API, ensuring that you get the most up-to-date and accurate ISO 3166-2 codes and naming conventions.

<!-- <strong> The earliest date for any ISO 3166 updates is 2000-06-21, and the most recent is 2022-11-29. </strong> -->

### Intended Audience

This software and accompanying API is for anyone working with country data at the ISO 3166 level. It's of high importance that the data that you are working with is correct and up-to-date, especially with consistent changes being posted every year since 2000 (excluding 2001 and 2006). Also, it's aimed not just at developers of ISO 3166 applications but for anyone working in that space, hence the creation of an easy-to-use API and frontend (https://iso3166-updates.com). 

Usage
-----
A demo of the software and API is available [here][demo_iso3166_updates]. Additionally, the documentation for installation and usage of the software and API is availble on the readthedocs platform:

**https://iso3166-updates.readthedocs.io/en/latest/**

The main API endpoint is:

> https://iso3166-updates.com/api

The other endpoints available in the API are:
* https://iso3166-updates.com/api/all
* https://iso3166-updates.com/api/alpha2/<input_alpha2>
* https://iso3166-updates.com/api/name/<input_name>
* https://iso3166-updates.com/api/year/<input_year>
* https://iso3166-updates.com/api/alpha2/<input_alpha2>/year/<input_year>
* https://iso3166-updates.com/api/name/<input_name>/year/<input_year>
* https://iso3166-updates.com/api/months/<input_month>

The paths/endpoints available in the API are - `/api/all`, `/api/alpha2`, `/api/name`, `/api/year` and `/api/months`. 

* The `/api/all` path/endpoint returns all of the ISO 3166 updates/changes data for all countries.

* The 2 letter alpha-2 country code can be appended to the **alpha2** path/endpoint e.g. `/api/alpha2/JP`. A single alpha-2 code or a list of them can be passed to the API e.g. `/api/alpha2/FR,DE,HU,ID,MA`. For redundancy, the 3 letter alpha-3 counterpart for each country's alpha-2 code can also be appened to the path e.g. `/api/alpha2/FRA,DEU,HUN,IDN,MAR`. The **alpha2** endpoint can be used in conjunction with the **year** endpoint to get the country updates for a specific country and year, in the format `/api/alpha2/<input_alpha2>/year/<input_year>` or `/api/year/<input_year>/alpha2/<input_alpha2>`. If an invalid alpha-2 code is input then an error will be returned.

* The <b>name</b> parameter can be a country name as it is most commonly known in English, according to the ISO 3166-1. The name can similarly be appended to the **name** path/endpoint e.g. `/api/name/Denmark`. A single country name or list of them can be passed into the API e.g. `/api/name/France,Moldova,Benin`. A closeness function is used to get the most approximate available country from the one input, e.g. Sweden will be used if the input is `/api/name/Swede`. The **name** endpoint can be used in conjunction with the **year** endpoint to get the country updates for a specific country name and year, in the format `/api/name/<input_name>/year/<input_year>`. If no country is found from the closeness function or an invalid name is input then an error will be returned.

* The **year** parameter can be a specific year, year range, or a cut-off year to get updates less than/more than a year. The year value can be appended to the **year** path/endpoint e.g. `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002`. The **year** endpoint can be used in conjunction with the **alpha2** and **name** endpoints to get the country updates for a specific country and year, in the format `/api/alpha2/<input_alpha2>/year/<input_year>` and `/api/name/<input_name>/year/<input_year>`, respectively. If an invalid year is input then an error will be returned. 

* The **months** parameter will gather all updates for 1 or more countries from an input number of months from the present day. The month value can be appended to the **months** path/endpoint e.g. `/api/months/12`, `/api/months/24`. If an invalid month value is input then an error will be returned.

* The main API endpoint (`/` or `/api`) will return the homepage and API documentation.

The API was hosted and built using GCP, with a Cloud Function being used in the backend which is fronted by an api gateway and load balancer. The function calls a GCP Storage bucket to access the back-end JSON where all ISO 3166 updates are stored. <i>Although, due to the cost of infrastructure, the hosting was switched to Vercel (https://vercel.com/).</i>

The full list of attributes available for each country are:

* Edition/Newsletter: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.
* Date Issued: date that the change was communicated.
* Code/Subdivision change: overall summary of change/update made.
* Description of change in newsletter: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.

Staying up to date
------------------
The list of ISO 3166 updates was last updated on <strong>Nov 2023</strong>.

The object storing all updates, both locally (iso3166-updates.json) for the software pacakge and on the API in GCP Storage bucket, are consistenly checked for the latest updates using a Google Cloud Run microservice ([iso3166-check-for-updates](https://github.com/amckenna41/iso3166-updates/tree/main/iso3166-check-for-updates)). The application is built using a custom Docker container that uses the `iso3166-updates` Python software to pull all the latest updates/changes from the various data sources, to check for the latest updates within a certain period e.g. the past 6-12 months (this month range is used as the ISO usually publishes their updates at the end of the year with occasional mid-year updates). The app compares the generated output with that of the updates JSON currently in the Google Cloud Storage bucket and will replace this json to integrate the latest updates found, such that the API will have the most up-to-date data. A Cloud Scheduler is used to call the application.

Additionally, a GitHub Issue in the custom-built [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates), [`iso3166-2`](https://github.com/amckenna41/iso3166-2) and [`iso3166-flag-icons`](https://github.com/amckenna41/iso3166-flag-icons) repositories will be automatically created that formats and tabulates all updates/changes that need to be implemented into the JSONs on the aforementioned repos.

Ultimately, this Cloud Run microservice ensures that the software and assoicated APIs are up-to-date with the latest and most accurate ISO 3166-2 information for all countries/territories/subdivisions etc.

Requirements
------------
* [python][python] >= 3.7
* [flask][flask] >= 2.3.2
* [requests][requests] >= 2.28.1
* [iso3166][iso3166] >= 2.1.1
* [iso3166-updates][iso3166_updates] >= 1.6.0
* [python-dateutil][python-dateutil] >= 2.8.2

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
<a href="https://www.buymeacoffee.com/amckenna41" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

[Back to top](#TOP)

[demo_iso3166_updates]: https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing
[flask]: https://flask.palletsprojects.com/en/2.3.x/
[python]: https://www.python.org/downloads/release/python-360/
[requests]: https://requests.readthedocs.io/
[iso3166]: https://github.com/deactivated/python-iso3166
[iso3166_updates]: https://github.com/amckenna41/iso3166-updates
[python-dateutil]: https://pypi.org/project/python-dateutil/
[google-auth]: https://cloud.google.com/python/docs/reference
[google-cloud-storage]: https://cloud.google.com/python/docs/reference
[google-api-python-client]: https://cloud.google.com/python/docs/reference
[Issues]: https://github.com/amckenna41/iso3166-updates-api/issues
[vercel]: https://vercel.com/