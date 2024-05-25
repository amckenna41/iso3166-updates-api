from flask import Flask, request, render_template, jsonify
import iso3166
from iso3166_updates import *
import re
from thefuzz import fuzz, process
from datetime import datetime
from dateutil import relativedelta

########################################################## Endpoints ##########################################################
'''
/api - main homepage for API, displaying purpose, examples and documentation
/api/all - return all updates data for all countries
/api/alpha/<input_alpha> - return all updates data for input country using its ISO 3166-1 alpha-2, alpha-3 or numeric codes  
/api/year/<input_year> - return all updates data for input year, list of years, year range or greater/less than input year
/api/name/<input_name> - return all updates for input country name
/api/alpha/<input_alpha>/year/<input_year> - return all updates data for input ISO 3166-1 alpha-2, alpha-3 or numeric country 
      code + year, list of years, year range or greater/less than input year
/api/year/<input_year>/name/<input_name> - return all updates data for input country name + year, list of years, year range 
      or greater/less than input year
/api/months/<input_months> -  return all updates data from the previous number of months
/api/months/<input_months>/alpha/<input_alpha> - return all updates data from the previous number of months for input country
      using its ISO 3166-1 alpha-2, alpha-3 or numeric codes
/api/months/<input_months>/name/<input_name> - return all updates data from the previous number of months for input country
      name
'''
###############################################################################################################################

#initialise Flask app
app = Flask(__name__)

#register routes/endpoints with or without trailing slash
app.url_map.strict_slashes = False

#json object storing the error message, route and status code 
error_message = {}
error_message["status"] = 400

#create instance of ISO3166_Updates class and get all ISO 3166 updates data
iso_updates = ISO3166_Updates()
all_iso3166_updates = iso_updates.all

@app.route('/api')
@app.route('/')
def home():
    """
    Default route for https://iso3166-updates.com. Main homepage for API displaying the 
    purpose of API and its documentation. Route can accept path with or without 
    trailing slash.

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
    available countries. Route can accept path with or without trailing slash.

    Parameters
    ==========
    None

    Returns
    =======
    :jsonify(all_iso3166_updates): json
        jsonified ISO 3166 updates data.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input. 
    """  
    return jsonify(all_iso3166_updates), 200

@app.route('/api/alpha', methods=['GET'])
@app.route('/api/alpha/<input_alpha>', methods=['GET'])
@app.route('/api/alpha/<input_alpha>/year', methods=['GET'])
@app.route('/api/alpha/<input_alpha>/months', methods=['GET'])
@app.route('/alpha/<input_alpha>', methods=['GET'])
@app.route('/alpha/<input_alpha>/year', methods=['GET'])
@app.route('/alpha/<input_alpha>/months', methods=['GET'])
@app.route('/alpha', methods=['GET'])
def api_alpha(input_alpha: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/alpha' path/endpoint. Return all ISO 3166 updates for the inputted 
    ISO 3166-1 alpha-2, alpha-3 or numeric country code/codes. The alpha-3 and numeric codes will 
    be converted into their corresponding alpha-2 code. If an invalid alpha code input then return 
    error. Additionally, the endpoint can be used in conjunction with the year and months endpoints.
    Route can accept path with or without trailing slash.

    Parameters
    ==========
    :input_alpha: string
        1 or more alpha-2, alpha-3 or numeric country codes according to the ISO 3166-1 standard. 
        The alpha-3 and numeric codes will be converted into their alpha-2 counterparts.

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input alpha code.
    :blob_not_found_error_message: dict 
        error message if issue finding updates object json.  
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    alpha2_code = []

    #set path url for error message object
    error_message['path'] = request.base_url
    
    #if no input alpha parameter then return error message
    if (input_alpha == ""):
        error_message["message"] = "The alpha input parameter cannot be empty." 
        return jsonify(error_message), 400    

    #parse alpha code parameter, sort, uppercase and remove any whitespace
    alpha2_code = sorted(input_alpha.upper().replace(' ', '').replace('%20', '').split(','))
    
    #iterate over each input alpha codes, validating and converting each to its alpha-2 counterpart, if applicable 
    for code in range(0, len(alpha2_code)):
        #api can accept 3 letter alpha-3 or numeric code for country, this has to be converted into its alpha-2 counterpart
        if (len(alpha2_code[code]) == 3):
            temp_code = convert_to_alpha2(alpha2_code[code])
            #return error message if invalid numeric code input
            if (temp_code is None and alpha2_code[code].isdigit()):
                error_message["message"] = f"Invalid ISO 3166-1 numeric country code input, cannot convert into corresponding alpha-2 code: {''.join(alpha2_code[code])}."
                return jsonify(error_message), 400
            #return error message if invalid alpha-3 code input
            if (temp_code is None):
                error_message["message"] = f"Invalid ISO 3166-1 alpha-3 country code input, cannot convert into corresponding alpha-2 code: {''.join(alpha2_code[code])}."
                return jsonify(error_message), 400
            alpha2_code[code] = temp_code
        #use regex to validate format of alpha-2 codes, raise error if invalid code input
        if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[code]))) or (alpha2_code[code] not in list(iso3166.countries_by_alpha2.keys()) or (alpha2_code[code] == "XK")):
            error_message["message"] = f"Invalid ISO 3166-1 alpha country code input, no corresponding alpha-2 code found: {''.join(alpha2_code[code])}."
            return jsonify(error_message), 400

    #get updates from iso3166_updates instance object per country using alpha-2 code
    for code in alpha2_code:
        iso3166_updates[code] = all_iso3166_updates[code]

    return jsonify(iso3166_updates), 200

@app.route('/api/year', methods=['GET'])
@app.route('/api/year/<input_year>', methods=['GET'])
@app.route('/api/year/<input_year>/alpha', methods=['GET'])
@app.route('/year/<input_year>', methods=['GET'])
@app.route('/year', methods=['GET'])
@app.route('/year/<input_year>/alpha', methods=['GET'])
@app.route('/year/<input_year>/name', methods=['GET'])
def api_year(input_year: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/year' path/endpoint. Return all ISO 3166 updates for the inputted 
    year, list of years, year range or greater than or less than input year. If invalid year 
    then return error. Route can accept the path with or without the trailing slash.

    Parameters
    ==========
    :input_year: string
        year, comma separated list of years, or year range to get updates from. Can also accept 
        greater than or less than symbol, returning updates greater than/less than specified year.

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
    year_range = False
    greater_than = False
    less_than = False
    year = []

    #set path url for error message object
    error_message['path'] = request.base_url
    
    #if no input year parameter then return error message
    if (input_year == ""):
        error_message["message"] = "The year input parameter cannot be empty." 
        return jsonify(error_message), 400    
    
    #parse alpha code parameter, split into list, remove any whitespace and sort
    year = sorted(input_year.replace(' ', '').replace('%20', '').split(','))

    #iterate over all years, convert > or < symbol from unicode to string ("%3E" and "%3C", respectively)
    for y in range(0, len(year)):
        if ("%3E" in year[y]):
            year[y] = ">" + year[y][3:]
        elif ("%3C" in year[y]):
            year[y] = "<" + year[y][3:]

    #validate format of year input parameter:
    #a '-' separating 2 years implies a year range of sought country updates
    #a ',' separating 2 years implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    if ('-' in year[0]): 
        year_range = True
        year = year[0].split('-')
        #if years in year range input are wrong way around then swap them
        if (year[0] > year[1]):
            year[0], year[1] = year[1], year[0]
        #only 2 years should be included in input parameter when using a year range
        if (len(year) > 2):
            year = []
            year_range = False
    elif (',' in year[0]):
        #split years into comma separated list of multiple years if multiple years are input
        year = year[0].split(',')
    #parse array if using greater than symbol
    elif ('>' in year[0]):
        year = year[0].split('>')
        greater_than = True
        year.remove('')
        #after removing >, only 1 year should be left in year parameter
        if (len(year) > 1):
            year = []
            greater_than = False
    #parse array if using less than symbol
    elif ('<' in year[0]):
        year = year[0].split('<')
        less_than = True
        year.remove('')
        #after removing <, only 1 year should be left in year parameter
        if (len(year) > 1):
            year = []
            less_than = False

    #iterate over all years, validate their format using regex, raise error if invalid year found    
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>'):
            continue
        #validate each year format using regex, raise error if invalid year input
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            error_message["message"] = f"Invalid year input {''.join(year)}, year should be >1999 and <={datetime.now().year}." 
            error_message['path'] = request.base_url
            return jsonify(error_message), 400
    
    #temporary updates object
    temp_iso3166_updates = {}
            
    #if no valid alpha-2 codes input, use all alpha-2 codes from iso3166 and all updates data (all_iso3166_updates)
    input_alpha_codes  = list(iso3166.countries_by_alpha2.keys())
    input_data = all_iso3166_updates

    #remove XK (Kosovo) from list, if applicable
    if ("XK" in input_alpha_codes):
        input_alpha_codes.remove("XK")

    #iterate over alpha codes and data object, remove any rows for country that don't match input year parameter
    for code in input_alpha_codes:
        temp_iso3166_updates[code] = []
        for update in range(0, len(input_data[code])):

            #convert year in Date Issued column to string of year, remove "corrected" date if applicable
            if ("corrected" in input_data[code][update]["Date Issued"]):
                temp_year = str(datetime.strptime(re.sub("[(].*[)]", "", input_data[code][update]["Date Issued"]).replace(' ', "").
                                                    replace(".", '').replace('\n', ''), '%Y-%m-%d').year)
            else:
                temp_year = str(datetime.strptime(input_data[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d').year)
        
            #if year range true then get country updates within specified range inclusive
            if (year_range):
                if (temp_year != "" and (temp_year >= year[0] and temp_year <= year[1])):
                    temp_iso3166_updates[code].append(input_data[code][update])
            
            #if greater than true then get country updates greater than specified year, inclusive
            elif (greater_than):
                if (temp_year != "" and (temp_year >= year[0])):
                    temp_iso3166_updates[code].append(input_data[code][update])    

            #if less than true then get country updates less than specified year 
            elif (less_than):
                if (temp_year != "" and (temp_year < year[0])):
                    temp_iso3166_updates[code].append(input_data[code][update]) 

            #if greater than & less than not true then get country updates equal to specified year
            elif not (greater_than and less_than):
                for year_ in year:
                    if (temp_year != "" and (temp_year == year_)):
                        temp_iso3166_updates[code].append(input_data[code][update])
        
        #if current alpha-2 code has no rows for selected year/year range, remove from temp object
        if (temp_iso3166_updates[code] == []):
            temp_iso3166_updates.pop(code, None)
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/api/year/<input_year>/alpha/<input_alpha>', methods=['GET'])
@app.route('/api/alpha/<input_alpha>/year/<input_year>', methods=['GET'])
@app.route('/year/<input_year>/alpha/<input_alpha>', methods=['GET'])
def api_alpha_year(input_alpha: str="", input_year: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/alpha' + '/api/year' path/endpoint. Return all ISO 3166 
    updates for the inputted ISO 3166-1 alpha-2, alpha-3 or numeric country code/codes 
    + year/years/year range or greater than or less than input year. The alpha-3 and 
    numeric codes will be converted into their corresponding alpha-2 code. If invalid 
    alpha code or year/years input then return error. Route can accept the path with 
    or without the trailing slash.
    
    Parameters
    ==========
    :input_alpha: string
        1 or more ISO 3166-1 alpha-2, alpha-3 or numeric country codes.
    :input_year: string
        year, comma separated list of years, or year range to get updates from. Can 
        also accept greater than or less than symbol returning updates greater 
        than/less than specified year.

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
    year = []
    year_range = False
    greater_than = False
    less_than = False

    #set path url for error message object
    error_message['path'] = request.base_url

    #parse alpha code parameter, split, uppercase, remove any whitespace and sort
    if (input_alpha != ""):
        alpha2_code = sorted(input_alpha.upper().replace(' ', '').replace('%20', '').split(','))

    #parse year parameter, split, remove any whitespace and sort
    if (input_year != ""):
        year = sorted(input_year.replace(' ', '').replace('%20', '').split(','))

    #iterate over all years, convert > or < symbol from unicode to string ("%3E" and "%3C", respectively)
    for y in range(0, len(year)):
        if ("%3E" in year[y]):
            year[y] = ">" + year[y][3:]
        elif ("%3C" in year[y]):
            year[y] = "<" + year[y][3:]

    #iterate over each input alpha code, validating and converting into its corresponding alpha-2, if applicable
    if (alpha2_code != []):
        for code in range(0, len(alpha2_code)):
            #api can accept 3 letter alpha-3 or numeric code for country, this has to be converted into its alpha-2 counterpart
            if (len(alpha2_code[code]) == 3):
                temp_code = convert_to_alpha2(alpha2_code[code])
                #return error message if invalid numeric code input
                if (temp_code is None and alpha2_code[code].isdigit()):
                    error_message["message"] = f"Invalid ISO 3166-1 numeric country code input, cannot convert into corresponding alpha-2 code: {''.join(alpha2_code[code])}."
                    return jsonify(error_message), 400
                #return error message if invalid alpha-3 code input
                if (temp_code is None):
                    error_message["message"] = f"Invalid ISO 3166-1 alpha-3 country code input, cannot convert into corresponding alpha-2 code: {''.join(alpha2_code[code])}."
                    return jsonify(error_message), 400
                alpha2_code[code] = temp_code
            #use regex to validate format of alpha-2 codes, raise error if invalid code input
            if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[code]))) or (alpha2_code[code] not in list(iso3166.countries_by_alpha2.keys()) or (alpha2_code[code] == "XK")):
                error_message["message"] = f"Invalid ISO 3166-1 alpha country code input, no corresponding alpha-2 code found: {''.join(alpha2_code[code])}."
                return jsonify(error_message), 400

    #validate format of year input parameter:
    #a '-' separating 2 years implies a year range of sought country updates
    #a ',' separating 2 years implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    if ('-' in year[0]): 
        year_range = True
        year = year[0].split('-')
        #if years in year range input are wrong way around then swap them
        if (year[0] > year[1]):
            year[0], year[1] = year[1], year[0]
        #only 2 years should be included in input parameter when using a year range
        if (len(year) > 2):
            year = []
            year_range = False
    elif (',' in year[0]):
        #split years into comma separated list of multiple years if multiple years are input
        year = year[0].split(',')
    #parse array if using greater than symbol
    elif ('>' in year[0]):
        year = year[0].split('>')
        greater_than = True
        year.remove('')
        #after removing >, only 1 year should be left in year parameter
        if (len(year) > 1):
            year = []
            greater_than = False
    #parse array if using less than symbol
    elif ('<' in year[0]):
        year = year[0].split('<')
        less_than = True
        year.remove('')
        #after removing <, only 1 year should be left in year parameter
        if (len(year) > 1):
            year = []
            less_than = False

    #iterate over all years, validate their format using regex, raise error if invalid year found    
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>'):
            continue
        #validate each year format using regex, raise error if invalid year input
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            error_message["message"] = f"Invalid year input {''.join(year)}, year should be >1999 and <={datetime.now().year}." 
            error_message['path'] = request.base_url
            return jsonify(error_message), 400
        
    #get updates from iso3166_updates object per country using alpha-2 code
    for code in alpha2_code:
        iso3166_updates[code] = all_iso3166_updates[code]

    #temporary updates object
    temp_iso3166_updates = {}

    #if no valid alpha-2 codes input, use all alpha-2 codes from iso3166 and all updates data
    if ((year != [] and alpha2_code == []) or ((year == [] or year != []) and alpha2_code == [])):
        input_alpha_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = all_iso3166_updates
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

                #convert year in Date Issued column to string of year, remove "corrected" date if applicable
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
                elif (greater_than):
                    if (temp_year != "" and (temp_year >= year[0])):
                        temp_iso3166_updates[code].append(input_data[code][update])    

                #if less than true then get country updates less than specified year 
                elif (less_than):
                    if (temp_year != "" and (temp_year < year[0])):
                        temp_iso3166_updates[code].append(input_data[code][update]) 

                #if greater than & less than not true then get country updates equal to specified year
                elif not (greater_than and less_than):
                    for year_ in year:
                        if (temp_year != "" and (temp_year == year_)):
                            temp_iso3166_updates[code].append(input_data[code][update])
            
            #if current alpha-2 has no rows for selected year/year range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = input_data
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/api/name/<input_name>', methods=['GET'])
@app.route('/api/name/<input_name>/year', methods=['GET'])
@app.route('/api/name/<input_name>/months', methods=['GET'])
@app.route('/name/<input_name>', methods=['GET'])
@app.route('/name/<input_name>/year', methods=['GET'])
@app.route('/name/<input_name>/months', methods=['GET'])
def api_name(input_name: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/name' path/endpoint. Return all ISO 3166 updates for the 
    inputted country name/names. A closeness function is used to find the most 
    approximate name to a high degree from the one input. If invalid name or no 
    matching name found then return error. Route can accept the path with or 
    without the trailing slash.

    Parameters
    ==========
    :input_name: string
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

    #set error path for function error messages
    error_message['path'] = request.base_url

    #if no input parameters set then return error message
    if (input_name == ""):
        error_message["message"] = "The name input parameter cannot be empty."
        return jsonify(error_message), 400

    #remove unicode space (%20) from input parameter
    input_name = input_name.replace('%20', ' ').title()
    
    #check if input country is in above list, if not add to sorted comma separated list    
    if (input_name.upper() in name_comma_exceptions):
        names = [input_name]
    else:
        names = sorted(input_name.split(','))
    
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

        #using thefuzz library, get all countries that match the input country name
        name_matches = process.extract(name_.upper(), all_names_no_space, scorer=fuzz.ratio)
        
        #return error if no matching country name found
        if (name_matches == []):           
            #return error if country name not found
            error_message["message"] = "No matching country name found for input: {}.".format(name_)
            return jsonify(error_message), 400
        elif (name_matches[0][1] <70):
            if (name_matches[0][1] >60):
                #return error if country name not found
                error_message["message"] = "No matching country name found for input: {}, did you mean {}?".format(name_, name_matches[0][0].title())
            else:
                error_message["message"] = "No matching country name found for input: {}.".format(name_)
            return jsonify(error_message), 400

        #use iso3166 package to find corresponding alpha-2 code from its name
        alpha2_code.append(iso3166.countries_by_name[name_matches[0][0].upper()].alpha2)
    
    #get country data from ISO3166-2 object, using alpha-2 code
    for code in alpha2_code:
        iso3166_updates_[code] = all_iso3166_updates[code]

    return jsonify(iso3166_updates_), 200

@app.route('/api/year/<input_year>/name/<input_name>', methods=['GET'])
@app.route('/api/name/<input_name>/year/<input_year>', methods=['GET'])
@app.route('/year/<input_year>/name/<input_name>', methods=['GET'])
@app.route('/name/<input_name>/year/<input_year>', methods=['GET'])
def api_name_year(input_name: str="", input_year: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/name' + '/api/year' path/endpoint. Return all ISO 3166 updates 
    for the inputted country name/names + year, list of years, year range or greater than 
    or less than input year. A closeness function is used to find the most approximate 
    name to a high degree from the one input. If invalid name or no matching name found, 
    or invalid year/years then return error. Route can accept the path with or without 
    the trailing slash.
    
    Parameters
    ==========
    :input_name: string
        1 or more country names as they are most commonly known in English, according to the 
        ISO 3166-1.
    :input_year: string
        year, comma separated list of years, or year range to get updates from. Can also accept 
        greater than or less than symbol, returning updates greater than/less than specified year.

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input country name and year.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an invalid 
        parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    names = []
    year = []
    alpha2_code = []
    year_range = False
    greater_than = False
    less_than = False
    
    #path for error message
    error_message['path'] = request.base_url
    
    #parse alpha code parameter, sort, uppercase and remove any whitespace
    if (input_year != ""):
        year = sorted(input_year.replace(' ', '').replace('%20', '').split(','))

    #iterate over all years, convert > or < symbol from unicode to string ("%3E" and "%3C", respectively)
    for y in range(0, len(year)):
        if ("%3E" in year[y]):
            year[y] = ">" + year[y][3:]
        elif ("%3C" in year[y]):
            year[y] = "<" + year[y][3:]

    #remove unicode space (%20) from input parameter
    input_name = input_name.replace('%20', ' ').title()

    #check if input country is in above list, if not add to sorted comma separated list    
    if (input_name.upper() in name_comma_exceptions):
        names = [input_name]
    else:
        names = sorted(input_name.split(','))
    
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

        #using thefuzz library, get all countries that match the input country name
        name_matches = process.extract(name_.upper(), all_names_no_space)

        #return error if no matching country name found
        if (name_matches == []):           
            #return error if country name not found
            error_message["message"] = "No matching country name found for input: {}.".format(name_)
            return jsonify(error_message), 400
        elif (name_matches[0][1] <70):
            if (name_matches[0][1] >60):
                #return error if country name not found
                error_message["message"] = "No matching country name found for input: {}, did you mean {}?".format(name_, name_matches[0][0].title())
            else:
                error_message["message"] = "No matching country name found for input: {}.".format(name_)
            return jsonify(error_message), 400
        
        #use iso3166 package to find corresponding alpha-2 code from its name
        alpha2_code.append(iso3166.countries_by_name[name_matches[0][0].upper()].alpha2)
    
    #validate format of year input parameter: 
    #a '-' separating 2 years implies a year range of sought country updates
    #a ',' separating 2 years implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    if (year != []):
        if ('-' in year[0]):
            year_range = True
            year = year[0].split('-')
            #if years in year range input are wrong way around then swap them
            if (year[0] > year[1]):
                year[0], year[1] = year[1], year[0]
            #only 2 years should be included in input parameter when using a year range
            if (len(year) > 2):
                year = []
                year_range = False
        elif (',' in year[0]):
            #split years into comma separated list of multiple years if multiple years are input
            year = year[0].split(',')
        #parse array if using greater than symbol
        elif ('>' in year[0]):
            year = year[0].split('>')
            greater_than = True
            year.remove('')
            #after removing >, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                greater_than = False
        #parse array if using less than symbol
        elif ('<' in year[0]):
            year = year[0].split('<')
            less_than = True
            year.remove('')
            #after removing <, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                less_than = False
    
    #iterate over all years, validate each are correct format, raise error if invalid year
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>'):
            continue
        #validate each year format using regex, raise error if invalid year input
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            error_message["message"] = f"Invalid year input {''.join(year)}, year should be >1999 and <={datetime.now().year}." 
            return jsonify(error_message), 400
    
    #get updates from iso3166_updates object per country using alpha-2 code
    if (alpha2_code == [] and year == []):
        iso3166_updates = all_iso3166_updates
    else:
        for code in alpha2_code:
            iso3166_updates[code] = all_iso3166_updates[code]
    
    #temporary updates object
    temp_iso3166_updates = {}

    #if no valid alpha-2 codes input, use all alpha-2 codes from iso3166 and all updates data
    if ((year != [] and alpha2_code == []) or ((year == [] or year != []) and alpha2_code == [])):
        input_alpha_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = all_iso3166_updates
    #else set input alpha-2 codes to inputted and use corresponding updates data
    else:
        input_alpha_codes = alpha2_code
        input_data = iso3166_updates
    
    #use temp object to get updates data either for specific country/alpha-2 code or for all
    #countries, dependant on input_alpha_codes and input_data vars above
    if (year != []):
        for code in input_alpha_codes:
            temp_iso3166_updates[code] = []
            for update in range(0, len(input_data[code])):

                #convert year in Date Issued column to string of year, remove "corrected" date if applicable
                if ("corrected" in input_data[code][update]["Date Issued"]):
                    temp_year = str(datetime.strptime(re.sub("[(].*[)]", "", input_data[code][update]["Date Issued"]).replace(' ', "").
                                                      replace(".", '').replace('\n', ''), '%Y-%m-%d').year)
                else:
                    temp_year = str(datetime.strptime(input_data[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d').year)

                #if year range true then get country updates within specified range, inclusive
                if (year_range):
                    if (temp_year != "" and (temp_year >= year[0] and temp_year <= year[1])):
                        temp_iso3166_updates[code].append(input_data[code][update])
                
                #if greater than true then get country updates greater than specified year, inclusive
                elif (greater_than):
                    if (temp_year != "" and (temp_year >= year[0])):
                        temp_iso3166_updates[code].append(input_data[code][update])    

                #if less than true then get country updates less than specified year 
                elif (less_than):
                    if (temp_year != "" and (temp_year < year[0])):
                        temp_iso3166_updates[code].append(input_data[code][update]) 

                #if greater than & less than not true then get country updates equal to specified year
                elif not (greater_than and less_than):
                    for year_ in year:
                        if (temp_year != "" and (temp_year == year_)):
                            temp_iso3166_updates[code].append(input_data[code][update])
            
            #if current alpha-2 has no rows for selected year/year range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = input_data
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/api/months/<input_month>', methods=['GET'])
@app.route('/api/months', methods=['GET'])
@app.route('/months/<input_month>', methods=['GET'])
@app.route('/months/<input_month>/alpha', methods=['GET'])
@app.route('/months/<input_month>/name', methods=['GET'])
@app.route('/months', methods=['GET'])
def api_months(input_month: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/months' path/endpoint. Return all ISO 3166 updates for 
    the previous number of months specified by month parameter. If invalid month 
    input then return error. Route can accept the path with or without the 
    trailing slash.

    Parameters
    ==========
    :input_month: string
        number of past months to get published updates from, inclusive.

    Returns 
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input month.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an invalid 
        parameter input.
    """
    #set path url for error message object
    error_message['path'] = request.base_url
    
    #if no input month parameter then return error message
    if (input_month == ""):
        error_message["message"] = "The month input parameter cannot be empty." 
        return jsonify(error_message), 400    

    #return error if invalid month value input, skip if month range input
    if not ('-' in input_month):
        if not (str(input_month).isdigit()):
            error_message["message"] = f"Invalid month input: {''.join(input_month)}."
            return jsonify(error_message), 400

    #get current datetime object
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")
    
    #parse from date query string param, used for testing the /months endpoints, the from date will be the starting date used instead of the current date
    from_date = request.args.get('from_date')

    #convert from_date parameter into datetime object, set from_date as current datetime param value, if conversion fails set to None
    if not (from_date is None):
        try:
            from_date = datetime.strptime(from_date.replace('\n', ''), '%Y-%m-%d')
            current_datetime = from_date
        except:
            from_date = None

    #temporary updates object
    temp_iso3166_updates = {}

    #get all alpha-2 codes from iso3166 and all updates data before filtering by month
    input_alpha_codes = list(iso3166.countries_by_alpha2.keys())

    #remove XK (Kosovo) from list, if applicable
    if ("XK" in input_alpha_codes):
        input_alpha_codes.remove("XK")
    
    #filter out updates that are not within specified month range
    for code in input_alpha_codes:
        temp_iso3166_updates[code] = [] 
        for update in range(0, len(all_iso3166_updates[code])):

            #convert year in Date Issued column to date object, remove "corrected" date if applicable
            if ("corrected" in all_iso3166_updates[code][update]["Date Issued"]):
                row_date = datetime.strptime(re.sub("[(].*[)]", "", all_iso3166_updates[code][update]["Date Issued"]).replace(' ', "").
                                                    replace(".", '').replace('\n', ''), '%Y-%m-%d')
            else:
                row_date = datetime.strptime(all_iso3166_updates[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d')
            
            #calculate difference in dates
            date_diff = relativedelta.relativedelta(current_datetime, row_date)

            #calculate months difference
            diff_months = date_diff.months + (date_diff.years * 12)

            #parse parameter to get range of months to get updates from
            if ('-' in input_month):
                start_month, end_month = int(input_month.split('-')[0]), int(input_month.split('-')[1])
                #if months in month range input are wrong way around then swap them
                if (start_month > end_month):
                    start_month, end_month = end_month, start_month
                #if current updates row is >= start month input param and <= end month then add to temp object
                if ((diff_months >= start_month) and (diff_months <= end_month)):
                    temp_iso3166_updates[code].append(all_iso3166_updates[code][update])
            else:
                #if current updates row is <= month input param then add to temp object
                if (diff_months <= int(input_month)):
                    temp_iso3166_updates[code].append(all_iso3166_updates[code][update])

        #if current alpha-2 has no rows for selected month range, remove from temp object
        if (temp_iso3166_updates[code] == []):
            temp_iso3166_updates.pop(code, None)

    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/api/months/<input_month>/alpha/<input_alpha>', methods=['GET'])
@app.route('/api/alpha/<input_alpha>/months/<input_month>', methods=['GET'])
@app.route('/months/<input_month>/alpha/<input_alpha>', methods=['GET'])
@app.route('/alpha/<input_alpha>/months/<input_month>', methods=['GET'])
def api_months_alpha(input_month: str="", input_alpha: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/months' + '/api/alpha' path/endpoint. Return all ISO 3166 
    updates for the previous number of months specified by month parameter, for a 
    specified country or list of countries via their ISO 3166-1 alpha-2, alpha-3 or 
    numeric country codes. The alpha-3 and numeric codes  will be converted into their 
    corresponding alpha-2 code. If an invalid alpha code or invalid month input then 
    return error. Route can accept the path with or without the trailing slash.

    Parameters
    ==========
    :input_month: string
        number of past months to get published updates from, inclusive.
    :input_alpha: string
        1 or more ISO 3166-1 alpha-2, alpha-3 or numeric country codes.

    Returns
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input month and country alpha code.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an invalid 
        parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    alpha2_code = []

    #set path url for error message object
    error_message['path'] = request.base_url
    
    #return error if invalid month value input, skip if month range input
    if not ('-' in input_month):
        if not (str(input_month).isdigit()):
            error_message["message"] = f"Invalid month input: {''.join(input_month)}."
            return jsonify(error_message), 400

    #get current datetime object
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

    #parse from date query string param, used for testing the /months endpoints, the from date will be the starting date used instead of the current date
    from_date = request.args.get('from_date')

    #convert from_date parameter into datetime object, set from_date as current datetime param value, if conversion fails set to None
    if not (from_date is None):
        try:
            from_date = datetime.strptime(from_date.replace('\n', ''), '%Y-%m-%d')
            current_datetime = from_date
        except:
            from_date = None

    #parse alpha code parameter, split, uppercase, remove any whitespace and sort
    alpha2_code = sorted(input_alpha.upper().replace(' ', '').replace('%20', '').split(','))
    
    #iterate over each input alpha code, validating and converting into its corresponding alpha-2, if applicable
    for code in range(0, len(alpha2_code)):
        #api can accept 3 letter alpha-3 or numeric code for country, this has to be converted into its alpha-2 counterpart
        if (len(alpha2_code[code]) == 3):
            temp_code = convert_to_alpha2(alpha2_code[code])
            #return error message if invalid numeric code input
            if (temp_code is None and alpha2_code[code].isdigit()):
                error_message["message"] = f"Invalid ISO 3166-1 numeric country code input, cannot convert into corresponding alpha-2 code: {''.join(alpha2_code[code])}."
                return jsonify(error_message), 400
            #return error message if invalid alpha-3 code input
            if (temp_code is None):
                error_message["message"] = f"Invalid ISO 3166-1 alpha-3 country code input, cannot convert into corresponding alpha-2 code: {''.join(alpha2_code[code])}."
                return jsonify(error_message), 400
            alpha2_code[code] = temp_code
        #use regex to validate format of alpha-2 codes, raise error if invalid code input
        if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[code]))) or (alpha2_code[code] not in list(iso3166.countries_by_alpha2.keys()) or (alpha2_code[code] == "XK")):
            error_message["message"] = f"Invalid ISO 3166-1 alpha country code input, no corresponding alpha-2 code found: {''.join(alpha2_code[code])}."
            return jsonify(error_message), 400
        
    #get updates from iso3166_updates instance object per country using alpha-2 code
    for code in alpha2_code:
        iso3166_updates[code] = all_iso3166_updates[code]
        
    #temporary updates object
    temp_iso3166_updates = {}

    #filter out updates that are not within specified month range
    for code in alpha2_code:
        temp_iso3166_updates[code] = [] 
        for update in range(0, len(iso3166_updates[code])):

            #convert year in Date Issued column to date object, remove "corrected" date if applicable
            if ("corrected" in iso3166_updates[code][update]["Date Issued"]):
                row_date = datetime.strptime(re.sub("[(].*[)]", "", iso3166_updates[code][update]["Date Issued"]).replace(' ', "").
                                                    replace(".", '').replace('\n', ''), '%Y-%m-%d')
            else:
                row_date = datetime.strptime(iso3166_updates[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d')
            
            #calculate difference in dates
            date_diff = relativedelta.relativedelta(current_datetime, row_date)

            #calculate months difference
            diff_months = date_diff.months + (date_diff.years * 12)

            #parse parameter to get range of months to get updates from
            if ('-' in input_month):
                start_month, end_month = int(input_month.split('-')[0]), int(input_month.split('-')[1])
                #if months in month range input are wrong way around then swap them
                if (start_month > end_month):
                    start_month, end_month = end_month, start_month
                #if current updates row is >= start month input param and <= end month then add to temp object
                if ((diff_months >= start_month) and (diff_months <= end_month)):
                    temp_iso3166_updates[code].append(iso3166_updates[code][update])
            else:
                #if current updates row is <= month input param then add to temp object
                if (diff_months <= int(input_month)):
                    temp_iso3166_updates[code].append(iso3166_updates[code][update])

        #if current alpha-2 has no rows for selected month range, remove from temp object
        if (temp_iso3166_updates[code] == []):
            temp_iso3166_updates.pop(code, None)

    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/api/months/<input_month>/name/<input_name>', methods=['GET'])
@app.route('/api/name/<input_name>/months/<input_month>', methods=['GET'])
@app.route('/months/<input_month>/name/<input_name>', methods=['GET'])
@app.route('/name/<input_name>/months/<input_month>', methods=['GET'])
def api_months_name(input_month: str="", input_name: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/months' + '/api/name' path/endpoint. Return all ISO 3166 
    updates for the previous number of months specified by month parameter, for a 
    specified country or list of countries using their country name, as it is commonly
    known in English. If an invalid country name or invalid month input then return 
    error. Route can accept the path with or without the trailing slash.

    Parameters
    ==========
    :input_month: string
        number of past months to get published updates from, inclusive.
    :input_name: string
        1 or more ISO 3166-1 country names, as they are commonly known in English.

    Returns
    =======
    :iso3166_updates: json
        jsonified response of iso3166 updates per input month and country name.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an invalid 
        parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    names = []
    alpha2_codes = []

    #set path url for error message object
    error_message['path'] = request.base_url
    
    #return error if invalid month value input, skip if month range input
    if not ('-' in input_month):
        if not (str(input_month).isdigit()):
            error_message["message"] = f"Invalid month input: {''.join(input_month)}."
            return jsonify(error_message), 400

    #get current datetime object
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

    #parse from date query string param, used for testing the /months endpoints, the from date will be the starting date used instead of the current date
    from_date = request.args.get('from_date')

    #convert from_date parameter into datetime object, set from_date as current datetime param value, if conversion fails set to None
    if not (from_date is None):
        try:
            from_date = datetime.strptime(from_date.replace('\n', ''), '%Y-%m-%d')
            current_datetime = from_date
        except:
            from_date = None

    #remove unicode space (%20) from input parameter
    input_name = input_name.replace('%20', ' ').title()
    
    #check if input country is in above list, if not add to sorted comma separated list    
    if (input_name.upper() in name_comma_exceptions):
        names = [input_name]
    else:
        names = sorted(input_name.split(','))
    
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

        #using thefuzz library, get all countries that match the input country name
        name_matches = process.extract(name_.upper(), all_names_no_space, scorer=fuzz.ratio)
        
        #return error if no matching country name found
        if (name_matches == []):           
            #return error if country name not found
            error_message["message"] = "No matching country name found for input: {}.".format(name_)
            return jsonify(error_message), 400
        elif (name_matches[0][1] <70):
            if (name_matches[0][1] >60):
                #return error if country name not found
                error_message["message"] = "No matching country name found for input: {}, did you mean {}?".format(name_, name_matches[0][0].title())
            else:
                error_message["message"] = "No matching country name found for input: {}.".format(name_)
            return jsonify(error_message), 400

        #use iso3166 package to find corresponding alpha-2 code from its name
        alpha2_codes.append(iso3166.countries_by_name[name_matches[0][0].upper()].alpha2)

    #get updates from iso3166_updates instance object per country using alpha-2 code
    for code in alpha2_codes:
        iso3166_updates[code] = all_iso3166_updates[code]
        
    #temporary updates object
    temp_iso3166_updates = {}

    #filter out updates that are not within specified month range
    for code in alpha2_codes:
        temp_iso3166_updates[code] = [] 
        for update in range(0, len(iso3166_updates[code])):

            #convert year in Date Issued column to date object, remove "corrected" date if applicable
            if ("corrected" in iso3166_updates[code][update]["Date Issued"]):
                row_date = datetime.strptime(re.sub("[(].*[)]", "", iso3166_updates[code][update]["Date Issued"]).replace(' ', "").
                                                    replace(".", '').replace('\n', ''), '%Y-%m-%d')
            else:
                row_date = datetime.strptime(iso3166_updates[code][update]["Date Issued"].replace('\n', ''), '%Y-%m-%d')
            
            #calculate difference in dates
            date_diff = relativedelta.relativedelta(current_datetime, row_date)

            #calculate months difference
            diff_months = date_diff.months + (date_diff.years * 12)

            #parse parameter to get range of months to get updates from
            if ('-' in input_month):
                start_month, end_month = int(input_month.split('-')[0]), int(input_month.split('-')[1])
                #if months in month range input are wrong way around then swap them
                if (start_month > end_month):
                    start_month, end_month = end_month, start_month
                #if current updates row is >= start month input param and <= end month then add to temp object
                if ((diff_months >= start_month) and (diff_months <= end_month)):
                    temp_iso3166_updates[code].append(iso3166_updates[code][update])
            else:
                #if current updates row is <= month input param then add to temp object
                if (diff_months <= int(input_month)):
                    temp_iso3166_updates[code].append(iso3166_updates[code][update])

        #if current alpha-2 has no rows for selected month range, remove from temp object
        if (temp_iso3166_updates[code] == []):
            temp_iso3166_updates.pop(code, None)

    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

'''
/api/name and /api/name/year path/endpoints can accept multiple country names, separated 
by a comma but several countries contain a comma already in their official name in the 
iso3166 package. Separate multiple country names by a comma, cast to a sorted list, 
unless any of the names are in the below list...
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

def convert_to_alpha2(alpha_code: str):
    """ 
    Auxillary function that converts an ISO 3166-1 country's 3 letter 
    alpha-3 or numeric code into its 2 letter alpha-2 counterpart. 

    Parameters 
    ==========
    :alpha3_code: str
        3 letter ISO 3166-1 alpha-3 or numeric country code.
    
    Returns
    =======
    :iso3166.countries_by_alpha3[alpha3_code].alpha2: str
        2 letter ISO 3166 alpha-2 country code. 
    """
    if (alpha_code.isdigit()):
        #return error if numeric code not found
        if not (alpha_code in list(iso3166.countries_by_numeric.keys())):
            return None
        else:
            #use iso3166 package to find corresponding alpha-2 code from its numeric code
            return iso3166.countries_by_numeric[alpha_code].alpha2

    #return error if 3 letter alpha-3 code not found
    if not (alpha_code in list(iso3166.countries_by_alpha3.keys())):
        return None
    else:
        #use iso3166 package to find corresponding alpha-2 code from its alpha-3 code
        return iso3166.countries_by_alpha3[alpha_code].alpha2

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