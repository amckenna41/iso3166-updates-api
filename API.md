# ISO 3166 Updates API 🌎

![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-2-api)

The main API endpoint is:

> https://iso3166-updates.com/api

The other endpoints available in the API are:
* https://iso3166-updates.com/api/all
* https://iso3166-updates.com/api/alpha/<input_alpha>
* https://iso3166-updates.com/api/name/<input_name>
* https://iso3166-updates.com/api/year/<input_year>
* https://iso3166-updates.com/api/alpha/<input_alpha>/year/<input_year>
* https://iso3166-updates.com/api/name/<input_name>/year/<input_year>
* https://iso3166-updates.com/api/months/<input_month>
* https://iso3166-updates.com/api/months/<input_month>/alpha/<input_alpha>

The paths/endpoints available in the API are - `/api/all`, `/api/alpha`, `/api/name`, `/api/year` and `/api/months`. 

* `/api/all`: get all of the ISO 3166 updates/changes data for all countries.

* `/api/alpha`: get all the ISO 3166 updates/changes data for one or more countries according to their ISO 3166-1 alpha-2, alpha-3 or numeric country codes. A single alpha code or a list of them can be passed to the API e.g. `/api/alpha/AL`, `/api/alpha/BW`, `/api/alpha/FR,DE,HUN,IDN,504`. If an invalid alpha code is input then an error will be returned. This endpoint can be used in conjunction with the **year** and **month** endpoints to get the country updates for a specific country and year, and the country updates for a specific country over the past number of months, respectively. This will be in the format: `/api/alpha/<input_alpha>/year/<input_year>` and `/api/alpha/<input_alpha>/months/<input_month>`, respectively.

* `/api/name`: get all the ISO 3166 updates/changes data for one or more countries according to their country name, as listed in the ISO 3166-1. A single country name or list of them can be passed into the API e.g. `/api/name/Brazil`, `/api/name/Colombia`, `/api/name/Benin,France,Moldova`. A closeness function is used to get the most approximate available country from the one input, e.g. Sweden will be used if the input is `/api/name/Swede`. If no matching country is found from the closeness function or an invalid name is input then an error will be returned. This endpoint can be used in conjunction with the **year** and **months** endpoint to get the country updates for a specific country name and year and the country updates for a specific country over the past number of months, respectively. This will be in the format: `/api/name/<input_name>/year/<input_year>` and `/api/name/<input_name>/months/<input_month>`, respectively. 

* `/api/year`: get all the ISO 3166 updates/changes data for one or more countries according to a specific year, year range, or a cut-off year to get updates less than/more than a year, e.g. `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002`. If an invalid year is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** and **name** endpoints to get the country updates for a specific country and year. This will be in in the format `/api/alpha/<input_alpha>/year/<input_year>` and `/api/name/<input_name>/year/<input_year>`, respectively. 

* `/api/months`: get all the ISO 3166 updates/changes data for one or more countries from an input number of months from the present day, e.g. `/api/months/12`, `/api/months/24`, `/api/months/50`. If an invalid month value is input then an error will be returned. This endpoint can be used in conjunction with the **alpha** and **name** endpoints to get the country updates for a specific country over the past number of months using their ISO 3166-1 alpha code or country name, respectively. This will be in the format: `/api/months/<input_month>/alpha/<input_alpha>` and `/api/months/<input_month>/name/<input_name>`, respectively.

* `/api`: main homepage and API documentation.

The API was hosted and built using GCP, with a Cloud Function being used in the backend which is fronted by an api gateway and load balancer. The function calls a GCP Storage bucket to access the back-end JSON where all ISO 3166 updates are stored. <i>Although, due to the cost of infrastructure, the hosting was switched to Vercel (https://vercel.com/).</i>

The full list of attributes available for each country are:

* Edition/Newsletter: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform page.
* Date Issued: date that the change was communicated.
* Code/Subdivision change: overall summary of change/update made.
* Description of change: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.

The API documentation and usage with all useful commands and examples to the API is available below. A demo of the software and API are available [here][demo_iso3166_updates].

Get All ISO 3166 updates for all countries
------------------------------------------
### Request
`GET /api/all`

    curl -i https://www.iso3166-updates.com/api/all

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

request_url = "https://iso3166-updates.com/api/all"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch('https://iso3166-updates.com/api/all');
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country e.g. France (FR), Germany (DEU), Honduras (340)
----------------------------------------------------------------------------------

### Request
`GET /api/alpha/FR`

    curl -i https://iso3166-updates.com/api/alpha/FR

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:30:27 GMT
    server: Vercel
    content-length: 4513

    "FR":[{"Code/Subdivision change":"Codes...}]

### Request
`GET /api/alpha/DE`

    curl -i https://iso3166-updates.com/api/alpha/DEU

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:31:19 GMT
    server: Vercel
    content-length: 10

    {"DE":{}}

### Request
`GET /api/alpha/HN`

    curl -i https://iso3166-updates.com/api/alpha/340

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

base_url = "https://iso3166-updates.com/api/"
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
    await fetch(`https://iso3166-updates.com/api/alpha/${input_alpha}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all updates for a specific year e.g. 2004, 2007
---------------------------------------------------

### Request
`GET /api/year/2004`

    curl -i https://iso3166-updates.com/api/year/2004

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:40:19 GMT
    server: Vercel
    content-length: 10

    {"AF":[{"Code/Subdivision change":""...}]}

### Request
`GET /api/year/2007`

    curl -i https://iso3166-updates.com/api/year/2007

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

base_url = "https://iso3166-updates.com/api/"
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
    await fetch(`https://iso3166-updates.com/api/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country for a specified year e.g. Andorra (AD), Dominica (DM) for 2007
-------------------------------------------------------------------------------------------------

### Request
`GET /api/alpha/AD/year/2007`

    curl -i https://iso3166-updates.com/api/alpha/AD/year/2007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:34:31 GMT
    server: Vercel
    content-length: 227

    {"AD":[{"Code/Subdivision change":"","Date Issued":"2007-04-17"...}]}

### Request
`GET /api/alpha/DM/year/2007`

    curl -i https://iso3166-updates.com/api/alpha/DM/year/2007

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

base_url = "https://iso3166-updates.com/api/"
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
    await fetch(`https://iso3166-updates.com/api/alpha/${input_alpha}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country for a specified year range, using country name e.g. Bosnia, Haiti for 2009-2015
------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/name/Bosnia/year/2009-2015`

    curl -i https://iso3166-updates.com/api/name/Bosnia/year/2009-2015

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 20:19:23 GMT
    server: Vercel
    content-length: 1111

    {"BA":[{"Code/Subdivision change":"","Date Issued":"2015-11-27"...}]}

### Request
`GET /api/name/Haiti/year/2009-2015`

    curl -i https://iso3166-updates.com/api/name/haiti/year/2009-2015

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

base_url = "https://iso3166-updates.com/api/"
input_name = "Bosnia" #Haiti
input_year = "2009-2015"

request_url = base_url + f"name/{input_name}/year/{input_year}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_name = "Bosnia"; //Haiti
let input_year = "2007";

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/name/${input_name}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get updates for a specific country less than/greater than a specified year e.g. Israel (IL), Lithuania (LT) <2010 or >2012
--------------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/alpha/IL/year/<2010`

    curl -i https://iso3166-updates.com/api/alpha/IL/year/<2010

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 05 Mar 2023 17:19:23 GMT
    server: Vercel
    content-length: 3

    {}

### Request
`GET /api/alpha/LT/year/<2012`

    curl -i https://iso3166-updates.com/api/alpha/LT/year/>2012

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

base_url = "https://iso3166-updates.com/api/"
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
  const response = await fetch(`https://iso3166-updates.com/api/alpha/${input_alpha}/year/${input_year}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166 updates data for a specific country, using country name, e.g. Tajikistan, Seychelles, Uganda
--------------------------------------------------------------------------------------------------------------

### Request
`GET /api/name/Tajikistan`

    curl -i https://iso3166-updates.com/api/name/Tajikistan

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:40:19 GMT
    server: Vercel
    content-length: 10

    {"TJ":[{"Code/Subdivision change":...}]}

### Request
`GET /api/name/Seychelles`

    curl -i https://iso3166-updates.com/api/name/Seychelles

### Response
    HTTP/2 200 
    content-type: application/json
    date: Tue, 20 Dec 2022 17:41:53 GMT
    server: Vercel
    content-length: 479

    {"SC":[{"Code/Subdivision change":...}]}

### Request
`GET /api/name/Uganda`

    curl -i https://iso3166-updates.com/api/name/Uganda

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

base_url = "https://iso3166-updates.com/api/"
input_name = "Tajikistan" #Seychelles, Uganda

request_url = base_url + f"name/{input_name}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_name = "Tajikistan"; //Seychelles, Uganda

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/name/${input_name}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```
Get all updates for all countries from the past 3 or 6 months
-------------------------------------------------------------

### Request
`GET /api/months/3`

    curl -i https://iso3166-updates.com/api/months/3

### Response
    HTTP/2 200 
    Date: Thu, 06 Apr 2023 12:36:30 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 3

    {}
### Request
`GET /api/months/6`

    curl -i https://iso3166-updates.com/api/months/6

### Response
    HTTP/2 200 
    Date: Thu, 06 Apr 2023 14:36:30 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 4818

    {"DZ":[{"Code/Subdivision change":""...}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_month = "3" #6

request_url = base_url + f"months/{input_month}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_month = "3"; //6

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/months/${input_month}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all updates for specific country from the past 36 months, e.g. St Kitt's (KN), North Macedonia (MK), Russia (RU)
--------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/months/36/alpha/KN`

    curl -i https://iso3166-updates.com/api/months/36/alpha/KN

### Response
    HTTP/2 200 
    Date: Thu, 06 Mar 2024 11:24:30 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 3

    {}

### Request
`GET /api/months/36/alpha/mk`

    curl -i https://iso3166-updates.com/api/months/36/alpha/MK

### Response
    HTTP/2 200 
    Date: Thu, 06 Mar 2024 12:01:33 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 3

    {}

### Request
`GET /api/months/36/alpha/RU`

    curl -i https://iso3166-updates.com/api/months/36/alpha/RU

### Response
    HTTP/2 200 
    Date: Thu, 06 Mar 2024 12:42:02 GMT
    Connection: close
    Content-Type: application/json
    Content-Length: 282

    {"RU":[{"Code/Subdivision Change":""}]}

### Python
```python
import requests

base_url = "https://iso3166-updates.com/api/"
input_month = "36" 
input_alpha = "KN" #MK, RU

request_url = base_url + f"months/{input_month}/alpha/{input_alpha}"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_month = "36";

function getData() {
  const response = 
    await fetch(`https://iso3166-updates.com/api/months/${input_month}/alpha/${input_alpha}`);
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

[Back to top](#TOP)

[demo_iso3166_updates]: https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing