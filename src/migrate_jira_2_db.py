from config_reader import load_config
from transformer import transform_csv_to_json, save_to_db

# Load configurations
config = load_config("../config.json")

# Extract configurations
input_csv =  '../' + config["input_csv_file"]
db_file = '../' + config["database"]

# Transform CSV to JSON
json_objects = transform_csv_to_json(input_csv, config)

# Save data to database
save_to_db(json_objects, db_file)

print(f"Data saved to database {db_file}")