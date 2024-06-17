import os
import json
from pymongo import MongoClient


def remove_dot_from_keys(d):
    new_dict = {}
    for key, value in d.items():
        # Remove the trailing dot from the key if it exists
        new_key = key[:-1] if key.endswith(".") else key
        new_key = new_key.replace("/", " ")

        # Recursively process nested dictionaries
        if isinstance(value, dict):
            value = remove_dot_from_keys(value)

        # Assign the possibly modified value to the possibly modified key
        new_dict[new_key] = value

    return new_dict


def load_json_files_to_mongodb(
    folder_path, db_name, collection_name, mongo_uri="mongodb://localhost:27017"
):
    """
    Load JSON files from a folder into a MongoDB collection.

    :param folder_path: Path to the folder containing JSON files.
    :param db_name: Name of the MongoDB database.
    :param collection_name: Name of the MongoDB collection.
    :param mongo_uri: MongoDB URI for connecting to the database.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Iterate over every file in the directory specified
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                data = remove_dot_from_keys(data)
                collection.insert_one(data)
                print(f"Inserted document from {filename}")

    print("All JSON files have been inserted into the database.")


if __name__ == "__main__":
    # Specify the folder containing JSON files
    folder_path = "stukken"  # Update this path
    db_name = "dekamer"  # Update with your database name
    collection_name = "kamerstukken3"  # Update with your collection name

    load_json_files_to_mongodb(folder_path, db_name, collection_name)
