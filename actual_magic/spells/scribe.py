import json
import os
import sys
import typesense

def create_typesense_client():
    return typesense.Client({
        'nodes': [{
            'host': 'localhost',
            'port': '8108',
            'protocol': 'http'
        }],
        'api_key': os.getenv('TYPESENSE_API_KEY'),
        'connection_timeout_seconds': 2
    })

def read_json_file(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def write_to_typesense(json_data, client, collection_name):
    try:
        client.collections[collection_name].delete()
    except Exception as e:
        print(f"Collection '{collection_name}' does not exist. Creating a new one.")

    # Assuming the first item in the JSON data to infer the schema
    document_example = json_data[0]
    schema = {
        'name': collection_name,
        'fields': [{'name': key, 'type': 'auto'} for key in document_example.keys()]
    }

    client.collections.create(schema)

    for document in json_data:
        client.collections[collection_name].documents.create(document)

def main():
    if len(sys.argv) != 3:
        print("Usage: poetry run scribe <json-file-path> <collection-name>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    collection_name = sys.argv[2]

    client = create_typesense_client()
    json_data = read_json_file(json_file_path)
    write_to_typesense(json_data, client, collection_name)
    print(f"Data written to Typesense collection '{collection_name}' successfully.")

if __name__ == "__main__":
    main()
