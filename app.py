from flask import Flask, redirect, url_for, render_template, request, session, jsonify, Response
from flask_oauthlib.client import OAuth
from flask_cors import CORS
from flask_compress import Compress
import os
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
from urllib.parse import unquote
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import jwt
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer



# Flask App Initialization
app = Flask(__name__)
Compress(app)
app.secret_key = 'My_Secret_Key'  # Replace with your actual secret key
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
CORS(app)


# OAuth Setup
oauth = OAuth(app)
azure = oauth.remote_app(
    'azure',
    consumer_key='e87d91e8-ab56-45aa-9346-e20b076f61e1',  # Replace with your Azure AD Application ID
    consumer_secret='EhC8Q~f1NluYkO7ef_IvW3pEHqsEkQ_qwPUh0cnY',  # Replace with your Azure AD Client Secret
    request_token_params={'scope': 'openid email profile'},
    base_url='https://graph.microsoft.com/v1.0/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://login.microsoftonline.com/bd717aa1-6670-4ce3-ba94-ef01de50c477/oauth2/v2.0/token',  # Replace TENANT_ID
    authorize_url='https://login.microsoftonline.com/bd717aa1-6670-4ce3-ba94-ef01de50c477/oauth2/v2.0/authorize'  # Replace TENANT_ID
)


# Azure Blob Storage Setup
storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'podcastscoref')
storage_account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', 'mYdJ0JI2YBZKj56B1u33/xYwsN3LbpyM6jYum+PxClFSlPs2kqsHZFP+5R8RFE9yfOGBSk4E93mr+AStqo/S9w==')

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=storage_account_key)



@app.route('/')
def index():
    anonymous = request.args.get('anonymous', 0)
    logged_in = session.get('logged_in', False)
    return render_template('index.html', anonymous=anonymous,logged_in=logged_in)

@app.route('/login')
def login():
    callback_url = url_for('authorized', _external=True, _scheme='https')
    #return azure.authorize(callback=callback_url)
    #Localhost
    return azure.authorize(url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    response = azure.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access Denied: Reason=%s\nError=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['azure_token'] = (response['access_token'], '')
    
    id_token = response.get('id_token')
    if id_token:
        # Decode the ID token
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})

        # Extract the 'name'
        user_name = decoded_token.get('name')
        if user_name:
            session['username'] = user_name
            #print("User Name:", user_name)
        
    # Set a session variable to indicate the user is logged in
    #for azure 
    callback_url = url_for('index', logged_in=True, _scheme='https')
    #return redirect(callback_url)
    
    #for local host
    return redirect(url_for('index', logged_in=True))
 
@azure.tokengetter
def get_azure_oauth_token():
    return session.get('azure_token')


# # Load model and tokenizer
# # Assuming 'my_model_directory' is directly under 'C:\Users\guyma\Desktop\LAB\Seq2seq'
# model_directory = os.path.abspath('./my_model_directory')
# # Load model and tokenizer using the absolute path
# model = AutoModelForSeq2SeqLM.from_pretrained(model_directory)
# tokenizer = AutoTokenizer.from_pretrained(model_directory)

# @app.route('/api/translate', methods=['POST'])
# def translate_text():
#     input_data = request.json
#     inputs = tokenizer.encode(input_data["text"], return_tensors="pt")
#     outputs = model.generate(inputs)
#     translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return jsonify(translated_text=translated_text)



# #template : 

# # Replace with your account information
# account_id = "YOUR_ACCOUNT_ID"
# access_token = "YOUR_ACCESS_TOKEN"

# def upload_video_and_get_transcript(video_filepath):
#   """
#   This function uploads a video file to the Azure AI Video Indexer API
#   and retrieves the transcribed text with identified speakers.

#   Args:
#       video_filepath: The path to the video file on your local system.

#   Returns:
#       A dictionary containing the transcript text and speaker information,
#       or None if there's an error.
#   """

#   # Prepare the request headers
#   headers = {
#       "Authorization": f"Bearer {access_token}"
#   }

#   # Open the video file in binary mode
#   with open(video_filepath, "rb") as video_file:
#       video_data = video_file.read()

#   # Set request URL based on your region (replace if necessary)
#   url = "https://api.videoindexer.ai/videos"

#   # Prepare the multipart form data for video upload
#   form_data = {
#       "video": (os.path.basename(video_filepath), video_data, "video/mp4")  # Adjust content type if needed
#   }

#   try:
#       response = requests.post(url, headers=headers, files=form_data)
#       response.raise_for_status()  # Raise an exception for non-200 status codes
#   except requests.exceptions.RequestException as e:
#       print(f"Error uploading video: {e}")
#       return None

#   # Parse the response to get transcript and speaker information (same as before)
#   # ... (refer to previous code for parsing logic)

#   return transcript

# Main Entry Point
if __name__ == '__main__':
    app.run(debug=True)