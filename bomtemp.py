import json

def print_license_values(data):
    """
    Recursively search for and print the value of any key named 'license' in a JSON-like data structure.
    """
    if isinstance(data, dict):  # If the item is a dictionary
        for key, value in data.items():
            if key == 'license':
                for k, v in value.items():
                    if k == 'id':
                        print(v)
            print_license_values(value)  # Recurse into the value
    elif isinstance(data, list):  # If the item is a list
        for item in data:
            print_license_values(item)  # Recurse into each item

def read_json_and_find_license(json_file):
    """
    Read JSON data from a file and search for 'license' keys.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)  # Load JSON data from the file
        print_license_values(data)  # Call the recursive function on the loaded data

# Path to your JSON file
json_file_path = r"C:\Users\wston\Desktop\Purdue\SeniorDesign\kaleidoscope\kaleidoscope.bom"

# Run the function
read_json_and_find_license(json_file_path)
