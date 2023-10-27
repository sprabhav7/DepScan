import importlib
import importlib.metadata
import requests
from bs4 import BeautifulSoup


class PythonAnalyzer:
	def __init__(self, online_package_metadata):
		print('Initialized Python Analyzer...')
		self.online_package_metadata = online_package_metadata

	def validate_name(self):
		if self.online_package_metadata["info"]["name"] is None or self.online_package_metadata["info"]["name"] == "":
			return "error"
		else:
			return self.online_package_metadata["info"]["name"]

	def analyze(self):
		results = {
		"name": self.validate_name()
		}
		for key, value in results.items():
			if value == "error":
				return f'{key} has no value, please check package'
				
		return results

class AnalysisBuilder:
    def __init__(self, language):
        self.language = language

    def analyze(self, online_package_metadata):
        if self.language == "Python":
        	analyzer = PythonAnalyzer(online_package_metadata)
        else:
        	print('In development...')
        	exit(1)
        return analyzer.analyze()

class MetadataAnalyzer:
	def MetadataAnalyzer(online_package_metadata, language="Python"):
		analysis_builder = AnalysisBuilder(language)
		return analysis_builder.analyze(online_package_metadata)
