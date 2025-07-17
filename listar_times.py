import os
import requests
from dotenv import load_dotenv

load_dotenv()

organization = os.getenv("AZURE_DEVOPS_ORGANIZATION")
project = os.getenv("AZURE_DEVOPS_PROJECT")
pat = os.getenv("AZURE_DEVOPS_PAT")
base_url = "https://dev.azure.com"

url = f"{base_url}/{organization}/_apis/projects/{project}/teams?api-version=5.0"
headers = {
    "Authorization": f"Basic {requests.auth._basic_auth_str('', pat).split(' ')[1]}",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)
print("Times disponíveis para o projeto:")
for team in response.json().get("value", []):
    print("-", team["name"]) 