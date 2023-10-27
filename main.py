import importlib
import importlib.metadata
import requests
from metadata_validator import MetadataAnalyzer
from metadata_parser import MetadataInfo
from bs4 import BeautifulSoup

'''
def fetch_package_metadata(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    response.raise_for_status()

    metadata = response.json()
    return metadata


def parse_package_metadata(metadata):
    parsed_metadata = {}

    """
    keys = []
    for key in metadata["last_serial"]:
    	keys.append(key)
    """

    print(metadata["last_serial"])
    return metadata


def is_package_installed(package_name):
    try:
        importlib.import_module(package_name)
        return True
    except ModuleNotFoundError:
        return False


def get_package_metadata(package_name):
    if not is_package_installed(package_name):
        return None

    metadata = importlib.metadata.metadata(package_name)
    return metadata


def fetch_npm_package_metadata(package_name):
    """
    Fetches package metadata from the npm repository.

    Args:
      package_name: The name of the package to fetch metadata for.

    Returns:
      A dictionary containing the package metadata, or None if the package is not found.
    """

    response = requests.get(f"https://registry.npmjs.org/{package_name}")
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        return None
'''

if __name__ == "__main__":
    # TODO - Parse file, get repo type
    repo = input("Enter the repository name:")
    package_name = input("Enter the package name: ")

    metadata = MetadataInfo.IsPackageInstalled(package_name,repo)
    print(metadata)
    exit(1)
    parsed_metadata = parse_package_metadata(metadata)

    # call metadata analysis here

    is_installed = is_package_installed(package_name)
    if is_installed:
        context_metadata = get_package_metadata(package_name)
        print("Successfully fetched local copy and remote copy...")
        print(context_metadata)
        # call attack analysis with context_metadata
    else:
        print(
            f"The package {package_name} is not installed. Reverting back to popularity metrics..."
        )
        # call attack analysis with nonetype
        res = analyze_package_metadata(metadata, "Python")
        print(res)
