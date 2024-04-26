# video_indexer.py

from dataclasses import dataclass
import requests

@dataclass
class VideoIndexer:
    subscription_key: str
    account_id: str
    location: str = "westeurope"

    def get_access_token(self):
        url = f"https://api.videoindexer.ai/{self.location}/Auth/{self.account_id}/AccessToken?allowEdit=true"
        headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['accessToken']

    def upload_video_and_get_indexed(self, video_file):
        access_token = self.get_access_token()
        headers = {'Content-Type': 'multipart/form-data'}
        params = {
            'accessToken': access_token,
            'name': video_file.filename,
            'privacy': 'Private',
            'description': 'Uploaded for indexing',
            'partition': 'none',
            'videoUrl': '',
            'streamingPreset': 'Default',
            'language': 'English',
            'indexingPreset': 'Default'
        }
        files = {'file': (video_file.filename, video_file, 'video/mp4')}
        upload_url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"
        response = requests.post(upload_url, headers=headers, params=params, files=files)
        response.raise_for_status()
        return response.json()['id']

    def get_video_index(self, video_id):
        access_token = self.get_access_token()
        url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos/{video_id}/Index?accessToken={access_token}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
