import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json


class GeminiChat:

    error = lambda self, error_name: {"status": "error", "details": error_name}
    success = lambda self, data: {"status": "success", "data": data}
    response_mime_type = "application/json"


    def __init__(self, api_key, system_instruction, model_name, max_output_tokens, temperature, input_words_limit):
        genai.configure(api_key=api_key)
        self.url = f"https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta&key={api_key}"

        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                response_mime_type=self.response_mime_type
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            },
            system_instruction=system_instruction
        )
        self.input_words_limit = input_words_limit
        self.is_started = False


    def start(self):
        self.chat = self.model.start_chat(history=[])
        self.is_started = True


    def __call__(self, message):
        response = self.chat.send_message(message)
        text = response.text.replace("  ", " ")
        json_response = json.loads(text)
        return self.success(json_response)