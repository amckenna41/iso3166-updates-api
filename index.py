from flask import Flask, request, render_template, jsonify
from google.cloud import storage
from google.oauth2 import service_account
from googleapiclient import discovery
import requests
import json 
import iso3166
import re
import os
import logging
import getpass
from datetime import datetime
from dateutil import relativedelta

#initialise Flask app
app = Flask(__name__)

#initialise logging library 
__version__ = "1.1.0"
log = logging.getLogger(__name__)

#initalise User-agent header for requests library 
USER_AGENT_HEADER = {'User-Agent': 'iso3166-updates/{} ({}; {})'.format(__version__,
                                       'https://github.com/amckenna41/iso3166-updates', getpass.getuser())}

#get Cloud Storage specific env vars
sa_json_str = os.environ["SA_JSON"]
project_id = os.environ["PROJECT_ID"]
bucket_name = os.environ["BUCKET"]
blob_name = os.environ["BLOB"]

#convert str of service account from env var into json 
sa_json = json.loads(sa_json_str)
#pass service account json into credentials object
credentials = service_account.Credentials.from_service_account_info(sa_json)
#create GCP Storage client using credentials
storage_client = storage.Client(project=project_id, credentials=credentials)
#initialise bucket object
bucket = storage_client.bucket(bucket_name)
#get path to json blob in bucket
blob_path = "gs://" + bucket_name + "/" + blob_name

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
    """
    #load json from blob on bucket
    all_iso3166_updates = json.loads(storage.Blob.from_string(blob_path, client=storage_client).download_as_text())
    
    return render_template('index.html', string=all_iso3166_updates)

@app.route('/api', methods=['GET'])
def api():
    """
    Main route for API (https://iso3166-updates.com/api) that can accept the alpha-2, 
    year and months query string parameters and return the relevant ISO3166 updates.
    The API uses a pre-created json with all the latest updates stored in a GCP Cloud
    Storage bucket, the object is imported in after authentication and used as the
    basis of the API.  

    Parameters
    ----------
    None

    Returns 
    -------
    :iso3166_updates : json
      jsonified response of iso3166 updates.
    :status_code : int
        response status code.
    """
    #initialise vars
    iso3166_updates = {}
    alpha2_code = []
    year_range = False
    greater_than = False
    less_than = False
    year = []
    months = []

    #json object storing the error message and status code 
    error_message = {}
    error_message["status"] = 400

    #load json from blob on bucket
    all_iso3166_updates = json.loads(storage.Blob.from_string(blob_path, client=storage_client).download_as_text())

    #get current datetime object
    current_datetime = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")

    #parse alpha-2 code parameter
    if not (request.args.get('alpha2') is None):
        alpha2_code = sorted([request.args.get('alpha2').upper()])
    
    #parse year parameter
    if not (request.args.get('year') is None):
        year = [request.args.get('year').upper()]

    #parse months parameter, return error message if invalid input
    if not (request.args.get('months') is None):
        try:
            months = int(request.args.get('months'))
        except:
            error_message["message"] = f"Invalid month input: {''.join(request.args.get('months'))}"
            return jsonify(error_message), 400

    #if no input parameters set then return all country update iso3166_updates
    if (year == [] and alpha2_code == [] and months == []):
        return (jsonify(all_iso3166_updates), 200)
    
    def convert_to_alpha2(alpha3_code):
        """ 
        Convert an ISO3166 country's 3 letter alpha-3 code into its 2 letter
        alpha-2 counterpart. 

        Parameters 
        ----------
        :alpha3_code: str
            3 letter ISO3166 country code.
        
        Returns
        -------
        :iso3166.countries_by_alpha3[alpha3_code].alpha2: str
            2 letter ISO3166 country code. 
        """
        #return error if 3 letter alpha-3 code not found
        if not (alpha3_code in list(iso3166.countries_by_alpha3.keys())):
            return None
        else:
            #use iso3166 package to find corresponding alpha-2 code from its alpha-3
            return iso3166.countries_by_alpha3[alpha3_code].alpha2

    #validate multiple alpha-2 codes input, remove any invalid ones
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
                        error_message["message"] = f"Invalid 3 letter alpha-3 code input: {''.join(alpha2_code[code])}"
                        return jsonify(error_message), 400
                    alpha2_code[code] = temp_code
                #use regex to validate format of alpha-2 codes
                if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[code]))) or (alpha2_code[code] not in list(iso3166.countries_by_alpha2.keys())):
                    alpha2_code.remove(alpha2_code[code])
        else:
            #api can accept 3 letter alpha-3 code for country, this has to be converted into its alpha-2 counterpart
            if (len(alpha2_code[0]) == 3):
                temp_code = convert_to_alpha2(alpha2_code[0])
                #return error message if invalid alpha-3 code input
                if (temp_code is None):
                    error_message["message"] = f"Invalid 3 letter alpha-3 code input: {''.join(alpha2_code[0])}"
                    return jsonify(error_message), 400
                alpha2_code[0] = temp_code
            #if single alpha-2 code passed in, validate its correctness
            if not (bool(re.match(r"^[A-Z]{2}$", alpha2_code[0]))) or \
                (alpha2_code[0] not in list(iso3166.countries_by_alpha2.keys()) and \
                alpha2_code[0] not in list(iso3166.countries_by_alpha3.keys())):
                error_message["message"] = f"Invalid 2 letter alpha-2 code input: {''.join(alpha2_code)}"
                return jsonify(error_message), 400

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
            return jsonify(error_message), 400

    #get updates from iso3166_updates object per country using alpha-2 code
    if (alpha2_code == [] and year == [] and months == []):
        iso3166_updates = all_iso3166_updates
    else:
        for code in alpha2_code:
            iso3166_updates[code] = all_iso3166_updates[code]
    
    #temporary updates object
    temp_iso3166_updates = {}

    #if no valid alpha-2 codes input, use all alpha-2 codes from iso3166 and all updates data
    if ((year != [] and alpha2_code == [] and months == []) or \
        ((year == [] or year != []) and alpha2_code == [] and months != [])):
        input_alpha2_codes  = list(iso3166.countries_by_alpha2.keys())
        input_data = all_iso3166_updates
    #else set input alpha-2 codes to inputted and use corresponding updates data
    else:
        input_alpha2_codes = alpha2_code
        input_data = iso3166_updates
    
    #use temp object to get updates data either for specific country/alpha-2 code or for all
    #countries, dependant on input_alpha2_codes and input_data vars above
    if (year != [] and months == []):
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

    #if months parameter input then get updates within this months range
    elif (months != []):
        #return error if invalid month value input
        if not (str(months).isdigit()):
            error_message["message"] = f"Invalid month input: {''.join(months)}"
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
        temp_iso3166_updates = input_data #return updates data when Years and Month params are empty
    
    #set main updates dict to temp one
    iso3166_updates = temp_iso3166_updates

    return jsonify(iso3166_updates), 200

if __name__ == '__main__':
    app.run(debug=True)