async function downloadVideo() {
    const url = document.getElementById('youtube-url').value;
    if (!url) {
        alert("Please enter a YouTube URL");
        return;
    }

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (response.status !== 200) {
            throw new Error(data.error);
        }

        const videoContainer = document.getElementById('video-container');
        videoContainer.innerHTML = `<iframe width="100%" height="315" src="https://www.youtube.com/embed/${getYouTubeID(url)}" frameborder="0" allowfullscreen></iframe>`;
        
        const audioPlayer = document.getElementById('audio-player');
        audioPlayer.src = `/downloaded/${data.audio_file.split('/').pop()}`;
        
        transcribeAudio(data.audio_file);
    } catch (error) {
        showError(error.message);
    }
}

async function transcribeAudio(audioFile) {
    try {
        const response = await fetch('/transcribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audio_file: audioFile })
        });

        const data = await response.json();

        if (response.status !== 200) {
            throw new Error(data.error);
        }

        const transcriptionDiv = document.getElementById('transcription');
        transcriptionDiv.innerText = data.transcript;
    } catch (error) {
        showError(error.message);
    }
}

function getYouTubeID(url) {
    const regExp = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length == 11) ? match[2] : null;
}

function showError(message) {
    const errorPopup = document.createElement('div');
    errorPopup.className = 'error-popup';
    errorPopup.innerText = message;
    document.body.appendChild(errorPopup);

    setTimeout(() => {
        document.body.removeChild(errorPopup);
    }, 7500);
}
