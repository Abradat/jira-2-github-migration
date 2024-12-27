from config_reader import load_config
from transformer import load_username_mapping, transform_csv_to_json, save_json, save_to_db

# Load configurations
config = load_config("config.json")

# Extract configurations
input_csv = config["input_csv_file"]
output_json = config["output_json_file"]
db_file = config["database"]
username_mapping_file = config["j2g_json_file"]

# Load username mapping
username_mapping = load_username_mapping(username_mapping_file)

# Transform CSV to JSON
json_objects = transform_csv_to_json(input_csv, username_mapping)

# Save JSON to file
save_json(json_objects, output_json)

# Save data to database
save_to_db(json_objects, db_file)

print(f"JSON data saved to {output_json}")
print(f"Data saved to database {db_file}")