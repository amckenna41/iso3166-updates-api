<a name="TOP"></a>

# ISO 3166 Updates API 🌎

![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-2-api)

The main API endpoint and homepage is:

> https://iso3166-updates.vercel.app/

The other endpoints available in the API are `/api/all`, `/api/alpha/<input_alpha>`, `/api/year/<input_year>`, `/api/country_name/<input_country_name>`, `/api/search/<input_search>`, `/api/date_range/<input_date_range>` and `/api/latest`.

* `/api`: main homepage and API documentation.

* `/api/all`: get all of the ISO 3166 updates/changes data for all countries and publication years.

* `/api/alpha`: get all the ISO 3166 updates/changes data for one or more countries according to their ISO 3166-1 alpha-2, alpha-3 or numeric country codes. A single alpha code or a list of them can be passed to the API e.g. `/api/alpha/AL`, `/api/alpha/BWA`, `/api/alpha/FR,DE,HUN,IDN,504`. If an invalid alpha code is input then an error will be returned. This endpoint can be used in conjunction with the **year** and **date_range** endpoints to get the country updates for a specific country and year, and the country updates over a specific date range, respectively. This will be in the format: `/api/alpha/<input_alpha>/year/<input_year>` and `/api/alpha/<input_alpha>/date_range/<input_date_range>`, respectively.

* `/api/year`: get all the ISO 3166 updates/changes data for one or more countries according to a specific year, year range, a cut-off year to get updates less than/more than a year or all updates except for a year, e.g. `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002` and `/api/year/<>2020`. If an invalid year is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** endpoint to get the country updates for a specific country and year. This will be in in the format `/api/alpha/<input_alpha>/year/<input_year>`.

* `/api/country_name`: get all the ISO 3166 updates/changes data for one or more countries according to their name, as it is commonly known in English, e.g. `/api/country_name/Tajikistan`, `/api/country_name/Benin,Togo`, `/api/country_name/Russia,Sudan,Swaziland`. If an invalid country name is input then an error will be returned. This endpoint can be used in conjunction with the **year** endpoint to get the country updates for a specific country and year. This will be in in the format `/api/country_name/<input_country_name>/year/<input_year>`.

* `/api/search`: get all the ISO 3166 updates/changes data for one or more countries that have the inputted search terms. A single keyword/term or list of them can be passed to the API e.g. `/api/search/Brazil`, `/api/search/Addition,deletion`, `/api/search/2017-11-23`. A closeness function is used to search through the updates objects, finding any applicable matches to the keywords input via the Change and Description of Change attributes. If a date is explicitly input then the Date Issued attributes will also be searched. If no matching objects found then an error will be returned. 

* `/api/date_range`: get all the ISO 3166 updates/changes data for one or more countries that were published within a specified input date range e.g. `/api/date_range/2011-12-09,2014-01-10`, `/api/date_range/2013-08-02,2015-07-10`, `/api/date_range/2018-05-12`. If a single date is input it will act as the starting date within the date range, with the end of the range being the current day. An update is included if either its publication date or its corrected date (the date in parenthesis in the Date Issued attribute) falls within the range. If an invalid date type/format value is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** endpoint to get the country updates for a specific country and date range. This will be in in the format `/api/alpha/<input_alpha>/date_range/<input_date_range>`.

* `/api/latest`: get the most recently published ISO 3166 updates/changes data across all countries, sorted by publication date, most recent first. The number of updates returned is set via the **n** query string parameter, e.g. `/api/latest`, `/api/latest?n=5`, `/api/latest?n=100` (default=20). Each returned update has the **Country Code** attribute added to it. If an invalid value for **n** is input then an error will be returned.

* `/api/version`: get the version of the iso3166-updates software that the API is using.

* `/api/spec`: get the OpenAPI specification for the API, also available at `/api/openapi.yaml`.

Attributes
----------
There are four main data attributes for each country updates object:

* <b>Change</b>: overall summary of change/update made.
* <b>Description of Change</b>: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* <b>Date Issue</b>: date that the change was communicated.
* <b>Source</b>: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.

Query String Parameters
-----------------------
There are several query string parameters that can be passed through the API endpoints:

* <b>sortBy</b>: sort the output results by publication date (Date Issued), either descending or ascending. By default, 
the updates data will be returned alphabetically, according to ISO 3166 2 letter country code, but you can order 
by date. The parameter accepts two values: dateDesc and dateAsc - sorting the output by date descending or 
ascending, respectively. If an invalid value input then the output is sorted by country code. This can be appended 
to all of the endpoints, e.g ``/api/all?sortBy=dateDesc``, ``/api/year/2010-2015?sortBy=dateAsc``, 
``/api/date_range/2019-01-01?sortBy=""`` (sorted by country code).
* <b>likeness</b>: this is a value between 0 and 100 that increases or reduces the % of similarity/likeness that the 
inputted search terms have to match to the updates data in the Change and Desc of Change attributes. This can 
be used in the /api/search and /api/country_name endpoints. Having a higher value should return more exact and less matches and 
having a lower value will return less exact but more matches, e.g ``/api/search/Paris?likeness=50``, 
``/api/search/canton?likeness=90`` (default=100).
* <b>excludeMatchScore</b>: exclude the matchScore` attribute from the search results when using the /api/search endpoint. 
The match score is the % of a match each returned updates data object is to the search terms, with 100% being an 
exact match. By default the match score is returned for each object, e.g ``/api/search/addition?excludeMatchScore=1``, 
``/api/search/New York?excludeMatchScore=1`` (default=0).
* <b>exclude</b>: URL-safe alternative to the `<>YEAR` path syntax for year-based endpoints. Use 
``/api/year?exclude=2020`` instead of ``/api/year/<>2020`` to exclude a specific year. This avoids the need 
to URL-encode the `<>` characters (as `%3C%3E`). Available on the year based endpoints, e.g ``/api/year?exclude=2020``, 
``/api/alpha/DE/year?exclude=2019``, ``/api/country_name/Germany/year?exclude=2019``.
* <b>fields</b>: comma-separated list of field names to include in the update records. Only valid field names 
are accepted: `Change`, `Description of Change`, `Date Issued`, `Source`, `Country Code`, `Match Score`. 
Unknown field names are silently ignored. If no valid fields remain, the full record is returned. 
E.g. ``/api/all?fields=Change,Date Issued``, ``/api/year/2020?fields=Change,Source``.
* <b>limit</b>: maximum number of countries (or update records, for the flat list responses) to return per 
page. Available on all of the data endpoints. Used together with `offset` for pagination. 
E.g. ``/api/all?limit=10&offset=0``, ``/api/search/addition?limit=5``, ``/api/date_range/2019-01-01?limit=3``.
* <b>offset</b>: number of countries (or update records) to skip before returning results. Available on all of 
the data endpoints. Used together with `limit` for pagination. E.g. ``/api/all?limit=10&offset=20``.
* <b>format</b>: set to `csv` to return the updates as CSV rather than the JSON envelope. The CSV columns are the 
union of the attributes present in the returned updates, with the `Country Code` column identifying each update's 
country. Available on all of the data endpoints, e.g ``/api/year/2020?format=csv``, ``/api/latest?n=50&format=csv`` 
(default=json).
* <b>n</b>: (``/api/latest`` only) the number of most recently published updates to return, must be a positive 
integer, e.g ``/api/latest?n=5`` (default=20).

**Note:** the pagination is applied at the country level for the country keyed responses and at the update record 
level for the flat list responses (``sortBy=dateAsc/dateDesc``, ``/api/search`` and ``/api/latest``).

**Note:** search terms input to the ``/api/search`` endpoint are limited to 200 characters, longer terms return an error.

Response Envelope
-----------------
All successful (HTTP 200) responses are wrapped in a standard JSON envelope:

```json
{
  "data": { ... },
  "metadata": {
    "count": 250,
    "generated": "2024-01-15T12:34:56.789012"
  }
}
```

The `metadata` object for paginated responses additionally includes `total` (the record count before pagination), 
`offset`, and `limit` fields:

```json
{
  "data": { ... },
  "metadata": {
    "count": 10,
    "generated": "2024-01-15T12:34:56.789012",
    "total": 250,
    "offset": 0,
    "limit": 10
  }
}
```

Error responses (HTTP 400) are **not** wrapped and return the error object directly:

```json
{"message": "...", "path": "...", "status": 400}
```

Rate Limit Headers
------------------
All responses include informational rate limit headers. These are advisory only and not enforced server-side 
(the API runs on serverless infrastructure):

* `X-RateLimit-Limit: 500`
* `X-RateLimit-Policy: 500;w=3600`

Caching
-------
Successful (HTTP 200) JSON and CSV responses are cacheable, the ISO 3166 updates dataset only changes a handful of 
times a year:

* `Cache-Control: public, max-age=3600`
* `ETag: "<hash of the response body>"`

Repeating a request with the returned ETag in an `If-None-Match` header returns an empty `304 Not Modified` if the 
data hasn't changed:

```bash
curl -i -H 'If-None-Match: "2d92e27a4e0f0e68a7c0f935d99f593f746b1f82"' https://iso3166-updates.vercel.app/api/all
```

Documentation
-------------
The API documentation and usage with all useful commands and examples to the API is available below. A demo of the software and API are available [here][demo_iso3166_updates].


Get All ISO 3166 updates for all countries
------------------------------------------
### Request
`GET /api/all`

    curl -i https://iso3166-updates.vercel.app/api/all

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:29:39 GMT
    server: Vercel
    content-length: 202273

    {"AD":...}

### Python
```python
import requests

request_url = "https://iso3166-updates.vercel.app/api/all"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates.vercel.app/api/all');
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country e.g. France (FR), Germany (DEU), Honduras (340)
----------------------------------------------------------------------------------

### Request
`GET /api/alpha/FR`

    curl -i https://iso3166-updates.vercel.app/api/alpha/FR

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:30:27 GMT
    server: Vercel
    content-length: 4513

    "FR":[{"Code/Subdivision change":"Codes...}]

### Request
`GET /api/alpha/DEU`

    curl -i https://iso3166-updates.vercel.app/api/alpha/DEU

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:19 GMT
    server: Vercel
    content-length: 10

    {"DE":{}}

### Request
`GET /api/alpha/340`

    curl -i https://iso3166-updates.vercel.app/api/alpha/340

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:53 GMT
    server: Vercel
    content-length: 479

    {"HN":[{"Code/Subdivision change":""...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"
input_alpha = "FR" #DEU, 340

request_url = base_url + f"alpha/{input_alpha}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_alpha = "FR"; //DEU, 340

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.vercel.app/api/alpha/${input_alpha}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all updates for a specific year e.g. 2004, 2007
---------------------------------------------------

### Request
`GET /api/year/2004`

    curl -i https://iso3166-updates.vercel.app/api/year/2004

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:40:19 GMT
    server: Vercel
    content-length: 10

    {"AF":[{"Code/Subdivision change":""...}]}

### Request
`GET /api/year/2007`

    curl -i https://iso3166-updates.vercel.app/api/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:41:53 GMT
    server: Vercel
    content-length: 479

    {"AD":[{"Code/Subdivision change":""...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"
input_year = "2004" #2007 

request_url = base_url + f"year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_year = "2004"; //2007

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.vercel.app/api/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country for a specified year e.g. Andorra (AD), Dominica (DM) for 2007
-------------------------------------------------------------------------------------------------

### Request
`GET /api/alpha/AD/year/2007`

    curl -i https://iso3166-updates.vercel.app/api/alpha/AD/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:34:31 GMT
    server: Vercel
    content-length: 227

    {"AD":[{"Code/Subdivision change":"","Date Issued":"2007-04-17"...}]}

### Request
`GET /api/alpha/DM/year/2007`

    curl -i https://iso3166-updates.vercel.app/api/alpha/DM/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:38:20 GMT
    server: Vercel
    content-length: 348

    {"DM":[{"Code/Subdivision change":"Subdivisions added:..., "Date Issued": "2007-04-17"}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"
input_alpha = "AD" #DM
input_year = "2007"

request_url = base_url + f"alpha/{input_alpha}/year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_alpha = "AD"; //DM
let input_year = "2007";

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.vercel.app/api/alpha/${input_alpha}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country for a specified year range, using country name e.g. Bosnia, Haiti for 2009-2015
------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/country_name/Bosnia/year/2009-2015`

    curl -i https://iso3166-updates.vercel.app/api/country_name/Bosnia/year/2009-2015

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 20:19:23 GMT
    server: Vercel
    content-length: 1111

    {"BA":[{"Code/Subdivision change":"","Date Issued":"2015-11-27"...}]}

### Request
`GET /api/country_name/Haiti/year/2009-2015`

    curl -i https://iso3166-updates.vercel.app/api/country_name/haiti/year/2009-2015

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 07 Jan 2023 17:19:23 GMT
    server: Vercel
    content-length: 476

    {"HT":[{"Code/Subdivision change":"",...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"
input_name = "Bosnia" #Haiti
input_year = "2009-2015"

request_url = base_url + f"country_name/{input_name}/year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_name = "Bosnia"; //Haiti
let input_year = "2007";

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.vercel.app/api/country_name/${input_name}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country less than/greater than a specified year e.g. Israel (IL), Lithuania (LT) <2010 or >2012
--------------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/alpha/IL/year/<2010`

    curl -i https://iso3166-updates.vercel.app/api/alpha/IL/year/<2010

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 05 Mar 2023 17:19:23 GMT
    server: Vercel
    content-length: 3

    {}

### Request
`GET /api/alpha/LT/year/<2012`

    curl -i https://iso3166-updates.vercel.app/api/alpha/LT/year/>2012

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 07 Jan 2023 17:19:23 GMT
    server: Vercel
    content-length: 637

    {"LT":[{"Code/Subdivision change":...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"
input_alpha = "IL" #LT
input_year = ">2012"

request_url = base_url + f"alpha/{input_alpha}/year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_alpha = "IL"; //LT
let input_year = ">2012";

function getData() {
  const response = await fetch(`https://iso3166-updates.vercel.app/api/alpha/${input_alpha}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166 updates data for a specific country, using country name, e.g. Tajikistan, Seychelles, Uganda
--------------------------------------------------------------------------------------------------------------

### Request
`GET /api/country_name/Tajikistan`

    curl -i https://iso3166-updates.vercel.app/api/country_name/Tajikistan

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:40:19 GMT
    server: Vercel
    content-length: 10

    {"TJ":[{"Code/Subdivision change":...}]}

### Request
`GET /api/country_name/Seychelles`

    curl -i https://iso3166-updates.vercel.app/api/country_name/Seychelles

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:41:53 GMT
    server: Vercel
    content-length: 479

    {"SC":[{"Code/Subdivision change":...}]}

### Request
`GET /api/country_name/Uganda`

    curl -i https://iso3166-updates.vercel.app/api/country_name/Uganda

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 21 Dec 2022 19:43:19 GMT
    server: Vercel
    content-length: 10

    {"UG":[{"Code/Subdivision change":...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"
input_name = "Tajikistan" #Seychelles, Uganda

request_url = base_url + f"country_name/{input_name}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_name = "Tajikistan"; //Seychelles, Uganda

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.vercel.app/api/country_name/${input_name}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Search for updates using keyword or list of keywords
----------------------------------------------------

### Request
`GET /api/search/addition`

    curl -i https://iso3166-updates.vercel.app/api/search/addition

### Response
    HTTP/2 200 
    content-type: application/json
    date: Sun, 10 May 2025 09:50:34 GMT
    server: Vercel
    content-length: 110473

    [{"Change":"Subdivisions added: 7 parishes.","Country Code":"AD","Date Issued"...}]


### Request 
`GET /api/search/canton,state`

    curl -i https://iso3166-updates.vercel.app/api/search/canton,state

### Response
    HTTP/2 200 
    content-type: application/json
    date: Mon, 11 May 2025 11:10:11 GMT
    server: Vercel
    content-length: 7405

    [{"Change":"Change of subdivision category from federal L\u00e4nder to state; update List Source.",...}]


### Request
`GET /api/search/2017-11-27`

    curl -i https://iso3166-updates.vercel.app/api/search/2017-11-27

### Response
    HTTP/2 200 
    content-type: application/json
    date: Mon, 11 May 2025 12:14:17 GMT
    server: Vercel
    content-length: 83

    {"Message":"No matching updates found with the given search term(s): 2017-11-27."}


### Request 
`GET /api/search/canton,state`

    curl -i https://iso3166-updates.vercel.app/api/search/canton,state?likeness=80&excludeMatchScore=1


### Response
    HTTP/2 200 
    content-type: application/json
    date: Thu, 15 May 2025 10:10:48 GMT
    server: Vercel
    content-length: 122709

    [{"Change":"Modification of remark part 2. (Remark part 2: No subdivisions relevant for this standard...)}]



Get all ISO 3166 updates data within a specified date range, inclusive, e.g. 2015-09-16 to 2017-11-12 or 2005-10-03 to 2009-01-01 or 2020-06-19
-----------------------------------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/date_range/2015-09-16,2017-11-12`

    curl -i https://iso3166-updates.vercel.app/api/date_range/'2015-09-16,2017-11-12'

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2024 18:30:11 GMT
    server: Vercel
    content-length: 10

### Request
`GET /api/date_range/2005-10-03,2009-01-01`

    curl -i https://iso3166-updates.vercel.app/api/date_range/'2005-10-03,2009-01-01'?sortBy=dateDesc

### Response
    HTTP/2 200 
    content-type: application/json
    date: Fri, 23 Dec 2024 20:29:01 GMT
    server: Vercel
    content-length: 10

### Request
`GET /api/date_range/2020-06-19

    curl -i https://iso3166-updates.vercel.app/api/date_range/2020-06-19?sortBy=dateAsc

### Response
    HTTP/2 200 
    content-type: application/json
    date: Fri, 23 Dec 2024 23:01:30 GMT
    server: Vercel
    content-length: 10


### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"
input_date_range = "2015-09-16,2017-11-12" #2005-10-03,2009-01-01, 2020-06-19

request_url = base_url + f"date_range/{input_date_range}"

all_request = requests.get(request_url, params={"sortBy": "dateDesc"})
all_request.json() 
```

### Javascript
```javascript
let input_name = "2015-09-16,2017-11-12"; //2005-10-03,2009-01-01, 2020-06-19

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.vercel.app/api/date_range/${input_date_range}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

[Back to top](#TOP)

Get the most recently published ISO 3166 updates across all countries, e.g the latest 20 (default) or the latest 5
------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/latest`

    curl -i https://iso3166-updates.vercel.app/api/latest

### Response
    HTTP/2 200
    content-type: application/json
    cache-control: public, max-age=3600
    server: Vercel

    {"data":[{"Change":"By a letter dated 10 April 2025, the Permanent Representative of The Bahamas confirmed the name of the country, which should be styled with a capital T.","Country Code":"BS","Date Issued":"2025-07-22","Description of Change":"","Source":"Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BS."}],"metadata":{"count":20,"generated":"2025-07-23T13:45:02Z"}}

### Request
`GET /api/latest?n=5`

    curl -i https://iso3166-updates.vercel.app/api/latest?n=5

### Response
    HTTP/2 200
    content-type: application/json
    cache-control: public, max-age=3600
    server: Vercel

    {"data":[{"Change":"By a letter dated 10 April 2025, the Permanent Representative of The Bahamas confirmed the name of the country, which should be styled with a capital T.","Country Code":"BS","Date Issued":"2025-07-22","Description of Change":"","Source":"Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:BS."}],"metadata":{"count":5,"generated":"2025-07-23T13:45:02Z"}}

### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"

request_url = base_url + "latest"

all_request = requests.get(request_url, params={"n": 5})
all_request.json()
```

### Javascript
```javascript
function getData() {
  const response =
    await fetch(`https://iso3166-updates.vercel.app/api/latest?n=5`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

[Back to top](#TOP)

Get the updates data as CSV rather than JSON, e.g all of the updates published in 2020
---------------------------------------------------------------------------------------

### Request
`GET /api/year/2020?format=csv`

    curl -i https://iso3166-updates.vercel.app/api/year/2020?format=csv

### Response
    HTTP/2 200
    content-type: text/csv; charset=utf-8
    content-disposition: attachment; filename=iso3166-updates.csv
    cache-control: public, max-age=3600
    server: Vercel

    Change,Description of Change,Date Issued,Source,Country Code
    Correction of the Code Source.,,2020-11-24,Online Browsing Platform (OBP) - https://www.iso.org/obp/ui/#iso:code:3166:AF.,AF

### Python
```python
import requests

base_url = "https://iso3166-updates.vercel.app/api/"
input_year = "2020"

request_url = base_url + f"year/{input_year}"

all_request = requests.get(request_url, params={"format": "csv"})
all_request.text
```

[Back to top](#TOP)

[demo_iso3166_updates]: https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing