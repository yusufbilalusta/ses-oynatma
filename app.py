from flask import Flask, request, jsonify, send_file, render_template_string
import os
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
latest_audio = None
latest_audio_timestamp = None  # Track the timestamp of the latest audio file

@app.route('/')
def index():
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Audio Player</title>
    </head>
    <body>
        <h1>Automatic Audio Player</h1>
        <audio id="audioPlayer" controls></audio>

        <script>
            let lastPlayedTimestamp = null;

            async function fetchAndPlayAudio() {
                try {
                    const response = await fetch("/get-latest-audio");
                    const data = await response.json();

                    // Check if a new audio file is available
                    if (response.ok && data.timestamp !== lastPlayedTimestamp) {
                        lastPlayedTimestamp = data.timestamp;

                        // Fetch the audio blob if timestamp has changed
                        const audioBlobResponse = await fetch("/play-audio");
                        const audioBlob = await audioBlobResponse.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        const audioPlayer = document.getElementById("audioPlayer");

                        audioPlayer.src = audioUrl;
                        audioPlayer.play();
                    }
                } catch (error) {
                    console.error("Error fetching audio:", error);
                }
            }

            // Check for new audio every 5 seconds
            setInterval(fetchAndPlayAudio, 5000);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/upload', methods=['POST'])
def receive_and_store_audio():
    global latest_audio, latest_audio_timestamp
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the audio file to "uploads" directory
    audio_path = os.path.join(UPLOAD_FOLDER, "output.wav")
    file.save(audio_path)
    
    latest_audio = audio_path
    latest_audio_timestamp = time.time()  # Update the timestamp to the current time
    
    return jsonify({'message': 'Audio uploaded successfully'}), 200

@app.route('/get-latest-audio', methods=['GET'])
def get_latest_audio():
    # Send the latest timestamp to the frontend
    if latest_audio and latest_audio_timestamp:
        return jsonify({'timestamp': latest_audio_timestamp})
    return jsonify({'error': 'No audio file available'}), 404

@app.route('/play-audio', methods=['GET'])
def play_audio():
    # Serve the actual audio file
    if latest_audio and os.path.exists(latest_audio):
        return send_file(latest_audio, mimetype="audio/wav")
    return jsonify({'error': 'No audio file available'}), 404

if __name__ == '__main__':
    app.run(port=4000)
