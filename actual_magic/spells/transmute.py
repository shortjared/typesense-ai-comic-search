import os
import sys
import argparse
from openai import OpenAI
import json

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def read_file(file_path, output_file_path):
    """Function to read the content of a JSON file and write analysis results to an output file."""
    try:
        with open(file_path, 'r') as file:
            content = json.load(file)
            with open(output_file_path, 'w') as output_file:
                output_file.write("[\n")
                from concurrent.futures import ThreadPoolExecutor, as_completed
                from tqdm import tqdm

                def process_item(item):
                    analysis_result = analyze_image(item['url'])
                    analysis_result.update(item)
                    return analysis_result

                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(process_item, item) for item in content]
                    for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc="Processing items")):
                        result = future.result()
                        json.dump(result, output_file, indent=4)
                        if i < len(futures) - 1:
                            output_file.write(",\n")
                output_file.write("\n]")
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")

def analyze_image(image_url):
    """Function to send the image URL to OpenAI and get a description."""
    try:
        response = client.chat.completions.create(
            response_format={
                "type": "json_object"
            },
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant who analyzes web comic images and returns back a json object.
                                  All content in your response should help provide a useful searchable archive.
                                  The properties required in the json object are:
                                      - description_environment: A string description of the environment in the image.
                                      - description_happening: A string description of what is happening in the image.
                                      - description_humor: A string. A description of the humor in the image.
                                      - caption: A string of the direct text in the image. If there are multiple lines or sections, separate them with a semicolon.
                                      - tags: An array of strings. Categories that the image fits into for useful faceted search. Assume a tech oriented audeience, so avoid overly broad categories like "technology", "comic" or "humor".
                                      - suggested_alt_text: A string of the suggested alt text for the image to make it useful for screen readers to communicate the humor and content of the image to visually impaired users.
                            """,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            model="gpt-4o",
        )

        result = response.choices[0].message.content
        if result is not None:
            return json.loads(result)
        else:
            return {}
    except Exception as e:
        print(f"An error occurred while analyzing the image: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="CLI to read a JSON file and output analysis results")
    parser.add_argument('file_path', type=str, help="JSON file path")
    parser.add_argument('output_file_path', type=str, help="Output JSON file path")

    args = parser.parse_args()
    file_path = args.file_path
    output_file_path = args.output_file_path
    read_file(file_path, output_file_path)

if __name__ == "__main__":
    main()
