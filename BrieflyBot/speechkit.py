import json
import requests


class SpeechKit:

    voices = json.load(open("modules/voices.json"))

    def __init__(
        self, elevenlabs_api_key, voice="Charlie", model="eleven_multilingual_v2"
    ):
        # elevenlabs text to speech
        self.model = model
        self.tts_url = (
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voices[voice]}/stream"
        )
        self.tts_headers = {
            "Accept": "application/json",
            "xi-api-key": elevenlabs_api_key,
        }

    def text_to_speech(self, text):
        data = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }
        response = requests.post(
            self.tts_url, headers=self.tts_headers, json=data, stream=True
        )

        if response.status_code != 200:
            print(response.text)
            return None

        audio = b""
        for chunk in response.iter_content(chunk_size=None):
            audio += chunk

        return audio
