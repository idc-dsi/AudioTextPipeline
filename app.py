from flask import Flask, redirect, url_for, render_template, request, session, jsonify, Response
from flask_oauthlib.client import OAuth
from flask_cors import CORS
from flask_compress import Compress
from dataclasses import dataclass
import os
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
from urllib.parse import unquote
from werkzeug.middleware.proxy_fix import ProxyFix
from static.py.video_indexer import VideoIndexer  # Importing the VideoIndexer class
import requests
import jwt
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer



# Flask App Initialization
app = Flask(__name__)
Compress(app)
app.secret_key = 'My_Secret_Key'  # Replace with your actual secret key
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
CORS(app)

# Load model and tokenizer (change to ours once its ready and uploaded to huggingface)
tokenizer = AutoTokenizer.from_pretrained("moussaKam/AraBART")
model = AutoModelForSeq2SeqLM.from_pretrained("moussaKam/AraBART")

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
    return azure.authorize(callback=callback_url)
    #Localhost
    #return azure.authorize(url_for('authorized', _external=True))

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
    return redirect(callback_url)
    
    ##for local host
    #return redirect(url_for('index', logged_in=True))

@app.route('/translate', methods=['POST'])
def translate():
    # Get the text from the request body
    data = request.get_json()
    text = data.get('text')

    # Prepare the text for the model
    inputs = tokenizer(text, return_tensors="pt")

    # Process the text with the model using specific translation settings
    ## will need to deal with the max length according to the actual model we will use, we might need to break the text into smaller chunks for the max length and for the computation cost sakes.
    generated_ids = model.generate(**inputs, num_beams=4, max_length=1024)
    translated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

    # Return the translated text in JSON format
    return jsonify({'translated_text': translated_text})

 

#azure indexer api:
@app.route('/upload', methods=['POST'])
def handle_upload():
    video_file = request.files['file']
    try:
        indexer = VideoIndexer(
            subscription_key="6dd8d30a65eb4004922e6e74a8fb313f",
            account_id="54f05c12-3476-43f4-96a7-3c80439ecb5c",
            location="westeurope"
        )

        video_id = indexer.upload_video_and_get_indexed(video_file)
        return {'message': 'Video uploaded and processing started', 'videoId': video_id}, 200
    
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


@app.route('/results/<video_id>', methods=['GET'])
def get_results(video_id):
    indexer = VideoIndexer(
        subscription_key="6dd8d30a65eb4004922e6e74a8fb313f",
        account_id="54f05c12-3476-43f4-96a7-3c80439ecb5c",
        location="westeurope"
    )

    try:
        results = indexer.get_video_index(video_id)
        return results, 200
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500
    

@azure.tokengetter
def get_azure_oauth_token():
    return session.get('azure_token')

# Main Entry Point
if __name__ == '__main__':
    app.run(debug=True)