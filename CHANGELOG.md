# Change Log


## v1.8.7

### Added
- CORS support via `flask-cors`; `Access-Control-Allow-Origin` header now present on all API responses, enabling browser-based clients to consume the API directly.
- `flask-cors` added to `requirements.txt` (was imported but missing, causing Vercel deployment failures).
- `requirements-test.txt` added for test-only dependencies (`beautifulsoup4`, `fake_useragent`, `jsonschema`), keeping them separate from the production requirements.
- New test cases in `tests/test_iso3166_updates_api.py`:
  - `test_cors_headers` — asserts `Access-Control-Allow-Origin` is present on `/all`, `/alpha`, and `/search` responses.
  - `test_sort_ascending` — verifies `sortBy=dateAsc` returns 911 records in oldest-first order and is the exact reverse of `dateDesc`.
  - `test_year_endpoint_list` — exercises the comma-separated year list path in `validate_year` (e.g. `2010,2015`).
  - `test_all_endpoint_invalid_pagination` — confirms `limit=-1`, `offset=-5`, and `limit=abc` all return HTTP 400.
  - `test_404_endpoint` — confirms unknown paths return HTTP 404.
  - `test_fields_parameter_other_endpoints` — verifies `?fields=` projection on `/alpha` and `/search` (was only tested on `/all`).
  - `test_metadata_generated_format` — validates `metadata.generated` matches `YYYY-MM-DDTHH:MM:SSZ` across all endpoint families.
  - `test_country_name_aliases` — tests `names_converted` alias resolution for `Russia`, `United Kingdom`, `Iran`, `Turkey`, and `South Korea`.

### Changed
- `setUpClass` now auto-boots a local Flask server on an ephemeral port when no `BASE_URL` environment variable is set, eliminating dependency on the live production API during testing.
- `setUp` reduced to per-test `User-Agent` rotation only; expensive operations (`Updates()` instantiation, `/api/all` fetch) moved to `setUpClass` so they run once per suite rather than once per test.
- `datetime.utcnow()` (deprecated since Python 3.12) replaced with `datetime.now(timezone.utc)` throughout `index.py`.
- `sort_by` normalisation (`(request.args.get('sortBy') or request.args.get('sortby') or "").lower().rstrip('/')`) applied consistently across all endpoints; previously some endpoints only lowercased one of the two param names.
- Leading space removed from the `"Sao Tome and Principe"` entry in `names_converted` dict.
- `clear_cache` endpoint now returns HTTP 403 when `app.debug` is `False`, preventing cache manipulation on production deployments.

### Fixed
- `api_country_name_year`: sort result was assigned to a new local variable `iso3166_updates` instead of the existing `iso3166_updates_`, causing the sort to be silently discarded. Now correctly assigned.
- `validate_year`: dummy `_ = False` placeholder returns replaced with explicit `True` / `[]` return values.
- `convert_date_format`: two unreachable `try/except` blocks after a `for/else` statement removed (dead code).


## v1.8.6

### Added
- Standardised JSON response envelope for all successful (HTTP 200) endpoints: `{"data": {...}, "metadata": {"count": N, "generated": "<ISO timestamp>"}}`. Error responses (HTTP 400) remain unwrapped.
- Pagination support (`?limit=N&offset=M`) for the `/api/all` endpoint; paginated responses include `total`, `offset`, and `limit` in the `metadata` object.
- `?fields=` query parameter for projecting specific fields from update records (e.g. `?fields=Change,Date+Issued`). Valid fields: `Change`, `Description of Change`, `Date Issued`, `Source`, `Country Code`, `Match Score`.
- `?exclude=YEAR` query parameter as a URL-safe alternative to the `<>YEAR` path syntax for year exclusion on year-based endpoints (e.g. `/api/year?exclude=2020` instead of `/api/year/<>2020` or `/api/year/%3C%3E2020`).
- Informational rate-limit headers added to all responses: `X-RateLimit-Limit: 500` and `X-RateLimit-Policy: 500;w=3600` (advisory only; not enforced on serverless infrastructure).

### Changed
- All successful API responses now wrapped in `{"data": ..., "metadata": {...}}` envelope (breaking change for clients consuming raw response body).
- Year endpoint empty-input error message updated to mention `?exclude=YEAR` as an alternative.
- Tests updated to access response data via `.json()["data"]` for all successful responses; new test cases added for envelope structure, pagination, fields projection, `?exclude` param, and rate-limit headers.
- API.md, README.md and templates/index.html updated to document all new query string parameters, the response envelope format, and rate-limit headers.


## v1.8.0-v1.8.3

### Added
- Extra default parameter value info to each function in index.py
- To avoid redundancy on error messages, a standardised helper function has been added
- Added year not equal to functionality to only return years not equal to a specific year
- In api main code, added separate validate and filter year functions due to their repetitive use
- Added excludeMatchScore query string parameter that allows the user to exclude the "Match Score" in the output search results for the search endpoint
- Added sortBy query parameter to API that allows you to sort the output by countryCode or dateIssued. By default it is countryCode which is just the output sorted in alphabetical order otherwise dateIssued sorts by date Issued, most recent first. Added to all endpoints
- likeness query string parameter added to /name endpoints
- In the /search endpoint, when an explicit date is input as the search term, the date issued column is included in the search. If date is input, search likeness parameter has to be 1
- Sort by date parameter now expanded so you can sort by ascending or descending date
- Tooltip appears when endpoint url copied to clipboard
- Added LRU caching mechanism for the all updates data variable 
- Added a dev only endpoint called '/clear-cache that clears the cached Updates class instance and any updates data
- Added a dev only endpoint called /version that outputs the current version of the iso3166-updates software currently being used

### Changed
- Changed "Code/Subdivision Change" to "Change" & "Edition/Newsletter" to "Source"
- All alpha country codes are passed through convert_to_alpha function rather than just alpha-3 and numeric, for validation. Any format validation is done in this function
- Renamed some variables in year endpoints to follow better naming conventions 
- Updated class name for iso3166-updates software
- Separated the date conversion code into a separate function
- Updated API error message unit tests
- If % match score excluded from search, dict of results returned.
- Likeness score for search changed from float to an int between 1 and 100
- /name endpoint changed to /country_name
- Most functionalities from index.py moved to the backend using the iso3166-updates software itself, rather than having individual functionalities per function on API

### Fixed
- Error with dynamically importing version from pypi
- Spelling error with static css import 
- Fixed year validation code that ensures the valid year and format are input
- Removed any trailing slashes that might be appended to the query string parameter in the url
- Error now returned if input parameters empty that are required
- Fixes across multiple endpoints, ensuring that an error message is always returned if no input parameter value provided, rather than just returning 404.html page
- For multiple endpoints, if there was a trailing or leading comma in the input parameter, an error would be returned, this comma is now just removed 
- Several fixes when searching for string with spaces in it
- Some error messages returning None rather than the original input parameter name, it should be the latter to convey the potential error
- If sortBy query string parameter passed but only one country output object, the original output is returned
- Copy to clipboard functionality fixed on main api page
- Fix with trailing/leading commas in the endpoints
- Several API.md fixes
- Version not displaying correctly on main API homepage
- Fixed several of the unit tests which were using some of the data in the previous iso3166-2 version
- Fixed the error with programmatically pulling the latest month update for the software 

## v1.7.0

### Added
- 'from_date' query string parameter added that sets the date from which /months endpoint searches from. Primarily added to test the /months endpoint as the unit tests previously used the current date/time thus the outputs of the tests may differ each month
- Add /months/X/name/Y endpoint allowing for searching over the previous number of months for a specified country or list of countries using their country name, as it is commonly known in English
- On /api homepage, programmatically get the version and last updated date of the iso3166-updates software from PyPI


### Changed
- Lower likeness score for searching for country name in /name endpoint
- Reorder credits and contributing sections in /api homepage
- Changed order of attributes per updates object. New order: Code/Subdivision change, Description of change, Date issued, Edition/Newsletter
- Upgraded checkout action in workflow from v3 to v4


### Fixed
- Some example links in the api landing page weren't working.
- If a comma separated list of year ranges input, API would retrieve the updates from the latter year range rather than the former
- Spell check on code


## v1.6.0

### Added
- Return closest country name suggestion from one input if it isn't an exact match, "Did you mean X?"
- Add support in /months endpoint for month range where you can search for updates over a specified month range. Add unit tests for this and update docs/API.md
- Parameter typing for each function
- /alpha endpoints now support all ISO 3166-1 alpha codes - alpha-2, alpha-3 and numeric


### Changed
- Remove GCP storage functionality, now using the object within the iso3166-updates software itself
- If no parameter value passed to the endpoints then return error rather than returning all data 
- Reordered app.routes in index.py
- In year endpoints, when searching for updates less than a year, the year itself is not included in the returned data
- Reordered jobs in github workflow file
- In /name endpoint, implementing thefuzz Python package for getting closest country name matches
- More info added to each error message


### Fixed
- In /year endpoint, add extra validation checks when inputting year range so lesser number is on left hand side
- Fixed error for some year endpoints when searching for less than/greater than year
- Copy buttons on api homepage not clicking properly


## v1.5.0


### Added 
- '/' and '/api' endpoints return the same API landing page 
- Update demo notebook with additional API endpoints/paths
- Add /months/X/alpha/Y endpoint allowing for searching over the previous number of months for a specified country or list of countries using their ISO 3166 alpha-2 code. Add unit tests and update API.md
- Add paths-ignore to github workflow


### Changed
- Make example links in the api homepage clickable
- Change border CSS on Endpoints section of api homepage


### Fixed
- Deployment on Vercel was including additional files, fixed .vercelignore file
- Endpoint GET requests not working if a trailing slash added, add app.url_map.strict_slashes = False