from flask import Flask, request, render_template, jsonify
import requests
import json 
import iso3166
import re
import logging
import getpass
from datetime import datetime
from dateutil import relativedelta

app = Flask(__name__)

#initialise logging library 
__version__ = "1.0.1"
log = logging.getLogger(__name__)

#initalise User-agent header for requests library 
USER_AGENT_HEADER = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}

OBJECT_URL = "https://storage.googleapis.com/iso3166-updates/iso3166-updates.json"

@app.route('/')
def home():
    """
    Default route for https://iso3166-updates.com. Returns all of the default
    ISO3166 updates data from json.

    Parameters
    ----------
    None

    Returns
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates.
    """
    #get html content from updates json in storage bucket, raise exception if status code != 200
    try:
        page = requests.get(OBJECT_URL, headers=USER_AGENT_HEADER)
        page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    #convert content to json
    iso3166_updates = page.json()
    
    return render_template('index.html', string=iso3166_updates)

@app.route('/api', methods=['GET'])
def api():
    """
    Main route for API (https://iso3166-updates.com/api) that can accept the alpha2 and 
    year query string parameters and return the relevant ISO3166 updates.
    
    Parameters
    ----------
    None

    Returns 
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates.
    """
    #initialise vars
    iso3166_updates = {}
    alpha2_code = []
    year_range = False
    greater_than = False
    less_than = False
    year = []
    months = []

    #json object storing the message and status code 
    error_message = {}

    #get html content from updates json in storage bucket, raise exception if status code != 200
    try:
        page = requests.get(OBJECT_URL, headers=USER_AGENT_HEADER)
        page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    #pgetull json from request object
    all_iso3166_updates = page.json()

    #get current datetime object
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

    #parse alpha2 code parameter
    if not (request.args.get('alpha2') is None):
        alpha2_code = sorted([request.args.get('alpha2').upper()])
    
    #parse year parameter
    if not (request.args.get('year') is None):
        year = [request.args.get('year').upper()]

    #parse months parameter
    if not (request.args.get('months') is None):
        try:
            months = int(request.args.get('months'))
        except:
            raise TypeError("Invalid data type for months parameter, cannot cast to int.")

    #if no input parameters set then return all country update iso3166_updates
    if (year == [] and alpha2_code == [] and months == []):
        return render_template('index.html', string=all_iso3166_updates)
    
    #validate multiple alpha2 codes input, remove any invalid ones
    if (alpha2_code != []):
        if (',' in alpha2_code[0]):
            alpha2_code = alpha2_code[0].split(',')
            alpha2_code = [code.strip() for code in alpha2_code]
            for code in alpha2_code:
                #use regex to validate format of alpha2 codes
                if not (bool(re.match(r"^[A-Z]{2}$", code))) or (code not in list(iso3166.countries_by_alpha2.keys())):
                    alpha2_code.remove(code)
        else:
            #if single alpha2 code passed in, validate its correctness
            if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[0]))) or (alpha2_code[0] not in list(iso3166.countries_by_alpha2.keys())):
                error_message["message"] = f"Invalid 2 letter alpha-2 code input: {''.join(alpha2_code)}"
                error_message["status"] = 400
                return jsonify(error_message), 400
                # alpha2_code.remove(alpha2_code[0])

    #a '-' seperating 2 years implies a year range of sought country updates, validate format of years in range
    if (year != [] and months == []):
        if ('-' in year[0]):
            year_range = True
            year = year[0].split('-')
            #only 2 years should be included in input parameter
            if (len(year) > 2):
                year = []
                year_range = False
        elif (',' in year[0]):
            #split years into multiple years, if multiple are input
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
    
    for year_ in year:
        #skip to next iteration if < or > symbol
        if (year_ == '<' or year_ == '>'):
            continue
        #validate each year format using regex
        if not (bool(re.match(r"^1[0-9][0-9][0-9]$|^2[0-9][0-9][0-9]$", year_))):
            error_message["message"] = f"Invalid year input: {''.join(year)}"
            error_message["status"] = 400
            return jsonify(error_message), 400

    #get updates from iso3166_updates object per country using alpha2 code
    if (alpha2_code == [] and year == [] and months == []):
        # iso3166_updates = {alpha2_code[0]: all_iso3166_updates[alpha2_code[0]]}
        iso3166_updates = all_iso3166_updates
    else:
        for code in alpha2_code:
            iso3166_updates[code] = all_iso3166_updates[code]
    
    #temporary updates object
    temp_iso3166_updates = {}

    #if no valid alpha2 codes input use all alpha2 codes from iso3166 and all updates data
    if ((year != [] and alpha2_code == [] and months == []) or \
        ((year == [] or year != []) and alpha2_code == [] and months != [])): #**
        input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = all_iso3166_updates
    #else set input alpha2 codes to inputted and use corresponding updates data
    else:
        input_alpha2_codes = alpha2_code
        input_data = iso3166_updates
    
    #correct column order
    reordered_columns = ['Date Issued', 'Edition/Newsletter', 'Code/Subdivision change', 'Description of change in newsletter']

    #use temp object to get updates data either for specific country/alpha2 code or for all
    #countries, dependant on input_alpha2_codes and input_data vars above
    if (year != [] and months == []):
        for code in input_alpha2_codes:
            temp_iso3166_updates[code] = []
            for update in range(0, len(input_data[code])):
                #reorder dict columns
                input_data[code][update] = {col: input_data[code][update][col] for col in reordered_columns}
               
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
            
            #if current alpha2 has no rows for selected year/year range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)

    #if months parameter input then get updates within this months range, param must be 2 digits
    elif ((months != []) and (bool(re.match(r"[0-9][0-9]$", str(months))))):
        for code in input_alpha2_codes:
            temp_iso3166_updates[code] = [] 
            for update in range(0, len(input_data[code])):
                #reorder dict columns
                input_data[code][update] = {col: input_data[code][update][col] for col in reordered_columns}
                
                #convert date in Date Issued column to date object
                row_date = (datetime.strptime(input_data[code][update]["Date Issued"], "%Y-%m-%d"))
                
                #calculate difference in dates
                date_diff = relativedelta.relativedelta(current_datetime, row_date)
                
                #calculate months difference
                diff_months = date_diff.months + (date_diff.years * 12)
                
                #if current updates row is <= month input param then add to temp object
                if (diff_months <= months):
                    temp_iso3166_updates[code].append(input_data[code][update])
   
            #if current alpha2 has no rows for selected month range, remove from temp object
            if (temp_iso3166_updates[code] == []):
                temp_iso3166_updates.pop(code, None)
    else:
        temp_iso3166_updates = input_data #return updates data when Years and Month params are empty
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates)
    # return render_template('api.html', string=iso3166_updates)

if __name__ == '__main__':
    app.run(debug=True)