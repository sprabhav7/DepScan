import importlib
import importlib.metadata
import requests
import pkg_resources
from bs4 import BeautifulSoup
from PythonMetadataAnalyzer import PythonMetadataAnalyzer
from NpmMetadataAnalyzer import NpmMetadataAnalyzer

repo_list = {
1: 'GEMS_REPO',
2: 'NPM_REPO',
3: 'PYTHON_REPO'
}

class AnalysisBuilder:
    def __init__(self, repo):
        self.repo = repo_list[repo]

    def analyze(self, remote_metadata, local_metadata):
        if self.repo == 'PYTHON_REPO':
        	analyzer = PythonMetadataAnalyzer(remote_metadata, local_metadata)
        elif self.repo == 'NPM_REPO':
        	analyzer = NpmMetadataAnalyzer(remote_metadata, local_metadata)
        else:
        	print('In development...')
        	exit(1)
        return analyzer.analyze()

class MetadataAnalyzer:
	def Analyzer(remote_metadata, local_metadata,repo):
		analysis_builder = AnalysisBuilder(repo)
		return analysis_builder.analyze(remote_metadata, local_metadata)
