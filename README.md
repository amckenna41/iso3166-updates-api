# iso3166-updates-api

<!-- ![Vercel](https://vercelbadge.vercel.app/api/amckenna41/iso3166-updates-frontend) -->
![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-updates-frontend)
[![iso3166_updates](https://img.shields.io/pypi/v/iso3166-updates)](https://pypi.org/project/iso3166-updates)
[![pytest](https://github.com/amckenna41/iso3166-updates-api/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-updates-api/actions?query=workflowBuilding%20and%20Testing)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-updates)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-updates-api)](https://github.com/amckenna41/iso3166-updates-api/issues)

<div alt="images" style="justify-content: center; display:flex; margin-left=50px;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Flag-map_of_the_world_%282017%29.png" alt="globe" height="200" width="500"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="200" width="300"/>
</div>

> Frontend API for the iso3166-updates repo that returns the latest updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Built using the Python [Flask][flask] framework and hosted on the [Vercel][vercel] platform.

Table of Contents
-----------------
  * [Introduction](#introduction)
  * [API](#api)
  * [Staying up to date](#staying-up-to-date)
  * [Requirements](#requirements)
  * [Issues](#Issues)
  * [Contact](#contact)
  * [References](#references)

Introduction
------------
This repo forms the front-end of the API created for the `iso3166-updates` (https://github.com/amckenna41/iso3166-updates) repository. The API returns the latest updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). Built using the Python [Flask][flask] framework and hosted on the [Vercel][vercel] platform.

The `iso3166-updates`(https://github.com/amckenna41/iso3166-updates) repository is a repo that consists of a series of scripts that check for any updates/changes to the ISO 3166-2 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html). The ISO 3166 standard by the ISO defines codes for the names of countries, dependent territories, special areas of geographical interest, consolidated into the ISO 3166-1 standard [[1]](#references), and their principal subdivisions (e.g., provinces, states, departments, regions), which comprise the ISO 3166-2 standard [[2]](#references). 

The ISO 3166-1 was first published in 1974 and currently comprises 249 countries, 193 of which are sovereign states that are members of the United Nations [[1]](#references). The ISO 3166-2 was first published in 1998 and as of 29 November 2022 there are 5,043 codes defined in it [[2]](#references).

### Problem Statement:

The ISO is a very dynamic organisation and regularly change/update/remove entries within its library of standards, including the ISO 3166. Additions/changes/deletions to country/territorial codes occur less often in the ISO 3166-1, but changes are more frequent for the ISO 3166-2 codes due to there being thousands more entries, thus it can be difficult to keep up with any changes to these codes. These changes can occur for a variety of geopolitical and bureaucratic reasons and are usually communicated via Newsletters on the ISO platform, their Online Browsing Platform (OBP) or via a database, which usually costs money to subscribe to [[3]](#references). Usually these updates are conveyed at the end of the year, with amendments and updates occasionally published at various times throughout the year [[4]](#references). 

This software and accompanying API makes it extremely easy to check for any new or historic updates to a country or set of country's ISO 3166-2 codes for free; with an easy-to-use interface and Python package and API, ensuring that you get the most up-to-date and accurate ISO 3166-2 codes and naming conventions.

<strong> The earliest date for any ISO 3166 updates is 2000-06-21, and the most recent is 2022-11-29. </strong>

### Intended Audience:

This software and accompanying API is for anyone working with country data at the ISO 3166 level. It's of high importance that the data that you are working with is correct and up-to-date, especially with consistent changes being posted every year since 2000 (excluding 2001 and 2006). Also, it's aimed not just at developers of ISO 3166 applications but for anyone working in that space, hence the creation of an easy-to-use API (https://iso3166-updates.com). 

API
---
An API is available that can be used to extract any applicable updates for a country via a URL. The API endpoint is available at the URL:

> https://www.iso3166-updates.com/api

The paths available in the API are below:
* https://www.iso3166-updates.com/api/alpha2
* https://www.iso3166-updates.com/api/year
* https://www.iso3166-updates.com/api/alpha2/{alpha2}/year/{year}
* https://www.iso3166-updates.com/api/months

Three query string parameters are available in the API - `alpha2`, `year` and `months`. 

* The 2 letter alpha-2 country code can be appended to the url as a query string parameter or as its own path ("?alpha2=JP" or /alpha2/JP). A single alpha-2 or list of them can be passed to the API (e.g "?alpha2="FR, DE, HU, ID, MA" or /alpha2/FR,DE,HU,ID,MA). The 3 letter alpha-3 counterpart for each country's alpha-2 code can also be passed into the `alpha2` parameter (e.g "?alpha2="FRA, DEU, HUN, IDN, MAR" or /alpha2/FRA,DEU,HUN,IDN,MAR). 

* The year parameter can be a specific year, year range, or a cut-off year to get updates less than/more than a year (e.g "/year/2017", "2010-2015", "<2009", ">2002"). 

* Finally, the months parameter will gather all updates for 1 or more alpha-2 codes from a number of months from the present day (e.g "?months=2", "/months/6", "/months/48").

* If no input parameter values specified then all ISO 3166-2 updates for all countries and years will be gotten.

The API was hosted and built using GCP, with a Cloud Function being used in the backend which is fronted by an api gateway and load balancer. The function calls a GCP Storage bucket to access the back-end JSON where all ISO 3166 updates are stored. A complete diagram of the architecture is shown below. Although, due to the cost of infrastructure the hosting was switched to Vercel (https://vercel.com/).

The API documentation and usage with all useful commands and examples to the API is available on the [API.md](https://github.com/amckenna41/iso3166-updates-api/API.md) file.

<p align="center">
  <img src="https://raw.githubusercontent.com/amckenna41/iso3166-updates/main/iso3166-updates-api/gcp_arch.png" alt="gcp_arch" height="200" width="400"/>
</p>

Staying up to date
------------------
The list of ISO 3166-2 updates was last updated on <strong>Nov 2022</strong>. The object storing all updates, both locally and on the API, are consistenly checked for the latest updates using a Google Cloud Function ([iso3166-check-for-updates](https://github.com/amckenna41/iso3166-updates/tree/main/iso3166-check-for-updates)). The function uses the `iso3166-updates` Python software to pull all the latest updates/changes from all ISO 3166-2 wiki's to check for the latest updates within a certain period e.g the past 3-6 months. The function compares the generated output with that of the updates json currently in the Google Cloud Storage bucket and will replace this json to integrate the latest updates found such that the API will have the most up-to-date data.

Additionally, a GitHub Issue in the custom-built `iso3166-updates`, `iso3166-2` and `iso3166-flag-icons` repositories will be automatically created that outlines all updates/changes that need to be implemented into the `iso3166-updates`, `iso3166-2` and `iso3166-flag-icons` JSONs and repos.

Ultimately, this Cloud Function ensures that the software and assoicated APIs are up-to-date with the latest ISO 3166-2 information for all countries/territories/subdivisions etc.

Requirements
------------
* [python][python] >= 3.7
* [flask][flask] >= 2.3.2
* [requests][requests] >= 2.28.1
* [iso3166][iso3166] >= 2.1.1
* [python-dateutil][python-dateutil] >= 2.8.2
* [google-auth][google-auth] >= 2.17.3
* [google-cloud-storage][google-cloud-storage] >= 2.8.0
* [google-api-python-client][google-api-python-client] >= 2.86.0

Issues
------
Any issues, errors/bugs or enhancements can be raised via the [Issues](Issues) tab in the repository.

Contact
-------
If you have any questions or comments, please contact amckenna41@qub.ac.uk or raise an issue on the [Issues][Issues] tab. <br><br>
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adam-mckenna-7a5b22151/)

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

[flask]: https://flask.palletsprojects.com/en/2.3.x/
[python]: https://www.python.org/downloads/release/python-360/
[requests]: https://requests.readthedocs.io/
[iso3166]: https://github.com/deactivated/python-iso3166
[python-dateutil]: https://pypi.org/project/python-dateutil/
[google-auth]: https://cloud.google.com/python/docs/reference
[google-cloud-storage]: https://cloud.google.com/python/docs/reference
[google-api-python-client]: https://cloud.google.com/python/docs/reference
[Issues]: https://github.com/amckenna41/iso3166-updates-api/issues
[vercel]: https://vercel.com/