from flask import Flask, request, render_template, jsonify
import iso3166
from iso3166_updates import *
import re
import urllib.parse
from thefuzz import fuzz, process
from urllib.parse import unquote
from datetime import datetime
from functools import lru_cache

########################################################## Endpoints ##########################################################
'''
/api - main homepage for API, displaying purpose, examples and documentation
/api/all - return all updates data for all countries
/api/alpha/<input_alpha> - return all updates data for input country using its ISO 3166-1 alpha-2, alpha-3 or numeric codes  
/api/year/<input_year> - return all updates data for input year, list of years, year range, greater/less than input year or
        not equal to a year
/api/country_name/<input_country_name> - return all updates for input country name, as its commonly known in English
/api/search/<search_term> - return all updates that have the inputted search term/terms
/api/alpha/<input_alpha>/year/<input_year> - return all updates data for input ISO 3166-1 alpha-2, alpha-3 or numeric country 
      code + year, list of years, year range, greater/less than input year or not equal to a year
/api/year/<input_year>/name/<input_country_name> - return all updates data for input country name + year, list of years, year range 
      or greater/less than input year or not equal to a year
/api/date_range/<input_date_range> -  return all updates data within the specified date range.
/api/date_range/<input_date_range>/alpha/<input_alpha> - return all updates data within the specified date range for input country
      using its ISO 3166-1 alpha-2, alpha-3 or numeric codes
'''
###############################################################################################################################


################################################### Query String Parameters ###################################################
'''
sortBy - this parameter allows you to sort the output results by publication date (Date Issued), either descending or ascending.
By default, the updates data will be returned alphabetically, according to ISO 3166 2 letter country code. The parameter accepts 
two values: dateDesc and dateAsc - sorting the output by date descending or ascending, respectively. If an invalid value input 
then the output is sorted by country code. This can be appended to all of the endpoints, e.g /api/all?sortBy=dateDesc, 
/api/year/2010-2015?sortBy=dateAsc, /api/date_range/2019-01-01?sortBy="" (sorted by country code).

likeness - this is a parameter between 1 and 100 that increases or reduces the % similarity/likeness that the inputted search 
terms have to match to the updates data in the Change and Desc of Change attributes. This can be used with the /api/search and
/api/country_name endpoints. Having a higher value should return more exact and less matches, and having a lower value will 
return less exact but more matches, e.g /api/search/Paris?likeness=50, /api/search/canton?likeness=90 (default=100).

excludeMatchScore - this parameter allows you to exclude the matchScore attribute from the search results when using the 
/api/search endpoint. The match score is the % of a match each returned updates data object is to the search terms, with 100% 
being an exact match. By default the match score is returned for each object, e.g /api/search/addition?excludeMatchScore=1, 
/api/search/New York?excludeMatchScore=1 (default=0).
'''
###############################################################################################################################

#initialise Flask app
app = Flask(__name__)

#register routes/endpoints with or without trailing slash
app.url_map.strict_slashes = False

@lru_cache()
def get_updates_instance():
    """ Cache function for initialization of Updates instance. """
    return Updates()

@lru_cache()
def get_all_updates():
    """ Cache function for all data variable of Updates instance. """
    return get_updates_instance().all

@app.route('/api')
@app.route('/')
def home():
    """
    Default route for https://iso3166-updates.vercel.app. Main homepage for API 
    displaying the purpose of API and its documentation.

    Parameters
    ==========
    None

    Returns
    =======
    :flask.render_template: html
      Flask html template for index.html page.
    """
    return render_template('index.html')

@app.route('/api/all', methods=['GET'])
@app.route('/all', methods=['GET'])
def all() -> tuple[dict, int]:
    """
    Flask route for '/api/all' path/endpoint. Return all ISO 3166-2 updates data for all 
    available countries.

    Parameters
    ==========
    None

    Returns
    =======
    :all_updates: json
        jsonified ISO 3166 updates data.
    :status_code: int
        response status code. 200 is a successful response.
    """  
    #pull sortBy/sortby query string parameter, that allows sorting by publication date, descending/ascending
    sort_by = (request.args.get('sortBy') or request.args.get('sortby') or "").lower().rstrip('/')
    
    #output var of all updates
    all_updates = get_all_updates()
    
    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date
    if (sort_by == 'dateasc' or sort_by == 'datedesc'):
        all_updates = sort_by_date(get_all_updates(), date_asc_desc=sort_by)

    return jsonify(all_updates), 200

@app.route('/alpha', methods=['GET'])
@app.route('/api/alpha', methods=['GET'])
@app.route('/api/alpha/<input_alpha>', methods=['GET'])
@app.route('/alpha/<input_alpha>', methods=['GET'])
def api_alpha(input_alpha: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/alpha' path/endpoint. Return all ISO 3166 updates for the inputted 
    ISO 3166-1 alpha-2, alpha-3 or numeric country code/codes. The alpha-3 and numeric codes will 
    be converted into their corresponding alpha-2 code. A single or list of alpha codes can be 
    input. If an invalid alpha code input then return error. Additionally, the endpoint can be 
    used in conjunction with the year and date range endpoints. 

    Parameters
    ==========
    :input_alpha: str (default="")
        1 or more alpha-2, alpha-3 or numeric country codes according to the ISO 3166-1 standard. 
        The alpha-3 and numeric codes will be converted into their alpha-2 counterparts.

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input alpha code/codes.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates = {}

    #pull sortBy query string parameter, that allows sorting by country code or publication date, descending/ascending
    sort_by = request.args.get('sortBy', default="") or request.args.get('sortby', default="").lower().rstrip('/')

    #if no input alpha parameter then return error message
    if (input_alpha == ""):
        return jsonify(create_error_message("The ISO 3166-1 alpha input parameter cannot be empty.", request.url)), 400    

    #get the country updates data using the input alpha codes, return error if invalid codes input
    try:
        iso3166_updates = get_updates_instance()[input_alpha]
    except ValueError as ve:
        return jsonify(create_error_message(str(ve), request.url)), 400    

    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date, ascending or descending, don't sort if just one country object present
    if (sort_by == 'dateasc' or sort_by == 'datedesc') and len(iso3166_updates) > 1:
        iso3166_updates = sort_by_date(iso3166_updates, date_asc_desc=sort_by)

    return jsonify(iso3166_updates), 200

@app.route('/year', methods=['GET'])
@app.route('/api/year', methods=['GET'])
@app.route('/api/year/<input_year>', methods=['GET'])
@app.route('/year/<input_year>', methods=['GET'])
def api_year(input_year: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/year' path/endpoint. Return all ISO 3166 updates for the inputted 
    year, list of years, year range, greater than or less than input year or all updates
    excluding a year/list of years. If invalid year or symbol input then return error. 

    Parameters
    ==========
    :input_year: str (default="")
        year, comma separated list of years, year range to get updates from. Can also accept 
        greater than or less than symbol returning updates greater than/less than specified 
        year or <> which indicates to exclude the years.

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input year/years.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an invalid 
        parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    
    #pull sortBy query string parameter, that allows sorting by country code or publication date, descending/ascending
    sort_by = request.args.get('sortBy', default="") or request.args.get('sortby', default="").lower().rstrip('/')

    #if no input year parameter then return error message
    if (input_year == ""):
        return jsonify(create_error_message("The year input parameter cannot be empty.", request.url)), 400    

    #remove any unicode characters
    input_year = urllib.parse.unquote(input_year)

    #get the country updates fot the input years, return error if invalid years input
    try:
        iso3166_updates = get_updates_instance().year(input_year)
    except ValueError as ve:
        return jsonify(create_error_message(str(ve), request.url)), 400    

    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date, ascending or descending, don't sort if just one country object present
    if (sort_by == 'dateasc' or sort_by == 'datedesc') and len(iso3166_updates) > 1:
        iso3166_updates = sort_by_date(iso3166_updates, date_asc_desc=sort_by)

    return jsonify(iso3166_updates), 200

@app.route('/api/year/<input_year>/alpha/<input_alpha>', methods=['GET'])
@app.route('/api/alpha/<input_alpha>/year/<input_year>', methods=['GET'])
@app.route('/year/<input_year>/alpha/<input_alpha>', methods=['GET'])
@app.route('/alpha/<input_alpha>/year/<input_year>', methods=['GET'])
@app.route('/api/year/<input_year>/alpha/', defaults={'input_alpha': ""}, methods=['GET'])
@app.route('/api/alpha/<input_alpha>/year/', defaults={'input_year': ""}, methods=['GET'])
def api_alpha_year(input_alpha: str="", input_year: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/alpha' + '/api/year' path/endpoint. Return all ISO 3166 
    updates for the inputted ISO 3166-1 alpha-2, alpha-3 or numeric country code/codes 
    + year/years/year range, greater than or less than input year or not equal to a year. 
    The alpha-3 and numeric codes will be converted into their corresponding alpha-2 code. 
    If invalid alpha code or year/years input then return error. Route can accept the 
    path with or without the trailing slash.
    
    Parameters
    ==========
    :input_alpha: str (default="")
        1 or more ISO 3166-1 alpha-2, alpha-3 or numeric country codes.
    :input_year: str (default="")
        year, comma separated list of years, or year range to get updates from. Can 
        also accept greater than or less than symbol returning updates greater 
        than/less than specified year or updates not equal to year/list of years.

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input alpha-2 code and year.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    alpha2_code = []

    #pull sortBy query string parameter, that allows sorting by country code or publication date, descending/ascending
    sort_by = request.args.get('sortBy', default="") or request.args.get('sortby', default="").lower().rstrip('/')

    #parse alpha code parameter, split, uppercase, remove any whitespace and sort
    alpha2_code = sorted(input_alpha.strip(",").replace('%20', '').split(','))

    #if no input year parameter then return error message
    if (input_year == ""):
        return jsonify(create_error_message("The year input parameter cannot be empty.", request.url)), 400    
        
    #if no input alpha parameter then return error message
    if (input_alpha == ""):
        return jsonify(create_error_message("The alpha code input parameter cannot be empty.", request.url)), 400    
    
    #parse and validate input year parameter 
    year, year_range, year_greater_than, year_less_than, year_not_equal, year_error, year_error_message = validate_year(input_year)

    #return error if error found when parsing and validating the year input parameter
    if (year_error):
        return jsonify(create_error_message(year_error_message, request.url)), 400    

    #iterate over each input alpha code, validating and converting into its corresponding alpha-2, if applicable
    if (alpha2_code != []):
        for code in range(0, len(alpha2_code)):
            #api can accept 3 letter alpha-3 or numeric code for country, this has to be converted into its alpha-2 counterpart
            temp_code = convert_to_alpha2(alpha2_code[code])
            #return error message if invalid alpha code input
            if (temp_code is None):
                return jsonify(create_error_message(f"Invalid ISO 3166-1 country code input, cannot convert into corresponding alpha-2 code: {''.join(alpha2_code[code])}.", request.url)), 400 
            alpha2_code[code] = temp_code

    #get updates from iso3166_updates object per country using alpha-2 code
    for code in alpha2_code:
        iso3166_updates[code] = get_all_updates()[code]

    #temporary updates object
    temp_iso3166_updates = {}

    #if no valid alpha-2 codes input, use all alpha-2 codes from iso3166 and all updates data
    if ((year != [] and alpha2_code == []) or ((year == [] or year != []) and alpha2_code == [])):
        input_alpha_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = get_all_updates()
    #else set input alpha-2 codes to input parameter value and use corresponding updates data
    else:
        input_alpha_codes = alpha2_code
        input_data = iso3166_updates
    
    #use temp object to get updates data either for specific country/alpha-2 code or for all
    #countries, dependant on input_alpha_codes and input_data vars above
    if (year != []):
        for code in input_alpha_codes:
            temp_iso3166_updates[code] = []
            for update in range(0, len(input_data[code])):

                #convert year in Date Issued column to str of year, remove "corrected" date if applicable
                if ("corrected" in input_data[code][update]["Date Issued"]):
                    temp_year = str(datetime.strptime(re.sub("[(].*[)]", "", input_data[code][update]["Date Issued"]).replace(' ', "").
                                                      replace(".", '').replace('\n', ''), '%Y-%m-%d').year)
                else:
                    temp_year = str(datetime.strptime(input_data[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d').year)

                #if year range true then get country updates within specified range inclusive
                if (year_range):
                    if (temp_year != "" and (temp_year >= year[0] and temp_year <= year[1])):
                        temp_iso3166_updates[code].append(input_data[code][update])
                
                #if greater than true then get country updates greater than or equal to specified year
                elif (year_greater_than):
                    if (temp_year != "" and (temp_year >= year[0])):
                        temp_iso3166_updates[code].append(input_data[code][update])    

                #if less than true then get country updates less than specified year 
                elif (year_less_than):
                    if (temp_year != "" and (temp_year < year[0])):
                        temp_iso3166_updates[code].append(input_data[code][update]) 

                #get all country updates not equal to current year
                elif (year_not_equal):
                    if (temp_year != "" and temp_year not in year):
                        temp_iso3166_updates[code].append(input_data[code][update])

                #get country updates equal to specified year
                else:
                    for year_ in year:
                        if (temp_year != "" and (temp_year == year_)):
                            temp_iso3166_updates[code].append(input_data[code][update])

            #if current alpha-2 has no rows for selected year/year range etc, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = input_data
    
    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date, ascending or descending, don't sort if just one country object present
    if (sort_by == 'dateasc' or sort_by == 'datedesc') and len(temp_iso3166_updates) > 1:
        iso3166_updates = sort_by_date(temp_iso3166_updates, date_asc_desc=sort_by)
    else:
        #set main updates dict to temp one
        iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/api/country_name', methods=['GET'])
@app.route('/api/country_name/<input_country_name>', methods=['GET'])
@app.route('/api/country_name/<input_country_name>/year', methods=['GET'])
@app.route('/api/country_name/<input_country_name>/date_range', methods=['GET'])
@app.route('/country_name/<input_country_name>', methods=['GET'])
@app.route('/country_name/<input_country_name>/year', methods=['GET'])
@app.route('/country_name/<input_country_name>/date_range', methods=['GET'])
def api_country_name(input_country_name: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/country_name' path/endpoint. Return all ISO 3166 updates for the 
    inputted country name/names, as they are commonly known in English. A closeness 
    function is used to find the most approximate name to a high degree from the one input. 
    If invalid name or no matching name found then return error. Route can accept the path 
    with or without the trailing slash.

    Parameters
    ==========
    :input_country_name: str (default="")
        one or more country names as they are commonly known in english, according
        to the ISO 3166-1.

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per country name/names.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates_ = {}
    alpha2_code = []
    names = []    

    #if no input parameters set then return error message
    if (input_country_name == ""):
        return jsonify(create_error_message("The name input parameter cannot be empty.", request.url)), 400 
    
    #parse likeness query string param, used as a % cutoff for likeness of subdivision names, raise error if invalid type or value input
    try:
        search_likeness_score = int(request.args.get('likeness', default="100").rstrip('/'))
    except ValueError:
        return jsonify(create_error_message("Likeness query string parameter must be an integer between 0 and 100.", request.url)), 400 

    #raise error if likeness score isn't between 0 and 100
    if not (0 <= search_likeness_score <= 100):
        return jsonify(create_error_message("Likeness query string parameter value must be an between 0 and 100.", request.url)), 400 
    
    #pull sortBy query string parameter, that allows sorting by country code or publication date, descending/ascending
    sort_by = request.args.get('sortBy', default="") or request.args.get('sortby', default="").lower().rstrip('/')

    #remove unicode space (%20) from input parameter
    input_country_name = input_country_name.replace('%20', ' ').title()
    
    #check if input country is in above list, if not add to sorted comma separated list    
    if (input_country_name.upper() in name_comma_exceptions):
        names = [input_country_name]
    else:
        names = sorted(input_country_name.split(','))
    
    #iterate over list of names, convert country names from names_converted dict, if applicable
    for name_ in range(0, len(names)):
        if (names[name_].title() in list(names_converted.keys())):
            names[name_] = names_converted[names[name_]]

    #remove all whitespace in any of the country names
    names = [name_.strip(' ') for name_ in names]

    #get list of available country names from iso3166 library, remove whitespace
    all_names_no_space = [name_.strip(' ') for name_ in list(iso3166.countries_by_name.keys())]
    
    #iterate over all input country names, get corresponding 2 letter alpha-2 code
    for name_ in names:

        #using thefuzz library, get all countries that match the input country name, 
        # by default an exact match is sought, but the % likeness the match has to be can be reduced using likeness parameter 
        name_matches = process.extract(name_.upper(), all_names_no_space, scorer=fuzz.ratio)

        #filter all matches above the likeness threshold
        valid_matches = [match for match in name_matches if match[1] >= search_likeness_score]

        #% of likeness that a country name has to be to an erroneous input name
        country_name_suggestion_threshold = 75  

        #if no exact match found, return error message with suggested similar country name
        if not valid_matches:
            if name_matches and name_matches[0][1] >= country_name_suggestion_threshold:
                suggestion = name_matches[0][0].title()
                error_message= f"No matching country name found for input: {name_}, did you mean {suggestion}?"
            else:
                error_message = f"No matching country name found for input: {name_}."
            return jsonify(create_error_message(error_message, request.url)), 400

        #iterate over valid matches and append to output object
        for match_name, score in valid_matches:
            alpha2 = iso3166.countries_by_name[match_name.upper()].alpha2
            if alpha2 not in iso3166_updates_:
                iso3166_updates_[alpha2] = get_all_updates()[alpha2]

        #use iso3166 package to find corresponding alpha-2 code from its name
        alpha2_code.append(iso3166.countries_by_name[name_matches[0][0].upper()].alpha2)
    
    #get country data from ISO 3166-2 object, using alpha-2 code
    for code in alpha2_code:
        iso3166_updates_[code] = get_all_updates()[code]

    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date, ascending or descending, don't sort if just one country object present
    if (sort_by == 'dateasc' or sort_by == 'datedesc') and len(iso3166_updates_) > 1:
        iso3166_updates_ = sort_by_date(iso3166_updates_, date_asc_desc=sort_by)

    return jsonify(iso3166_updates_), 200

@app.route('/api/year/<input_year>/country_name/<input_country_name>', methods=['GET'])
@app.route('/api/country_name/<input_country_name>/year/<input_year>', methods=['GET'])
@app.route('/year/<input_year>/country_name/<input_country_name>', methods=['GET'])
@app.route('/country_name/<input_country_name>/year/<input_year>', methods=['GET'])
@app.route('/api/year/<input_year>/country_name/', defaults={'input_country_name': ""}, methods=['GET'])
@app.route('/api/country_name/<input_country_name>/year/', defaults={'input_year': ""}, methods=['GET'])
def api_country_name_year(input_country_name: str="", input_year: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/country_name/year' path/endpoint. Return all ISO 3166 updates for the 
    inputted country name/names and the selected years, year range, greater than/less than a year 
    or not equal to a year. A closeness function is used to find the most approximate name to a 
    high degree from the one input. If invalid name or no matching name found then return error. 

    Parameters
    ==========
    :input_country_name: str (default="")
        one or more country names as they are commonly known in english, according
        to the ISO 3166-1.
    :input_year: str (default="")
        year, comma separated list of years, or year range to get updates from. Can 
        also accept greater than or less than symbol returning updates greater 
        than/less than specified year or updates not equal to year/list of years.

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per country name/names.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates_ = {}
    alpha2_code = []
    names = []    

    #if no input parameters set then return error message
    if (input_country_name == ""):
        return jsonify(create_error_message("The name input parameter cannot be empty.", request.url)), 400 
    
    #parse likeness query string param, used as a % cutoff for likeness of subdivision names, raise error if invalid type or value input
    try:
        search_likeness_score = int(request.args.get('likeness', default="100").rstrip('/'))
    except ValueError:
        return jsonify(create_error_message("Likeness query string parameter must be an integer between 0 and 100.", request.url)), 400 

    #raise error if likeness score isn't between 0 and 100
    if not (0 <= search_likeness_score <= 100):
        return jsonify(create_error_message("Likeness query string parameter value must be an between 0 and 100.", request.url)), 400 
    
    #pull sortBy query string parameter, that allows sorting by country code or publication date
    sort_by = request.args.get('sortBy', default="") or request.args.get('sortby', default="").lower().rstrip('/')

    #remove unicode space (%20) from input parameter
    input_country_name = input_country_name.replace('%20', ' ').title()
    
    #check if input country is in above list, if not add to sorted comma separated list    
    if (input_country_name.upper() in name_comma_exceptions):
        names = [input_country_name]
    else:
        names = sorted(input_country_name.split(','))
    
    #iterate over list of names, convert country names from names_converted dict, if applicable
    for name_ in range(0, len(names)):
        if (names[name_].title() in list(names_converted.keys())):
            names[name_] = names_converted[names[name_]]

    #remove all whitespace in any of the country names
    names = [name_.strip(' ') for name_ in names]

    #get list of available country names from iso3166 library, remove whitespace
    all_names_no_space = [name_.strip(' ') for name_ in list(iso3166.countries_by_name.keys())]
    
    #iterate over all input country names, get corresponding 2 letter alpha-2 code
    for name_ in names:

        #using thefuzz library, get all countries that match the input country name, 
        # by default an exact match is sought, but the % likeness the match has to be can be reduced using likeness parameter 
        name_matches = process.extract(name_.upper(), all_names_no_space, scorer=fuzz.ratio)

        #filter all matches above the likeness threshold
        valid_matches = [match for match in name_matches if match[1] >= search_likeness_score]

        #% of likeness that a country name has to be to an erroneous input name
        country_name_suggestion_threshold = 75  

        #if no exact match found, return error message with suggested similar country name
        if not valid_matches:
            if name_matches and name_matches[0][1] >= country_name_suggestion_threshold:
                suggestion = name_matches[0][0].title()
                error_message= f"No matching country name found for input: {name_}, did you mean {suggestion}?"
            else:
                error_message = f"No matching country name found for input: {name_}."
            return jsonify(create_error_message(error_message, request.url)), 400

        #iterate over valid matches and append to output object
        for match_name, score in valid_matches:
            alpha2 = iso3166.countries_by_name[match_name.upper()].alpha2
            if alpha2 not in iso3166_updates_:
                iso3166_updates_[alpha2] = get_all_updates()[alpha2]

        #use iso3166 package to find corresponding alpha-2 code from its name
        alpha2_code.append(iso3166.countries_by_name[name_matches[0][0].upper()].alpha2)
    
    #get country data from ISO 3166-2 object, using alpha-2 code
    for code in alpha2_code:
        iso3166_updates_[code] = get_all_updates()[code]

    #parse and validate input year parameter 
    year, year_range, year_greater_than, year_less_than, year_not_equal, year_error, year_error_message = validate_year(input_year)

    #return error if error found when parsing and validating the year input parameter
    if (year_error):
        return jsonify(create_error_message(year_error_message, request.url)), 400   
    
    #temporary updates object
    temp_iso3166_updates = {}

    #use temp object to get updates data either for specific country/alpha-2 code or for all
    #countries, dependant on input_alpha_codes and input_data vars above
    if (year != []):
        for code in alpha2_code:
            temp_iso3166_updates[code] = []
            for update in range(0, len(iso3166_updates_[code])):

                #convert year in Date Issued column to str of year, remove "corrected" date if applicable
                if ("corrected" in iso3166_updates_[code][update]["Date Issued"]):
                    temp_year = str(datetime.strptime(re.sub("[(].*[)]", "", iso3166_updates_[code][update]["Date Issued"]).replace(' ', "").
                                                      replace(".", '').replace('\n', ''), '%Y-%m-%d').year)
                else:
                    temp_year = str(datetime.strptime(iso3166_updates_[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d').year)

                #if year range true then get country updates within specified range inclusive
                if (year_range):
                    if (temp_year != "" and (temp_year >= year[0] and temp_year <= year[1])):
                        temp_iso3166_updates[code].append(iso3166_updates_[code][update])
                
                #if greater than true then get country updates greater than or equal to specified year
                elif (year_greater_than):
                    if (temp_year != "" and (temp_year >= year[0])):
                        temp_iso3166_updates[code].append(iso3166_updates_[code][update])    

                #if less than true then get country updates less than specified year 
                elif (year_less_than):
                    if (temp_year != "" and (temp_year < year[0])):
                        temp_iso3166_updates[code].append(iso3166_updates_[code][update]) 

                #get all country updates not equal to current year
                elif (year_not_equal):
                    if (temp_year != "" and temp_year not in year):
                        temp_iso3166_updates[code].append(iso3166_updates_[code][update])

                #get country updates equal to specified year
                else:
                    for year_ in year:
                        if (temp_year != "" and (temp_year == year_)):
                            temp_iso3166_updates[code].append(iso3166_updates_[code][update])

            #if current alpha-2 has no rows for selected year/year range etc, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = iso3166_updates_

    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date, ascending or descending, don't sort if just one country object present
    if (sort_by == 'dateasc' or sort_by == 'datedesc') and len(temp_iso3166_updates) > 1:
        iso3166_updates = sort_by_date(temp_iso3166_updates, date_asc_desc=sort_by)
    else:
        #set main updates dict to temp one
        iso3166_updates_ = temp_iso3166_updates

    return jsonify(iso3166_updates_), 200

@app.route('/api/search/', methods=['GET'])
@app.route('/api/search/<input_search_term>', methods=['GET'])
@app.route('/api/search/<input_search_term>/year', methods=['GET'])
@app.route('/api/search/<input_search_term>/date_range', methods=['GET'])
@app.route('/search/<input_search_term>', methods=['GET'])
@app.route('/search/<input_search_term>/year', methods=['GET'])
@app.route('/search/<input_search_term>/date_range', methods=['GET'])
def api_search(input_search_term: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/search' path/endpoint. Return all ISO 3166 updates for the 
    inputted search terms/keywords. A closeness function via thefuzz package is used 
    to find the most approximate update objects that contain the inputted search terms. 
    A likeness query string parameter allows for you to set the % of likeness that the 
    attributes in the updates (Change & Desc of Change) have to be to the input search 
    terms, by default a score of 100 (meaning an exact match) is implemented. 
    
    The search results are sorted by the highest matching score first. This matching
    score is returned by default to the output, but this can be disabled by setting
    the query string parameter excludeMatchScore to 1.

    If a date is inputted to the endpoint, the Date Issued attribute will be explicitly 
    searched as well. If invalid search term or no matching updates found then return error. 

    Parameters
    ==========
    :input_search_term: str (default-"")
        1 or more sought search terms.

    Returns
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input search term.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an invalid 
        parameter input.
    """
    #if no input parameters set then return error message
    if (input_search_term == ""):
        return jsonify(create_error_message("The search input parameter cannot be empty.", request.url)), 400 
    
    #pull sortBy query string parameter, that allows sorting by country code or publication date, ascending/descending
    sort_by = request.args.get('sortBy', default="") or request.args.get('sortby', default="").lower().rstrip('/')

    #split search terms into comma separated list, remove all whitespace & unicode characters
    search_terms = unquote(input_search_term)
    # search_terms = [term.strip().lower() for term in decoded_term.split(",")]
    
    #parse likeness query string param, used as a % cutoff for likeness of subdivision names, raise error if invalid type or value input
    try:
        search_likeness_score = int(request.args.get('likeness', default="100").rstrip('/'))
    except ValueError:
        return jsonify(create_error_message("Likeness query string parameter must be an integer between 0 and 100.", request.url)), 400 

    #raise error if likeness score isn't between 0 and 100
    if not (0 <= search_likeness_score <= 100):
        return jsonify(create_error_message("Likeness query string parameter value must be between 0 and 100.", request.url)), 400 

    #parse query string parameter that allows user to exclude the Matching % score from search results, by default it is included in results
    exclude_match_score = (request.args.get('excludeMatchScore') or request.args.get('excludematchscore') or "false").lower().rstrip('/') in ['true', '1', 'yes']

    #call search function in iso3166-updates package, passing in likeness score & excludeMatchScore parameters
    search_results = get_updates_instance().search(search_terms, likeness_score=search_likeness_score, exclude_match_score=exclude_match_score)

    #return message that no search results were found
    if not search_results:
        return jsonify({"Message": f"No matching updates found with the given search term(s): {search_terms}. Try using the query string parameter '?likeness' and reduce the likeness score to expand the search space, '?likeness=30' will return subdivision data that have a 30% match to the input name. The current likeness score is set to {search_likeness_score}."}), 200

    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date, ascending or descending, don't sort if just one country object present
    if (sort_by == 'dateasc' or sort_by == 'datedesc') and len(search_results) > 1:
        search_results = sort_by_date(search_results, date_asc_desc=sort_by)

    return jsonify(search_results), 200

@app.route('/api/date_range/<input_date_range>', methods=['GET'])
@app.route('/api/date_range', methods=['GET'])
@app.route('/date_range/<input_date_range>', methods=['GET'])
@app.route('/date_range/<input_date_range>/alpha', methods=['GET'])
@app.route('/date_range', methods=['GET'])
def api_date_range(input_date_range: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/date_range' path/endpoint. Return all ISO 3166 
    updates published within the specified input date range, inclusive.
    The two dates in the range should be in a comma separated list in the
    format YYYY-MM-DD, although other formats are supported. The endpoint 
    can also accept a single date, which will act as the start date to get 
    updates from, with the current date being the end date.

    Parameters
    ==========
    :input_date_range: str (default="")
        start and end date to get updates from. If a single date input it will 
        act as the start date, with the current date being the end date. 

    Returns
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates published within date range. 
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an invalid 
        parameter input.
    """
    #initialise vars
    iso3166_updates = {}

    #pull sortBy query string parameter, that allows sorting publication date, ascending/descending
    sort_by = request.args.get('sortBy', default="") or request.args.get('sortby', default="").lower().rstrip('/')

    #return error if input data empty
    if (input_date_range == ""):
        return jsonify(create_error_message("Input date cannot be empty, expecting at least one date in the format YYYY-MM-DD.", request.url)), 400 
    
    #split multiple dates into list, remove whitespace
    date_parts = input_date_range.split(",")
    date_parts = [d.strip() for d in date_parts] 

    #if only one date input, treat this as the starting date, setting the end date as today
    if len(date_parts) == 1:
        date_parts.append(datetime.today().strftime("%Y-%m-%d"))
    elif len(date_parts) != 2:
        return jsonify(create_error_message(f"Date input must contain either one or two dates: {date_parts}.", request.url)), 400 

    #extract start and end date and convert each
    start_date, end_date = date_parts[0], date_parts[1]
    start_date = convert_date_format(start_date)
    end_date = convert_date_format(end_date)

    #return error if start or end date can't be converted into valid format 
    if (start_date is None or end_date is None):
        return jsonify(create_error_message(f"Invalid date format, expected YYYY-MM-DD format: {input_date_range}.", request.url)), 400 

    #swap dates if start_date is later than end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    #iterate over all updates data, adding all data that's within desired date range
    for country_code, updates in get_all_updates().items():
        filtered_changes = []
        for update in updates:

            #parse the original publication date from attribute
            original_date_str = update["Date Issued"].split(" ")[0]  
            original_date = datetime.strptime(original_date_str, "%Y-%m-%d")

            #parse corrected date from publication date attribute, if applicable 
            cleaned_date_row = re.sub(r"\(.*?\)", "", update["Date Issued"])
            corrected_date = re.sub(r'\s+', ' ', cleaned_date_row.replace('.', '').strip())

            #convert corrected date to datetime object, if applicable 
            if corrected_date:
                corrected_date = datetime.strptime(corrected_date, "%Y-%m-%d")
            
            #track if current date has been added to object
            update_added = False

            #check if the original date falls within the input range
            if (start_date <= original_date <= end_date): 
                filtered_changes.append(update)
                update_added = True

            #check if the corrected date falls within the input range
            if (corrected_date):
                if (start_date <= corrected_date <= end_date):
                    if not (update_added):
                        filtered_changes.append(update)

        #add filtered changes to main date filtered object
        if filtered_changes:
            iso3166_updates[country_code] = filtered_changes

    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date, ascending or descending, don't sort if just one country object present
    if (sort_by == 'dateasc' or sort_by == 'datedesc') and len(iso3166_updates) > 1:
        iso3166_updates = sort_by_date(iso3166_updates, date_asc_desc=sort_by)

    return jsonify(iso3166_updates), 200

@app.route('/api/date_range/<input_date_range>/alpha/<input_alpha>', methods=['GET'])
@app.route('/api/alpha/<input_alpha>/date_range/<input_date_range>', methods=['GET'])
@app.route('/date_range/<input_date_range>/alpha/<input_alpha>', methods=['GET'])
@app.route('/alpha/<input_alpha>/date_range/<input_date_range>', methods=['GET'])
@app.route('/api/date_range/<input_date_range>/alpha/', defaults={'input_alpha': ""}, methods=['GET'])
@app.route('/api/alpha/<input_alpha>/date_range/', defaults={'input_date_range': ""}, methods=['GET'])
def api_date_range_alpha(input_alpha: str="", input_date_range: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/alpha' + '/api/date_range' path/endpoint. Return all ISO 3166 
    updates for the inputted ISO 3166-1 alpha-2, alpha-3 or numeric country code/codes 
    + a specified date/date range. The alpha-3 and numeric codes will be converted into 
    their corresponding alpha-2 code. If an invalid alpha code or date range input then 
    return error. 
    
    Parameters
    ==========
    :input_alpha: str (default="")
        1 or more ISO 3166-1 alpha-2, alpha-3 or numeric country codes.
    :input_date_range: str (default="")
        start and end date to get updates from. If a single date input it will 
        act as the start date, with the current date being the end date. 

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input alpha-2 code and date range.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates = {}

    #pull sortBy query string parameter, that allows sorting by publication date, ascending/descending
    sort_by = request.args.get('sortBy', default="") or request.args.get('sortby', default="").lower().rstrip('/')

    #return error if input data empty
    if (input_date_range == ""):
        return jsonify(create_error_message("Input date cannot be empty, expecting at least one date in the format YYYY-MM-DD.", request.url)), 400 

    #if no input alpha parameter then return error message
    if (input_alpha == ""):
        return jsonify(create_error_message("The alpha code input parameter cannot be empty." , request.url)), 400 

    #get the country updates data using the input alpha codes, return error if invalid codes input
    try:
        all_iso3166_updates_ = get_updates_instance()[input_alpha]
    except ValueError as ve:
        return jsonify(create_error_message(str(ve) , request.url)), 400 

    #split multiple dates into list, remove whitespace
    date_parts = input_date_range.split(",")
    date_parts = [d.strip() for d in date_parts] 

    #if only one date input, treat this as the starting date, setting the end date as today
    if len(date_parts) == 1:
        date_parts.append(datetime.today().strftime("%Y-%m-%d"))
    elif len(date_parts) != 2:
        return jsonify(create_error_message(f"Date input must contain either one or two dates: {date_parts}." , request.url)), 400 

    #extra start and end date and convert each
    start_date, end_date = date_parts[0], date_parts[1]
    start_date = convert_date_format(start_date)
    end_date = convert_date_format(end_date)

    #return error if start or end date can't be converted into valid format 
    if (start_date is None or end_date is None):
        return jsonify(create_error_message(f"Invalid date format, expected YYYY-MM-DD format: {input_date_range}." , request.url)), 400 

    #swap dates if start_date is later than end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    #iterate over all updates data, adding all data that's within desired date range
    for country_code, updates in all_iso3166_updates_.items():
        filtered_changes = []
        for update in updates:

            #parse the original publication date from attribute
            original_date_str = update["Date Issued"].split(" ")[0]  
            original_date = datetime.strptime(original_date_str, "%Y-%m-%d")

            #parse corrected date from publication date attribute, if applicable 
            cleaned_date_row = re.sub(r"\(.*?\)", "", update["Date Issued"])
            corrected_date = re.sub(r'\s+', ' ', cleaned_date_row.replace('.', '').strip())

            #convert corrected date to datetime object, if applicable 
            if corrected_date:
                corrected_date = datetime.strptime(corrected_date, "%Y-%m-%d")
            
            #track if current date has been added to object
            update_added = False

            #check if the original date falls within the input range
            if (start_date <= original_date <= end_date): 
                filtered_changes.append(update)
                update_added = True

            #check if the corrected date falls within the input range
            if (corrected_date):
                if (start_date <= corrected_date <= end_date):
                    if not (update_added):
                        filtered_changes.append(update)

        #add filtered changes to main date filtered object
        if filtered_changes:
            iso3166_updates[country_code] = filtered_changes

    #if sortBy query string parameter set, call sort_by_date function to sort all updates data via the publication date, ascending or descending, don't sort if just one country object present
    if (sort_by == 'dateasc' or sort_by == 'datedesc') and len(iso3166_updates) > 1:
        iso3166_updates = sort_by_date(iso3166_updates, date_asc_desc=sort_by)

    return jsonify(iso3166_updates), 200

'''
/api/country_name and /api/country_name/year path/endpoints can accept multiple country names, 
separated by a comma, but several countries contain a comma already in their official name in 
the iso3166 package. Separate multiple country names by a comma, cast to a sorted list, unless 
any of the names are in the below list...
'''
name_comma_exceptions = ["BOLIVIA, PLURINATIONAL STATE OF",
                "BONAIRE, SINT EUSTATIUS AND SABA",
                "CONGO, DEMOCRATIC REPUBLIC OF THE",
                "IRAN, ISLAMIC REPUBLIC OF",
                "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF",
                "KOREA, REPUBLIC OF",
                "MICRONESIA, FEDERATED STATES OF",
                "MOLDOVA, REPUBLIC OF",
                "PALESTINE, STATE OF",
                "SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA",
                "TAIWAN, PROVINCE OF CHINA",
                "TANZANIA, UNITED REPUBLIC OF",
                "VIRGIN ISLANDS, BRITISH",
                "VIRGIN ISLANDS, U.S.",
                "VENEZUELA, BOLIVARIAN REPUBLIC OF"]

#list of country name exceptions that are converted into their more official name
names_converted = {"UAE": "United Arab Emirates", "Brunei": "Brunei Darussalam", "Bolivia": "Bolivia, Plurinational State of", 
                    "Bosnia": "Bosnia and Herzegovina", "Bonaire": "Bonaire, Sint Eustatius and Saba", "DR Congo": 
                    "Congo, the Democratic Republic of the", "Ivory Coast": "Côte d'Ivoire", "Cape Verde": "Cabo Verde", 
                    "Cocos Islands": "Cocos (Keeling) Islands", "Cura%C3%A7Ao": "Curaçao", "Falkland Islands": "Falkland Islands (Malvinas)", 
                    "Micronesia": "Micronesia, Federated States of", "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
                    "South Georgia": "South Georgia and the South Sandwich Islands", "Iran": "Iran, Islamic Republic of",
                    "North Korea": "Korea, Democratic People's Republic of", "South Korea": "Korea, Republic of", 
                    "Laos": "Lao People's Democratic Republic", "Moldova": "Moldova, Republic of", "Saint Martin": "Saint Martin (French part)",
                    "Macau": "Macao", "Pitcairn Islands": "Pitcairn", "R%C3%A9Union": "Réunion", "South Georgia": "South Georgia and the South Sandwich Islands",
                    "Heard Island": "Heard Island and McDonald Islands", "Palestine": "Palestine, State of", 
                    "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha", "St Helena": "Saint Helena, Ascension and Tristan da Cunha",              
                    "Saint Kitts": "Saint Kitts and Nevis", "St Kitts": "Saint Kitts and Nevis", "St Vincent": "Saint Vincent and the Grenadines", 
                    "St Lucia": "Saint Lucia", "Saint Vincent": "Saint Vincent and the Grenadines", "Russia": "Russian Federation", 
                    "Sao Tome and Principe":" São Tomé and Príncipe", "Sint Maarten": "Sint Maarten (Dutch part)", "Syria": "Syrian Arab Republic", 
                    "Svalbard": "Svalbard and Jan Mayen", "French Southern and Antarctic Lands": "French Southern Territories", "Turkey": "Türkiye", 
                    "Taiwan": "Taiwan, Province of China", "Tanzania": "Tanzania, United Republic of", "T%C3%Bcrkiye": "Türkiye", "USA": "United States of America", 
                    "United States": "United States of America", "Vatican City": "Holy See", "Vatican": "Holy See", "Venezuela": 
                    "Venezuela, Bolivarian Republic of", "British Virgin Islands": "Virgin Islands, (British)", "US Virgin Islands": "Virgin Islands, (U.S.)"} 

def convert_to_alpha2(alpha_code: str) -> str:
    """ 
    Auxiliary function that converts an ISO 3166 country's 3 letter alpha-3 
    or numeric code into its 2 letter alpha-2 counterpart. The function also
    validates the input alpha-2 or converted alpha-2 code, returning None
    if invalid alpha code input, the calling function should then return
    an error message.

    Parameters 
    ==========
    :alpha_code: str
        3 letter ISO 3166-1 alpha-3 or numeric country code.
    
    Returns
    =======
    :alpha_code: str/None
        converted ISO 3166-1 alpha-2 code. None returned if input cannot
        be converted or is invalid.
    
    Raises
    ======
    TypeError:
        Invalid data type input for alpha_code parameter
    """
    #raise error if invalid type input
    if not (isinstance(alpha_code, str)):
        raise TypeError(f"Expected input alpha code to be a string, got {type(alpha_code)}.")

    #uppercase alpha code, initial_alpha_code var maintains the original alpha code pre-uppercasing
    alpha_code = alpha_code.upper()
    
    #use iso3166 package to find corresponding alpha-2 code from its numeric code, return error if numeric code not found
    if (alpha_code.isdigit()):
        if not (alpha_code in list(iso3166.countries_by_numeric.keys())):
            return None
        return iso3166.countries_by_numeric[alpha_code].alpha2

    #return input alpha code if its valid, return error if alpha-2 code not found
    if len(alpha_code) == 2:
        if not (alpha_code in list(iso3166.countries_by_alpha2.keys())):
            return None
        return alpha_code

    #use iso3166 package to find corresponding alpha-2 code from its alpha-3 code, return error if code not found
    if len(alpha_code) == 3:
        if not (alpha_code in list(iso3166.countries_by_alpha3.keys())):
            return None
        return iso3166.countries_by_alpha3[alpha_code].alpha2

def validate_year(year: str) -> tuple[list,bool,bool,bool,bool,bool,str]:
    """
    Validate and parse the year parameter into a list of years. Also return if
    a year range, greater than/less than or not equal to year are input. Raise 
    error if invalid year format.

    Parameters
    ========= 
    :year: str
        single string or comma separated list of 1 or more years to get the specific 
        ISO 3166 updates from, per country. You can also pass in a year range 
        (e.g 2010-2015), a year to get all updates less than or greater than that 
        specified year (e.g >2007, <2021) or not equal to a year (e.g <>2001).

    Returns
    ======= 
    :year: str
        parsed and validated list of years.
    :year_range: bool
        if input year parameter contains a range of years.
    :year_greater_than: bool
        if input year parameter contains ">", thus getting all updates >= year.
    :year_less_than: bool
        if input year parameter contains "<", thus getting all updates < year.
    :year_not_equal: bool 
        if input year parameter contains "<>", thus excluding any rows with input 
        year/years.
    :year_error: bool
        if True then there was an error processing the inputted year/years.
    :year_error_message: str
        if there was an error during processing and validating the year parameters,
        this var returns the error message. 
    """
    #year bools
    year_range = False
    year_greater_than = False
    year_less_than = False
    year_not_equal = False
    year_error = False
    year_error_message = ""
    _ = False #this is a placeholder bool for the error return messages to represent the vars we dont need to return

    #parse alpha code parameter, split into list, remove any whitespace and sort
    year = sorted(year.replace(' ', '').replace('%20', '').split(','))
    
    #convert > or < symbol from unicode to str ("%3E" and "%3C", respectively)
    year = [urllib.parse.unquote(s) for s in year]

    #validate each year's format using regex
    for year_ in year:
        #remove symbols like '<' or '>'
        sanitized_year = re.sub(r"[<>]", "", year_)

        #if it's a range, split and validate each part
        years = sanitized_year.split('-')
        for y in years:
            #skip empty strings
            if not y:
                continue

            #validate year format
            if not re.match(r"^1[0-9]{3}$|^2[0-9]{3}$", y):
                year_error, year_error_message = 1, f"Invalid year input, must be a valid year >= 1996, got {year_}."
                return _, _, _, _, _, year_error, year_error_message

    #a '-' separating 2 years implies a year range
    #a ',' separating 2 years implies a list of years
    #a '>' before year means greater than or equal to specified year
    #a '<' before year means less than specified year
    #a '<>' before the year means don't include year/list of years 
    if ("<>" in year[0]):
        year_not_equal = True
        year = [x.replace("<>", "") for x in year]
    elif ('-' in year[0]):
        year_range = True
        year = year[0].split('-')
        #if year range years are wrong way around then swap them
        if (year[0] > year[1]):
            year[0], year[1] = year[1], year[0]
        #raise error if more than 2 years in list
        if (len(year) > 2):
            year_error, year_error_message = 1, f"If using a range of years, there must only be 2 years separated by a '-': {year}."
            return _, _, _, _, _, year_error, year_error_message
    #parse array for using greater than symbol
    elif ('>' in year[0]):
        year = list(year[0].rpartition(">")[1:])
        year_greater_than = True
        year.remove('>')
        #raise error if more than 2 years in list
        if (len(year) > 2):
            year_error, year_error_message = 1, f"If greater than year input, there must only be 1 year prepended by a '>': {year}."
            return _, _, _, _, _, year_error, year_error_message
    #parse array for using less than symbol
    elif ('<' in year[0]):
        year = list(year[0].rpartition("<")[1:])
        year_less_than = True
        year.remove('<')
        #raise error if more than 2 years in list
        if (len(year) > 2):
            year_error, year_error_message = 1, f"If less than year input, there must only be 1 year prepended by a '<': {year}."
            return _, _, _, _, _, year_error, year_error_message
    #split years into comma separated list of multiple years if multiple years are input
    elif (',' in year[0]):
        year = year[0].split(',')

    #raise error if more than one year related symbols are in year str
    for year_ in year:
        if any(symbol in year_ for symbol in ["-", "<", ">"]):
            year_error, year_error_message = 1, f"Only one type of symbol should be input for year e.g '-', '<' or '>': {year}."
            return _, _, _, _, _, year_error, year_error_message
    
    return year, year_range, year_greater_than, year_less_than, year_not_equal, year_error, year_error_message

def sort_by_date(input_iso3166_updates: dict, date_asc_desc="datedesc") -> dict:
    """
    Sort the inputted updates object by publication date. The date_asc_desc 
    parameter determines if the output is sorted latest or earliest first. 
    The 2 accepted values are dateDesc and dateAsc, meaning to sort the date
    descending or ascending, respectively. The "Country Code" attribute is 
    added to each update object.

    Parameters
    ==========
    :input_iso3166_updates: dict    
        object of unsorted ISO 3166 updates. 
    :date_asc_desc: str
        parameter to determine whether to sort ascending or descending.

    Returns
    =======
    :all_updates: dict
        sorted object of ISO 3166 updates by publication date. 
    """
    #iterate over all updates, create updates object with Country Code added to identify the update's country, flatten into a list and append to array 
    flattened_iso3166_updates = []
    for country_code, updates in input_iso3166_updates.items():
        for update in updates:
            flattened_iso3166_updates.append({**update, "Country Code": country_code})

    #sort flattened array by publication date, ascending or descending according to parameter, if invalid value input, descending by default
    if (date_asc_desc == "dateasc"):
        flattened_iso3166_updates.sort(key=lambda update: datetime.strptime(update["Date Issued"].split(" (")[0].strip(), "%Y-%m-%d"), reverse=False)
    else:
        flattened_iso3166_updates.sort(key=lambda update: datetime.strptime(update["Date Issued"].split(" (")[0].strip(), "%Y-%m-%d"), reverse=True)

    #set flattened data to output object
    all_updates = flattened_iso3166_updates

    return all_updates
    
def convert_date_format(date: str) -> str|None:
    """
    Convert inputted date string into the YYYY-MM-DD format. There
    are a series of accepted formats for the input date:
    '%Y-%m-%d', '%d %B %Y', '%Y-%d-%m', '%d/%m/%Y', '%d-%m-%Y', '%y-%m-%d'.

    If a matching format is not found then None will be returned.

    Parameters
    ==========
    :date: str
        input date string.

    Returns
    =======
    :parsed_date: str|None:
        converted date in the YYYY-MM-DD format or None.
    """
    #raise error if input date parameter isn't a string
    if not isinstance(date, str):
        return None

    #strip whitespace and "." from input date
    date = date.strip().rstrip(".") 

    #list of accepted input date formats
    date_formats = ['%Y-%m-%d', '%d %B %Y', '%Y-%d-%m', '%d/%m/%Y', '%d-%m-%Y', '%y-%m-%d']

    #iterate over accepted date formats
    for fmt in date_formats:
        try:
            #parse input date
            parsed_date = datetime.strptime(date, fmt)

            #handle potential ambiguity with the '%Y-%d-%m' format, in the case of the d & m values inputted incorrectly
            if fmt == '%Y-%d-%m':
                day = int(date.split('-')[1])  
                #if day is greater than 12, swap day and month, try and parse date
                if day > 12:  
                    date = parsed_date.strftime('%Y-%m-%d')
                    break  
                else:
                    #return None if date cannot be converted into desired format
                    return None

            #append validated and parsed date to the list
            return parsed_date
            
        #skip to next date format iteration if the current one has failed
        except ValueError:
            continue  

    #raise error if date format not valid
    else:  
        #return None if date cannot be converted into desired format
        return None

    #try to parse the date using the expected "%Y-%m-%d" format
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        return date  
    #if parsing failed, try the next format 
    except ValueError:
        pass  

    #try to parse the date using the "%d/%m/%Y" format
    try:
        parsed_date = datetime.strptime(date, "%d/%m/%Y")
        return parsed_date.strftime("%Y-%m-%d")  
    #if parsing failed, skip to valueError below
    except ValueError:
        pass 

    #return None if date format not valid
    return None

def create_error_message(message: str, path: str, status: int = 400) -> dict:
    """ Helper function that returns error message when one occurs in Flask app. """
    return {"message": message, "path": path, "status": status}

@app.route('/clear-cache')
@app.route('/api/clear-cache')
def clear_cache():
    """ Clear cache of Updates class instance and all cached subdivision data. Mainly used for dev. """
    get_updates_instance.cache_clear()
    get_all_updates.cache_clear()
    return 'Cache cleared'

@app.route('/version')
@app.route('/api/version')
def get_version():
    """ Get the current version of the iso3166-updates being used by the API. Mainly used for dev. """
    return get_updates_instance().__version__

@app.errorhandler(404)
def not_found(e: int) -> tuple[dict, int]:
    """
    Return html template for 404.html when page/path not found in Flask app.

    Parameters
    ==========
    :e: int
        error code.

    Returns
    =======
    :flask.render_template: html
      Flask html template for 404.html page.
    :status_code: int
        response status code. 404 code implies page not found.
    """
    return render_template("404.html", path=request.url), 404

if __name__ == '__main__':
    #run flask app
    app.run(debug=True)