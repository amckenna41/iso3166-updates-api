from flask import Flask, request, render_template, jsonify, redirect, url_for
from google.cloud import storage
from google.oauth2 import service_account
import json 
import iso3166
import re
import os
from datetime import datetime
from dateutil import relativedelta
from difflib import get_close_matches

#initialise Flask app
app = Flask(__name__)

#get Cloud Storage specific env vars
sa_json_str = os.environ["SA_JSON"]
project_id = os.environ["PROJECT_ID"]
bucket_name = os.environ["BUCKET_NAME"]
blob_name = os.environ["BLOB_NAME"]
blob_path = "gs://" + bucket_name + "/" + blob_name

##### Import ISO3166 updates JSON from GCP Storage bucket #####
#convert str of service account from env var into json 
sa_json = json.loads(sa_json_str)
#pass service account json into credentials object
credentials = service_account.Credentials.from_service_account_info(sa_json)
#create GCP Storage client using credentials
storage_client = storage.Client(project=project_id, credentials=credentials)
#initialise bucket object
bucket = storage_client.bucket(bucket_name)
#get blob from bucket
blob = bucket.blob(os.environ["BLOB_NAME"])      
#bool to track if blob exists
blob_exists = True
#return error if object not found in bucket
if (blob.exists()):    
    #load json from blob on bucket
    all_iso3166_updates = json.loads(storage.Blob.from_string(blob_path, client=storage_client).download_as_text())
else:
    blob_exists = False

#error message returned if issue retrieving updates json
blob_not_found_error_message = {}
blob_not_found_error_message["status_code"] = 400
blob_not_found_error_message["message"] = "Error finding updates object in GCP Storage Bucket."

#json object storing the error message, route and status code 
error_message = {}
error_message["status"] = 400

@app.route('/')
def home():
    """
    Default route for https://iso3166-updates.com. Main homepage for API displaying the 
    purpose of API and its documentation. 

    Parameters
    ----------
    None

    Returns
    -------
    :render_template : html
      Flask html template for index.html page.
    :blob_not_found_error_message : dict 
        error message if issue finding updates object json.
    :status_code : int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input. 
    """
    #return error if blob not found in bucket 
    if not (blob_exists):
        return jsonify(blob_not_found_error_message), 400
    
    #raise error if /api not prepended to url path before parameters
    if ('year' or 'alpha2') in list(request.args):
        error_message["message"] = "/api path must feature in URL endpoint."
        error_message['path'] = request.base_url
        return jsonify(error_message), 400

    return render_template('index.html', string=all_iso3166_updates)

@app.route('/api', methods=['GET'])
@app.route('/api/', methods=['GET'])
@app.route('/api/alpha2', methods=['GET'])
@app.route('/api/alpha2/', methods=['GET'])
@app.route('/api/name/', methods=['GET'])
@app.route('/api/name', methods=['GET'])
@app.route('/api/year', methods=['GET'])
@app.route('/api/year/', methods=['GET'])
@app.route('/api/months', methods=['GET']) 
@app.route('/api/months/', methods=['GET'])
def api():
    """
    Main route for API (https://iso3166-updates.com/api) that can accept the alpha-2, 
    year, months and name paths and query string parameters and return the relevant 
    ISO 3166 updates. The API uses a pre-created json with all the latest updates 
    stored in a GCP Cloud Storage bucket, the object is imported in after 
    authentication and used as the basis of the API. If query string parameters are
    appended to the path they will be redirected to their respective Flask route.
    Route can accept the path with or without the trailing slash.

    Parameters
    ----------
    None

    Returns 
    -------
    :all_iso3166_updates : json
      jsonified response of iso3166 updates.
    :blob_not_found_error_message : dict 
        error message if issue finding updates object json.
    :status_code : int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input. 
    :Flask.redirect : app.route
        Flask route redirected using the redirect function, specific route and URL
        used is determined by input parameters. 
    """
    #initialise vars
    alpha2_code = []
    year = []
    months = ""
    name = ""

    #return error if blob not found in bucket 
    if not (blob_exists):
        return jsonify(blob_not_found_error_message), 400

    #parse alpha-2 code parameter
    if not (request.args.get('alpha2') is None):
        alpha2_code = ','.join(sorted([request.args.get('alpha2').upper()]))
    
    #parse year parameter
    if not (request.args.get('year') is None):
        year = request.args.get('year')

    #parse months parameter, return error message if invalid input
    if not (request.args.get('months') is None):
        try:
            months = int(request.args.get('months'))
        except:
            error_message["message"] = f"Invalid month input: {''.join(request.args.get('months'))}."
            error_message['path'] = request.base_url
            return jsonify(error_message), 400

    #parse name parameter
    if not (request.args.get('name') is None):
        name = request.args.get('name')

    #redirect to api_alpha2 route if alpha-2 query string parameter set 
    if (alpha2_code != [] and year == []):
        return redirect(url_for('api_alpha2', input_alpha2=alpha2_code))

    #redirect to api_year route if year query string parameter set 
    if ((alpha2_code == [] and year != [] and name == "") or \
        (alpha2_code == [] and year != [] and months != [])):
        return redirect(url_for('api_year', input_year=year))

    #redirect to api_alpha2_year route if alpha-2 and year query string parameter set 
    if (alpha2_code != [] and year != []):
        return redirect(url_for('api_alpha2_year', input_alpha2=alpha2_code, input_year=year))

    #redirect to api_month route if month query string parameter set 
    if (alpha2_code == [] and year == [] and name == "" and months != ""):
        return redirect(url_for('api_month', input_month=months))

    #redirect to api_name route if name query string parameter set 
    if (name != "" and alpha2_code == []):
        return redirect(url_for('api_name', input_month=months))

    #if no input parameters set then return all ISO3166 updates for all countries
    if (year == [] and alpha2_code == [] and months == "" and name == ""):
        return jsonify(all_iso3166_updates), 200

@app.route('/alpha2/<input_alpha2>', methods=['GET'])
@app.route('/alpha2/<input_alpha2>/', methods=['GET'])
@app.route('/api/alpha2/<input_alpha2>', methods=['GET'])
@app.route('/api/alpha2/<input_alpha2>/', methods=['GET'])
@app.route('/api/alpha2/<input_alpha2>/year/', methods=['GET'])
@app.route('/api/alpha2/<input_alpha2>/year', methods=['GET'])
def api_alpha2(input_alpha2):
    """
    Flask route for alpha-2 path. Return all ISO 3166 updates
    for the inputted alpha-2 code/codes. If invalid alpha-2
    code then return error. Additionally, if the alpha-2 + year 
    path is appended to URL but no year proceeds the year 
    parameter but a valid alpha-2 code/codes are input then 
    return all listed ISO 3166 updates for countrys specified 
    by the input alpha-2 code/codes. The route can also accept
    the corresponding 3 letter alpha-3 code for all of the 
    alpha-2 codes. Route can accept path with or without trailing 
    slash.

    Parameters
    ----------
    :input_alpha2 : string/list
        1 or more 2 letter alpha-2 country codes according to ISO 3166-1.
        Can also accept the 3 letter alpha-3 code counterparts for each 
        of the alpha-2 codes.

    Returns 
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates per input alpha-2 code.
    :blob_not_found_error_message : dict 
        error message if issue finding updates object json.  
    :status_code : int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    alpha2_code = []
    
    #return error if blob not found in bucket 
    if not (blob_exists):
        return jsonify(blob_not_found_error_message), 400

    #parse alpha-2 code parameter
    if not (input_alpha2 is None and input_alpha2 != ""):
        alpha2_code = sorted([input_alpha2.upper()])
    
    #if no input parameters set then return all country updates (all_iso3166_updates)
    if (alpha2_code == []):
        return jsonify(all_iso3166_updates), 200
    
    #validate alpha-2 codes, remove any invalid ones, raise error if invalid alpha-3 codes input
    if (alpha2_code != []):
        if (',' in alpha2_code[0]):
            alpha2_code = alpha2_code[0].split(',')
            alpha2_code = [code.strip() for code in alpha2_code]
            for code in range(0, len(alpha2_code)):
                #api can accept 3 letter alpha-3 code for country, this has to be converted into its alpha-2 counterpart
                if (len(alpha2_code[code]) == 3):
                    temp_code = convert_to_alpha2(alpha2_code[code])
                    #return error message if invalid alpha-3 code input
                    if (temp_code is None):
                        error_message["message"] = f"Invalid 3 letter alpha-3 code input: {''.join(alpha2_code[code])}."
                        error_message['path'] = request.base_url
                        return jsonify(error_message), 400
                    alpha2_code[code] = temp_code
                #use regex to validate format of alpha-2 codes, raise error if invalid code input
                if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[code]))) or (alpha2_code[code] not in list(iso3166.countries_by_alpha2.keys())):
                    error_message["message"] = f"Invalid 2 letter alpha-2 code input: {''.join(alpha2_code[code])}."
                    error_message['path'] = request.base_url
                    return jsonify(error_message), 400
        else:
            #api can accept 3 letter alpha-3 code for country, this has to be converted into its alpha-2 counterpart
            if (len(alpha2_code[0]) == 3):
                temp_code = convert_to_alpha2(alpha2_code[0])
                #return error message if invalid alpha-3 code input
                if (temp_code is None):
                    error_message["message"] = f"Invalid 3 letter alpha-3 code input: {''.join(alpha2_code[0])}."
                    error_message['path'] = request.base_url
                    return jsonify(error_message), 400
                alpha2_code[0] = temp_code
            #if single alpha-2 code passed in, validate its correctness
            if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[0]))) or \
                (alpha2_code[0] not in list(iso3166.countries_by_alpha2.keys()) and \
                alpha2_code[0] not in list(iso3166.countries_by_alpha3.keys())):
                error_message["message"] = f"Invalid 2 letter alpha-2 code input: {''.join(alpha2_code)}."
                error_message['path'] = request.base_url
                return jsonify(error_message), 400

    #get updates from iso3166_updates object per country using alpha-2 code
    #if no valid alpha-2 codes input, use all alpha-2 codes from iso3166 and all updates data
    if (alpha2_code == []):
        iso3166_updates = all_iso3166_updates
        input_data = all_iso3166_updates
    else:
        for code in alpha2_code:
            iso3166_updates[code] = all_iso3166_updates[code]
        input_data = iso3166_updates
        
    #set main updates dict to temp one
    iso3166_updates = input_data

    return jsonify(iso3166_updates), 200

@app.route('/year/<input_year>', methods=['GET'])
@app.route('/year/<input_year>/', methods=['GET'])
@app.route('/api/year/<input_year>', methods=['GET'])
@app.route('/api/year/<input_year>/', methods=['GET'])
@app.route('/api/year/<input_year>/alpha2/', methods=['GET'])
@app.route('/api/year/<input_year>/alpha2', methods=['GET'])
def api_year(input_year):
    """
    Flask route for year path. Return all ISO 3166 updates
    for the inputted year/years/year range or greater than 
    or less than input year. If invalid year then return 
    error. Route can accept the path with or without the 
    trailing slash.

    Parameters
    ----------
    :input_year : string/list
        year, list of years, or year range to get updates
        from. Can also accept greater than or less than symbol
        returning updates greater than/less than specified year.

    Returns 
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates per input year/years.
    :blob_not_found_error_message : dict 
        error message if issue finding updates object json in storage bucket.
    :status_code : int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    year_range = False
    greater_than = False
    less_than = False
    year = []

    #return error if blob not found in bucket 
    if not (blob_exists):
        return jsonify(blob_not_found_error_message), 400

    #parse year parameter, convert to list
    if not (input_year is None and input_year != ""):
        year = sorted([input_year])

    #if no input parameters set then return all country updates (all_iso3166_updates)
    if (year == []):
        return jsonify(all_iso3166_updates), 200

    #iterate over all years, convert > or < symbol from unicode to string ("%3E" and "%3C", respectively)
    for y in range(0, len(year)):
        if ("%3E" in year[y]):
            year[y] = ">" + year[y][3:]
        elif ("%3C" in year[y]):
            year[y] = "<" + year[y][3:]

    #a '-' seperating 2 years implies a year range of sought country updates
    #a ',' seperating 2 year implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    #validate format of year input parameter 
    if (year != []):
        if ('-' in year[0]):
            year_range = True
            year = year[0].split('-')
            #only 2 years should be included in input parameter when using a year range
            if (len(year) > 2):
                year = []
                year_range = False
        elif (',' in year[0]):
            #split years into multiple years, if multiple are input, seperated by comma
            year = year[0].split(',')
        #parse array for using greater than symbol
        elif ('>' in year[0]):
            year = year[0].split('>')
            greater_than = True
            year.remove('')
            #after removing >, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                greater_than = False
        #parse array for using less than symbol
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
            error_message["message"] = f"Invalid year input: {''.join(year)}."
            error_message['path'] = request.base_url
            return jsonify(error_message), 400
    
    #temporary updates object
    temp_iso3166_updates = {}
    
    #use temp object to get updates data either for specific country/alpha-2 codes or for all countries
    if (year != []):
        
        #if no valid alpha-2 codes input, use all alpha-2 codes from iso3166 and all updates data (all_iso3166_updates)
        input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = all_iso3166_updates

        for code in input_alpha2_codes:
            #skip XK (Kosovo)
            if (code == "XK"):
                continue 
            temp_iso3166_updates[code] = []
            for update in range(0, len(input_data[code])):

                #convert year in Date Issued column to string of year
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
    else:
        temp_iso3166_updates = all_iso3166_updates #return updates data when Years params is empty
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/year/<input_year>/alpha2/<input_alpha2>', methods=['GET'])
@app.route('/year/<input_year>/alpha2/<input_alpha2>/', methods=['GET'])
@app.route('/api/year/<input_year>/alpha2/<input_alpha2>', methods=['GET'])
@app.route('/api/year/<input_year>/alpha2/<input_alpha2>/', methods=['GET'])
@app.route('/api/alpha2/<input_alpha2>/year/<input_year>', methods=['GET'])
@app.route('/api/alpha2/<input_alpha2>/year/<input_year>/', methods=['GET'])
def api_alpha2_year(input_alpha2, input_year):
    """
    Flask route for alpha-2 + year path. Return all ISO 3166 updates
    for the inputted alpha-2 code/codes + year/years/year range or 
    greater than or less than input year. If invalid alpha-2 code or 
    year/years input then return error. The route can also accept the 
    3 letter alpha-3 counterpart for each alpha-2 code. Route can accept 
    the path with or without the trailing slash.
    
    Parameters
    ----------
    :input_alpha2 : string/list
        1 or more 2 letter alpha-2 country codes according to ISO 3166-1.
        Can also accept the 3 letter alpha-3 counterpart for each alpha-2
        code.
    :input_year : string/list
        year, list of years, or year range to get updates
        from. Can also accept greater than or less than symbol
        returning updates greater than/less than specified year.

    Returns 
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates per input alpha-2 code and year.
    :blob_not_found_error_message : dict 
        error message if issue finding updates object json in storage bucket.
    :status_code : int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    alpha2_code = []
    year_range = False
    greater_than = False
    less_than = False
    year = []

    #return error if blob not found in bucket 
    if not (blob_exists):
        return jsonify(blob_not_found_error_message), 400

    #parse alpha-2 code parameter, sort and convert to list
    if not (input_alpha2 is None and input_alpha2 != ""):
        alpha2_code = sorted([input_alpha2.upper()])
    
    #parse year parameter, convert to list
    if not (input_year is None and input_year != ""):
        year = sorted([input_year])

    #if no input parameters set then return all country updates (all_iso3166_updates)
    if (year == [] and alpha2_code == []):
        return jsonify(all_iso3166_updates), 200

    #iterate over all years, convert > or < symbol from unicode to string ("%3E" and "%3C", respectively)
    for y in range(0, len(year)):
        if ("%3E" in year[y]):
            year[y] = ">" + year[y][3:]
        elif ("%3C" in year[y]):
            year[y] = "<" + year[y][3:]

    #validate all alpha-2 codes input, remove any invalid ones, raise error if invalid alpha-3 codes
    if (alpha2_code != []):
        if (',' in alpha2_code[0]):
            alpha2_code = alpha2_code[0].split(',')
            alpha2_code = [code.strip() for code in alpha2_code]
            for code in range(0, len(alpha2_code)):
                #api can accept 3 letter alpha-3 code for country, this has to be converted into its alpha-2 counterpart
                if (len(alpha2_code[code]) == 3):
                    temp_code = convert_to_alpha2(alpha2_code[code])
                    #return error message if invalid alpha-3 code input
                    if (temp_code is None):
                        error_message["message"] = f"Invalid 3 letter alpha-3 code input: {''.join(alpha2_code[code])}."
                        error_message['path'] = request.base_url
                        return jsonify(error_message), 400
                    alpha2_code[code] = temp_code
                #use regex to validate format of alpha-2 codes, raise error if invalid code input
                if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[code]))) or (alpha2_code[code] not in list(iso3166.countries_by_alpha2.keys())):
                    error_message["message"] = f"Invalid 2 letter alpha-2 code input: {''.join(alpha2_code[code])}."
                    error_message['path'] = request.base_url
                    return jsonify(error_message), 400
        else:
            #api can accept 3 letter alpha-3 code for country, this has to be converted into its alpha-2 counterpart
            if (len(alpha2_code[0]) == 3):
                temp_code = convert_to_alpha2(alpha2_code[0])
                #return error message if invalid alpha-3 code input
                if (temp_code is None):
                    error_message["message"] = f"Invalid 3 letter alpha-3 code input: {''.join(alpha2_code[0])}."
                    error_message['path'] = request.base_url
                    return jsonify(error_message), 400
                alpha2_code[0] = temp_code
            #if single alpha-2 code passed in, validate its correctness, raise error if invalid  alpha-2
            if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[0]))) or \
                (alpha2_code[0] not in list(iso3166.countries_by_alpha2.keys()) and \
                alpha2_code[0] not in list(iso3166.countries_by_alpha3.keys())):
                error_message["message"] = f"Invalid 2 letter alpha-2 code input: {''.join(alpha2_code)}."
                error_message['path'] = request.base_url
                return jsonify(error_message), 400

    #a '-' seperating 2 years implies a year range of sought country updates
    #a ',' seperating 2 year implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    #validate format of year input parameter 
    if (year != []):
        if ('-' in year[0]):
            year_range = True
            year = year[0].split('-')
            #only 2 years should be included in input parameter when using a year range
            if (len(year) > 2):
                year = []
                year_range = False
        elif (',' in year[0]):
            #split years into multiple years, if multiple are input seperated by comma
            year = year[0].split(',')
        #parse array for using greater than symbol
        elif ('>' in year[0]):
            year = year[0].split('>')
            greater_than = True
            year.remove('')
            #after removing >, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                greater_than = False
        #parse array for using less than symbol
        elif ('<' in year[0]):
            year = year[0].split('<')
            less_than = True
            year.remove('')
            #after removing <, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                less_than = False
    
    #iterate over all years, validate each are valid years, raise error if invalid year
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>'):
            continue
        #validate each year format using regex, raise error if invalid year input
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            error_message["message"] = f"Invalid year input: {''.join(year)}."
            error_message['path'] = request.base_url
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
        input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = all_iso3166_updates
    #else set input alpha-2 codes to inputted and use corresponding updates data
    else:
        input_alpha2_codes = alpha2_code
        input_data = iso3166_updates
    
    #use temp object to get updates data either for specific country/alpha-2 code or for all
    #countries, dependant on input_alpha2_codes and input_data vars above
    if (year != []):
        for code in input_alpha2_codes:
            temp_iso3166_updates[code] = []
            for update in range(0, len(input_data[code])):

                #convert year in Date Issued column to string of year
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
            
            #if current alpha-2 has no rows for selected year/year range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = input_data #return updates data when Years and Month params are empty
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/year/<input_year>/name/<input_name>', methods=['GET'])
@app.route('/year/<input_year>/name/<input_name>/', methods=['GET'])
@app.route('/api/year/<input_year>/name/<input_name>', methods=['GET'])
@app.route('/api/year/<input_year>/name/<input_name>/', methods=['GET'])
@app.route('/api/name/<input_name>/year/<input_year>', methods=['GET'])
@app.route('/api/name/<input_name>/year/<input_year>/', methods=['GET'])
def api_name_year(input_name, input_year):
    """
    Flask route for name + year path. Return all ISO 3166 updates
    for the inputted country name/names + year/years/year range or 
    greater than or less than input year. If invalid name or year/years 
    input then return error. Route can accept the path with or without 
    the trailing slash.
    
    Parameters
    ----------
    :input_name : string/list
        1 or more country names as they are most commonly known in English,
        according to the ISO 3166-1.
    :input_year : string/list
        year, list of years, or year range to get updates
        from. Can also accept greater than or less than symbol
        returning updates greater than/less than specified year.

    Returns 
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates per input country name and year.
    :blob_not_found_error_message : dict 
        error message if issue finding updates object json in storage bucket.
    :status_code : int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates = {}
    names = []
    alpha2_code = []
    year_range = False
    greater_than = False
    less_than = False
    year = []

    #return error if blob not found in bucket 
    if not (blob_exists):
        return jsonify(blob_not_found_error_message), 400
    
    #parse year parameter, convert to list
    if not (input_year is None and input_year != ""):
        year = sorted([input_year])

    #iterate over all years, convert > or < symbol from unicode to string ("%3E" and "%3C", respectively)
    for y in range(0, len(year)):
        if ("%3E" in year[y]):
            year[y] = ">" + year[y][3:]
        elif ("%3C" in year[y]):
            year[y] = "<" + year[y][3:]

    #remove unicode space (%20) from input parameter
    input_name = input_name.replace('%20', ' ').title()

    #path can accept multiple country names, seperated by a comma but several
    #countries contain a comma already in their name. Seperate multiple country names
    #by a comma, cast to a sorted list, unless any of the names are in the below list
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
    
    #check if input country is in above list, if not add to sorted comma seperated list    
    if (input_name.upper() in name_comma_exceptions):
        names = [input_name]
    else:
        names = sorted(input_name.split(','))

    #if no input parameters set then return all country updates (all_iso3166_updates)
    if (year == [] and names == []):
        return jsonify(all_iso3166_updates), 200

    #list of country name exceptions that are converted into their more common name
    name_converted = {"UAE": "United Arab Emirates", "Brunei": "Brunei Darussalam", "Bolivia": "Bolivia, Plurinational State of", 
                      "Bosnia": "Bosnia and Herzegovina", "Bonaire": "Bonaire, Sint Eustatius and Saba", "DR Congo": 
                      "Congo, the Democratic Republic of the", "Ivory Coast": "Côte d'Ivoire", "Cape Verde": "Cabo Verde", 
                      "Cocos Islands": "Cocos (Keeling) Islands", "Falkland Islands": "Falkland Islands (Malvinas)", 
                      "Micronesia": "Micronesia, Federated States of", "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
                      "South Georgia": "South Georgia and the South Sandwich Islands", "Iran": "Iran, Islamic Republic of",
                      "North Korea": "Korea, Democratic People's Republic of", "South Korea": "Korea, Republic of", 
                      "Laos": "Lao People's Democratic Republic", "Moldova": "Moldova, Republic of", "Saint Martin": "Saint Martin (French part)",
                      "Macau": "Macao", "Pitcairn Islands": "Pitcairn", "South Georgia": "South Georgia and the South Sandwich Islands",
                      "Heard Island": "Heard Island and McDonald Islands", "Palestine": "Palestine, State of", 
                      "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha", "St Helena": "Saint Helena, Ascension and Tristan da Cunha",              
                      "Saint Kitts": "Saint Kitts and Nevis", "St Kitts": "Saint Kitts and Nevis", "St Vincent": "Saint Vincent and the Grenadines", 
                      "St Lucia": "Saint Lucia", "Saint Vincent": "Saint Vincent and the Grenadines", "Russia": "Russian Federation", 
                      "Sao Tome and Principe":" São Tomé and Príncipe", "Sint Maarten": "Sint Maarten (Dutch part)", "Syria": "Syrian Arab Republic", 
                      "Svalbard": "Svalbard and Jan Mayen", "French Southern and Antarctic Lands": "French Southern Territories", "Turkey": "Türkiye", 
                      "Taiwan": "Taiwan, Province of China", "Tanzania": "Tanzania, United Republic of", "USA": "United States of America", 
                      "United States": "United States of America", "Vatican City": "Holy See", "Vatican": "Holy See", "Venezuela": 
                      "Venezuela, Bolivarian Republic of", "Virgin Islands, British": "British Virgin Islands"}
    
    #iterate over list of names, convert country names from name_converted dict, if applicable
    for name_ in range(0, len(names)):
        if (names[name_].title() in list(name_converted.keys())):
            names[name_] = name_converted[names[name_]]

    #remove all whitespace in any of the country names
    names = [name_.strip(' ') for name_ in names]

    #get list of available country names from iso3166 library, remove whitespace
    all_names_no_space = [name_.strip(' ') for name_ in list(iso3166.countries_by_name.keys())]
    
    #iterate over all input country names, get corresponding 2 letter alpha-2 code
    for name_ in names:

        #get list of country name matches from input name using closeness function, using default cutoff parameter value
        name_matches = get_close_matches(name_.upper(), all_names_no_space)
        matching_name = ""

        #get highest matching country name from one input (manually set British Virgin Islands vs US Virgin Islands)
        if (name_matches != []):           
            if (name_ == "British Virgin Islands"):
                matching_name = name_matches[1]
            else:
                matching_name = name_matches[0]
        else:
            #return error if country name not found
            error_message["message"] = "Country name {} not found in the ISO 3166.".format(name_)
            error_message['path'] = request.base_url
            return jsonify(error_message), 400

        #use iso3166 package to find corresponding alpha-2 code from its name
        alpha2_code.append(iso3166.countries_by_name[matching_name.upper()].alpha2)
    
    #a '-' seperating 2 years implies a year range of sought country updates
    #a ',' seperating 2 year implies a list of years
    #a '>' before year means get all country updates greater than or equal to specified year
    #a '<' before year means get all country updates less than specified year
    #validate format of year input parameter 
    if (year != []):
        if ('-' in year[0]):
            year_range = True
            year = year[0].split('-')
            #only 2 years should be included in input parameter when using a year range
            if (len(year) > 2):
                year = []
                year_range = False
        elif (',' in year[0]):
            #split years into multiple years, if multiple are input seperated by comma
            year = year[0].split(',')
        #parse array for using greater than symbol
        elif ('>' in year[0]):
            year = year[0].split('>')
            greater_than = True
            year.remove('')
            #after removing >, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                greater_than = False
        #parse array for using less than symbol
        elif ('<' in year[0]):
            year = year[0].split('<')
            less_than = True
            year.remove('')
            #after removing <, only 1 year should be left in year parameter
            if (len(year) > 1):
                year = []
                less_than = False
    
    #iterate over all years, validate each are valid years, raise error if invalid year
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>'):
            continue
        #validate each year format using regex, raise error if invalid year input
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            error_message["message"] = f"Invalid year input: {''.join(year)}."
            error_message['path'] = request.base_url
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
        input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = all_iso3166_updates
    #else set input alpha-2 codes to inputted and use corresponding updates data
    else:
        input_alpha2_codes = alpha2_code
        input_data = iso3166_updates
    
    #use temp object to get updates data either for specific country/alpha-2 code or for all
    #countries, dependant on input_alpha2_codes and input_data vars above
    if (year != []):
        for code in input_alpha2_codes:
            temp_iso3166_updates[code] = []
            for update in range(0, len(input_data[code])):

                #convert year in Date Issued column to string of year
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
            
            #if current alpha-2 has no rows for selected year/year range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = input_data #return updates data when Years and Month params are empty
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/months/<input_month>', methods=['GET'])
@app.route('/months/<input_month>/', methods=['GET'])
@app.route('/api/months/<input_month>', methods=['GET'])
@app.route('/api/months/<input_month>/', methods=['GET'])
def api_month(input_month):
    """
    Flask route for month path. Return all ISO 3166 updates
    for the previous number of months specified by month
    parameter. If invalid month input then return error. 
    Route can accept the path with or without the trailing 
    slash.

    Parameters
    ----------
    :input_month : string/list
        number of past months to get published updates from, 
        inclusive.

    Returns 
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates per input month.
    :blob_not_found_error_message : dict 
        error message if issue finding updates object json in storage bucket.  
    :status_code : int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    months = []

    #return error if blob not found in bucket 
    if not (blob_exists):
        return jsonify(blob_not_found_error_message), 400
        
    #get current datetime object
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

    #parse month parameter, raise error if invalid
    if not (input_month is None and input_month != ""):
        try:
            months = int(input_month)
        except:
            error_message["message"] = f"Invalid month input: {input_month}."
            error_message['path'] = request.base_url
            return jsonify(error_message), 400

    #if no input parameters set then return all ISO 3166 updates for all countries
    if (months == []):
        return jsonify(all_iso3166_updates), 200

    #temporary updates object
    temp_iso3166_updates = {}

    #get all alpha-2 codes from iso3166 and all updates data before filtering by month
    input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
    input_data = all_iso3166_updates
    
    #get updates within input months range
    if (months != []):
        #return error if invalid month value input
        if not (str(months).isdigit()):
            error_message["message"] = f"Invalid month input: {''.join(months)}."
            error_message['path'] = request.base_url
            return jsonify(error_message), 400
        for code in input_alpha2_codes:
            temp_iso3166_updates[code] = [] 
            for update in range(0, len(input_data[code])):

                #convert date in Date Issued column to date object
                row_date = (datetime.strptime(input_data[code][update]["Date Issued"], "%Y-%m-%d"))
                
                #calculate difference in dates
                date_diff = relativedelta.relativedelta(current_datetime, row_date)

                #calculate months difference
                diff_months = date_diff.months + (date_diff.years * 12)

                #if current updates row is <= month input param then add to temp object
                if (diff_months <= months):
                    temp_iso3166_updates[code].append(input_data[code][update])
   
            #if current alpha-2 has no rows for selected month range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = input_data #return updates data when Years and Month params are emptya
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

@app.route('/name/<input_name>', methods=['GET'])
@app.route('/name/<input_name>/', methods=['GET'])
@app.route('/api/name/<input_name>', methods=['GET'])
@app.route('/api/name/<input_name>/', methods=['GET'])
def api_name(input_name):
    """
    Flask route for name path. Return all ISO 3166 updates
    for the inputted country name/names. If invalid name then 
    return error. Route can accept the path with or without the 
    trailing slash.

    Parameters
    ----------
    :input_name : string/list
        one or more country names as they are commmonly known in english.

    Returns 
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates per country name/names.
    :blob_not_found_error_message : dict 
        error message if issue finding updates object json in storage bucket.
    :status_code : int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_updates_ = {}
    alpha2_code = []
    names = []    

    #return error if blob not found in bucket 
    if not (blob_exists):
        return jsonify(blob_not_found_error_message), 400

    #if no input parameters set then return error message
    if (input_name == ""):
        error_message["message"] = "The name input parameter cannot be empty."
        error_message['path'] = request.base_url
        return jsonify(error_message), 400

    #remove unicode space (%20) from input parameter
    input_name = input_name.replace('%20', ' ').title()

    #path can accept multiple country names, seperated by a comma but several
    #countries contain a comma already in their name. Seperate multiple country names
    #by a comma, cast to a sorted list, unless any of the names are in the below list
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
    
    #check if input country is in above list, if not add to sorted comma seperated list    
    if (input_name.upper() in name_comma_exceptions):
        names = [input_name]
    else:
        names = sorted(input_name.split(','))
    
    #list of country name exceptions that are converted into their more common name
    name_converted = {"UAE": "United Arab Emirates", "Brunei": "Brunei Darussalam", "Bolivia": "Bolivia, Plurinational State of", 
                      "Bosnia": "Bosnia and Herzegovina", "Bonaire": "Bonaire, Sint Eustatius and Saba", "DR Congo": 
                      "Congo, the Democratic Republic of the", "Ivory Coast": "Côte d'Ivoire", "Cape Verde": "Cabo Verde", 
                      "Cocos Islands": "Cocos (Keeling) Islands", "Falkland Islands": "Falkland Islands (Malvinas)", 
                      "Micronesia": "Micronesia, Federated States of", "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
                      "South Georgia": "South Georgia and the South Sandwich Islands", "Iran": "Iran, Islamic Republic of",
                      "North Korea": "Korea, Democratic People's Republic of", "South Korea": "Korea, Republic of", 
                      "Laos": "Lao People's Democratic Republic", "Moldova": "Moldova, Republic of", "Saint Martin": "Saint Martin (French part)",
                      "Macau": "Macao", "Pitcairn Islands": "Pitcairn", "South Georgia": "South Georgia and the South Sandwich Islands",
                      "Heard Island": "Heard Island and McDonald Islands", "Palestine": "Palestine, State of", 
                      "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha", "St Helena": "Saint Helena, Ascension and Tristan da Cunha",              
                      "Saint Kitts": "Saint Kitts and Nevis", "St Kitts": "Saint Kitts and Nevis", "St Vincent": "Saint Vincent and the Grenadines", 
                      "St Lucia": "Saint Lucia", "Saint Vincent": "Saint Vincent and the Grenadines", "Russia": "Russian Federation", 
                      "Sao Tome and Principe":" São Tomé and Príncipe", "Sint Maarten": "Sint Maarten (Dutch part)", "Syria": "Syrian Arab Republic", 
                      "Svalbard": "Svalbard and Jan Mayen", "French Southern and Antarctic Lands": "French Southern Territories", "Turkey": "Türkiye", 
                      "Taiwan": "Taiwan, Province of China", "Tanzania": "Tanzania, United Republic of", "USA": "United States of America", 
                      "United States": "United States of America", "Vatican City": "Holy See", "Vatican": "Holy See", "Venezuela": 
                      "Venezuela, Bolivarian Republic of", "Virgin Islands, British": "British Virgin Islands"}
    
    #iterate over list of names, convert country names from name_converted dict, if applicable
    for name_ in range(0, len(names)):
        if (names[name_].title() in list(name_converted.keys())):
            names[name_] = name_converted[names[name_]]

    #remove all whitespace in any of the country names
    names = [name_.strip(' ') for name_ in names]

    #get list of available country names from iso3166 library, remove whitespace
    all_names_no_space = [name_.strip(' ') for name_ in list(iso3166.countries_by_name.keys())]
    
    #iterate over all input country names, get corresponding 2 letter alpha-2 code
    for name_ in names:

        #get list of country name matches from input name using closeness function, using default cutoff parameter value
        name_matches = get_close_matches(name_.upper(), all_names_no_space)
        matching_name = ""

        #get highest matching country name from one input (manually set British Virgin Islands vs US Virgin Islands)
        if (name_matches != []):           
            if (name_ == "British Virgin Islands"):
                matching_name = name_matches[1]
            else:
                matching_name = name_matches[0]
        else:
            #return error if country name not found
            error_message["message"] = "Country name {} not found in the ISO 3166.".format(name_)
            error_message['path'] = request.base_url
            return jsonify(error_message), 400

        #use iso3166 package to find corresponding alpha-2 code from its name
        alpha2_code.append(iso3166.countries_by_name[matching_name.upper()].alpha2)
    
    #get country data from ISO3166-2 object, using alpha-2 code
    for code in alpha2_code:
        iso3166_updates_[code] = all_iso3166_updates[code]

    return jsonify(iso3166_updates_), 200

def convert_to_alpha2(alpha3_code):
    """ 
    Convert an ISO 3166 country's 3 letter alpha-3 code into its 2 letter
    alpha-2 counterpart. 

    Parameters 
    ----------
    :alpha3_code: str
        3 letter ISO 3166 country code.
    
    Returns
    -------
    :iso3166.countries_by_alpha3[alpha3_code].alpha2: str
        2 letter ISO 3166 country code. 
    """
    #return error if 3 letter alpha-3 code not found
    if not (alpha3_code in list(iso3166.countries_by_alpha3.keys())):
        return None
    else:
        #use iso3166 package to find corresponding alpha-2 code from its alpha-3
        return iso3166.countries_by_alpha3[alpha3_code].alpha2

@app.errorhandler(404)
def not_found(e):
    """
    Return html template for 404.html when page/path not found in 
    Flask app.

    Parameters
    ----------
    :e : int
        error code.

    Returns
    -------
    :render_template : html
      Flask html template for error.html page.
    :status_code : int
        response status code. 404 code implies page not found.
    """
    error_message_ = ""
    if not ("api" in request.path):
        error_message_ = "Path " + request.path + f" should have the /api path prefix in it:\n{e}" 
    else:
        error_message_ = "ISO 3166 Updates: Page not found: " + request.path + "\n{e}"

    return render_template("404.html", path=error_message_), 404

if __name__ == '__main__':
    #run flask app
    app.run(debug=True)