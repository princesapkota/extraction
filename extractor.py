from pyquery import PyQuery as pq
import json
import glob
import re

def extract_voters_data(html_file, json_file):
    """
    Extracts voter data from an HTML file and saves it to a JSON file.
    
    Args:
        html_file (str): The path to the HTML file.
        json_file (str): The path to the output JSON file.
    """
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        doc = pq(html_content)
        voters_data = []
        
        
        
        # Find the table within the div with class 'div_bbvrs_data'
        table = doc('div.div_bbvrs_data table.bbvrs_data')
        
        # Extract data from each row in the table body
        for row in table('tbody tr'):
            cells = [pq(td).text() for td in pq(row)('td')]
            if len(cells) == 8:
                voter_info = {
                    "voter_id": cells[1],
                    "name": cells[2],
                    "age": cells[3],
                    "gender": cells[4],
                    "spouse_name": cells[5],
                    "parents_name": cells[6],
                }
                voters_data.append(voter_info)

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(voters_data, f, ensure_ascii=False, indent=4)

        print(f"Successfully extracted data from {html_file} and saved to {json_file}")

    except FileNotFoundError:
        print(f"Error: The file {html_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == '__main__':
    # CHANGE 1: ADDED - Load election_data_full.json for location name mapping
    # This loads the full election data to get human-readable names for location IDs
    try:
        with open('election_data_full.json', 'r', encoding='utf-8') as f:
            election_data_full = json.load(f)
        print(f"Loaded {len(election_data_full)} records from election_data_full.json")
    except FileNotFoundError:
        print("Warning: election_data_full.json not found. Proceeding without location names.")
        election_data_full = []

    # ADDED: Load the location mapping from getlistofvoters.py
    with open('location_mapping.json', 'r') as f:
        location_data = json.load(f)
    
    # ADDED: Get all HTML files and process them
    html_files = glob.glob('*.html')
    all_voters_data = []
    
    for html_file in html_files:
        print(f"Processing {html_file}...")
        
        # ADDED: Get record number from filename to match with location data
        match = re.search(r'record_(\d+)\.html', html_file)
        record_num = int(match.group(1)) if match else 1
        
        # ADDED: Get the corresponding location info
        if record_num <= len(location_data):
            location_info = location_data[record_num - 1]  # Convert to 0-based index
            location = {
                "state": location_info["state"],
                "district": location_info["district"],
                "vdc": location_info["vdc_mun"],
                "ward": location_info["ward"],
                "reg": location_info["reg_centre"]
            }
            
            # CHANGE 2: ADDED - Find matching record in election_data_full.json and add location names
            # This matches the location IDs with the full data to get human-readable names
            #mapping logic ->
            if election_data_full:
                for full_record in election_data_full:
                    # Match all location IDs (convert to string for comparison)
                    if (str(full_record.get('state', '')) == str(location['state']) and
                        str(full_record.get('district', '')) == str(location['district']) and
                        str(full_record.get('vdc', '')) == str(location['vdc']) and
                        str(full_record.get('ward', '')) == str(location['ward']) and
                        str(full_record.get('reg', '')) == str(location['reg'])):
                        
                        # Add the name fields from the matching record
                        location['state_name'] = full_record.get('state_name', '')
                        location['district_name'] = full_record.get('district_name', '')
                        location['vdc_name'] = full_record.get('vdc_name', '')
                        location['ward_name'] = full_record.get('ward_name', location['ward'])  # Fallback to ward number
                        location['reg_name'] = full_record.get('reg_name', '')
                        break  # Stop searching once we find a match
        else:
            location = {}
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            doc = pq(html_content)
            
            
            # Find the table within the div with class 'div_bbvrs_data'
            table = doc('div.div_bbvrs_data table.bbvrs_data')
            
            # Extract data from each row in the table body
            for row in table('tbody tr'):
                cells = [pq(td).text() for td in pq(row)('td')]
                if len(cells) == 8:
                    voter_info = {
                        "voter_id": cells[1],
                        "name": cells[2],
                        "age": cells[3],
                        "gender": cells[4],
                        "spouse_name": cells[5],
                        "parents_name": cells[6],
                    }
                    
                    # ADDED: Add the location data to each voter
                    # CHANGE 3: NO MODIFICATION NEEDED HERE - This line now automatically includes both IDs and names
                    # because we enhanced the 'location' dictionary above to include name fields
                    voter_info.update(location)
                    
                    all_voters_data.append(voter_info)
            
        except FileNotFoundError:
            print(f"Error: The file {html_file} was not found.")
        except Exception as e:
            print(f"An error occurred processing {html_file}: {e}")
    
    # ADDED: Save all data to single JSON file
    with open('voters_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_voters_data, f, ensure_ascii=False, indent=4)
    
    print(f"Total voters extracted: {len(all_voters_data)}")
    print("All data saved to voters_data.json")
