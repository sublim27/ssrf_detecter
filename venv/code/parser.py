import os
import json
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def fetch_and_parse_links(url, base_url, json_file):
    tags_and_attributes = {
        'a': 'href',
        'link': 'href',
        'img': 'src',
        'script': 'src',
        'iframe': 'src',
        'form': 'action'
    }

    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract child links
            child_links = []
            for tag, attribute in tags_and_attributes.items():
                for element in soup.find_all(tag, attrs={attribute: True}):
                    href = element.get(attribute)
                    full_url = urljoin(base_url, href)
                    if full_url.startswith("http"):
                        child_links.append(full_url)

            # Load or initialize the JSON file
            link_tree = load_or_init_json(json_file)

            # Check if the URL already exists in the tree
            if url not in link_tree:
                # If not, add it as a new node
                parsed_url = urlparse(url)
                link_tree[url] = {
                    "path": parsed_url.path,
                    "visited": True,
                    "children": {}
                }

            # Add child links to the existing or newly created node
            link_tree[url]["visited"]=False
            for child in child_links:
                if child not in link_tree[url]["children"]:
                    link_tree[url]["children"][child] = {
                        "path": urlparse(child).path,
                        "visited": False,
                        "children": {}
                    }

            # Save the updated tree to the JSON file
            save_to_json(json_file, link_tree)

        elif response.status_code == 403:
            print(f"Access denied (403 Forbidden) for URL: {url}")
        elif response.status_code == 404:
            print(f"Page not found (404 Not Found) for URL: {url}")
        elif response.status_code >= 400 and response.status_code < 500:
            print(f"Client error ({response.status_code}) for URL: {url}")
        elif response.status_code >= 500:
            print(f"Server error ({response.status_code}) for URL: {url}")
        else:
            print(f"Unexpected status code ({response.status_code}) for URL: {url}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")


def load_or_init_json(json_file):
    
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                # If the file is empty or invalid JSON, return an empty dictionary
                return {}
    else:
        # If the file does not exist, return an empty dictionary
        return {}


def save_to_json(json_file, data):
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Example usage