from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from flask_cors import CORS
import youtube_dl
import os
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

app = Flask(__name__)
CORS(app)

DEEPGRAM_API_KEY = "YOUR_API_KEY"
AUDIO_DIR = 'downloads'
STATIC_DIR = 'static'

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory(STATIC_DIR, path)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data['url']
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(AUDIO_DIR, '%(title)s.%(ext)s'),
        'nocheckcertificate': True,
    }
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(result).replace('.m4a', '.mp3')

        return jsonify({'audio_file': audio_file, 'title': result['title'], 'url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    data = request.json
    audio_file = data['audio_file']
    
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        with open(audio_file, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']

        return jsonify({'transcript': transcript})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloaded/<filename>')
def downloaded_file(filename):
    return send_file(os.path.join(AUDIO_DIR, filename))

if __name__ == '__main__':
    app.run(debug=True)
