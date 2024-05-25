# Change Log

## v1.7.0

### Added
- 'from_date' query string parameter added that sets the date from which /months endpoint searches from. Primarily added to test the /months endpoint as the unit tests previously used the current date/time thus the outputs of the tests may differ each month
- Add /months/X/name/Y endpoint allowing for searching over the previous number of months for a specified country or list of countries using their country name, as it is commonly known in English
- On /api homepage, programmatically get the version and last updated date of the iso3166-updates software from PyPI

### Changed
- Lower likeness score for searching for country name in /name endpoint
- Reorder credits and contributing sections in /api homepage

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