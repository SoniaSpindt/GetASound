import requests
import boto3
from flask import Flask, escape, request
from flask import jsonify, send_from_directory
from io import StringIO, BytesIO
import uuid

BUCKETNAME='sound-files-apcsp'
app = Flask(__name__, static_url_path='/static')
s3 = boto3.client('s3')

@app.route('/handle', methods=['POST'])
def handle():
    print('fetching', request.form['url'])
    try:
        url = request.form.get('url')
        if url:
            content = requests.get(request.form['url'])
            sound = BytesIO(content.content)
            sound.seek(0)
            soundname = request.form['url'].split('/')[-1]
        elif 'file' in request.files:
            sound = request.files['file']
            soundname = sound.filename
            
        extension = soundname.split('.')[-1]
        print(f"uploading file {soundname} to s3")
        soundname = str(uuid.uuid4())+'.'+extension
        resp = s3.upload_fileobj(sound, BUCKETNAME, soundname, ExtraArgs={'ACL':'public-read'})
        url = f'https://{BUCKETNAME}.s3-us-west-1.amazonaws.com/{soundname}'
        return jsonify({'url': url})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@app.route('/')
def home():
    print('home')
    return send_from_directory('static', 'index.html')

if __name__=='__main__':
    app.run(host='0.0.0.0',debug=False, threaded=False)
