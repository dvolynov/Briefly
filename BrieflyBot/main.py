import io
import os
import re
import json
import datetime
import requests

import urllib.parse

import telebot
from telebot import types

from dotenv import load_dotenv
import configparser

from speechkit import SpeechKit


# load .env and config
load_dotenv()
config = configparser.ConfigParser()
config.read("config.ini")

# bot
bot = telebot.TeleBot(os.getenv("TOKEN"))

# server API
host = config.get("API", "host")
port = config.getint("API", "port")

SERVER_URL = f"http://{host}:{port}/api"


markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
markup.add(
    types.KeyboardButton("Recent News"),
    types.KeyboardButton("Menu"),
    types.KeyboardButton("Daily News"),
    types.KeyboardButton("Settings"),
)

cancel_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
cancel_markup.add(
    types.KeyboardButton("/cancel"),
)

setup_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
setup_markup.add(
    types.KeyboardButton("/setup"),
)

REPLY_MODES = {
    "text": 0,
    "voice": 1,
}


IS_SETUP = {}
ACTIVE_POLLS = {}
ACTIVE_SETUP_MESSAGES = {}
ACTIVE_SETTINGS_MESSAGES = {}

HELP_MESSAGE = f"""🗣️You can send me any content to summarize:

Formats
├ Link
├ Text, code or other file
├ Audio file
└ YouTube link (English Language)

When you send one of this formats, you can ask question directly to AI about the content using simple messages (e.g. What are the consequences of this event?)

🔥I can send you 2 types of news for given topics:

Formats
├ Recent (last 6 hours)
└ Daily news (last 24 hours)

⚙️Settings:
├ 📝Set specific text styles that will be applied to both news and summaries (e.g. bullet points, tweet)
├ 💡Set specific topics of news that you're interested in (e.g. Science, Culture)
└ 🎙Set a reply mode as text or audio"""


START_TEXT = f"""*Hello! I'm Briefly, revolutionizing your content experience!*

I’m here to help you get concise summaries of any content you need. Whether it's articles, documents, audio, YouTube videos, and more, I’ve got you covered!

- *Get daily* or recent news tailored to your interests
- *Customize* your experience to fit your needs

Ready to get started? Just press /setup 🚀"""


kit = SpeechKit(
    elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice=config.get("Elevenlabs", "voice"),
    model=config.get("Elevenlabs", "model"),
)


class User:

    def __init__(
        self, chat_id: int, first_name: str, last_name: str, username: str
    ) -> None:
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


class Settings:

    @classmethod
    def get_topics(cls, chat_id: int):
        response = requests.get(SERVER_URL + f"/topics")
        print(response)
        if response_wrapper(response, good_status_codes=[200], chat_id=chat_id):
            json_data = response.json()
            print(json_data)
            if json_data["topics"]:
                return json_data["topics"]

    @classmethod
    def get_topics_buttons(cls, show_cancel: bool = True) -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=2)
        if show_cancel:
            markup.add(
                types.InlineKeyboardButton(
                    "Cancel",
                    callback_data=f"cancel",
                ),
            )
        return markup

    @classmethod
    def send_topics_poll(cls, message: types.Message):
        is_setup = Settings.get_completed(message.chat.id)
        topics = cls.get_topics(message.chat.id)
        reply_markup = types.ReplyKeyboardRemove()

        question = "What topics are you interested in?\n_(you may choose multiple)_"
        if is_setup:
            reply_markup = cls.get_topics_buttons()
        else:
            question = "*Step 1/3*\n\n" + question

        msg = bot.send_poll(
            chat_id=message.chat.id,
            question=question,
            is_anonymous=False,
            options=[types.InputPollOption(topic.title()) for topic in topics],
            allows_multiple_answers=True,
            question_parse_mode="Markdown",
            reply_markup=reply_markup,
        )
        ACTIVE_POLLS[msg.chat.id] = {
            "options": topics,
            "chat_id": message.chat.id,
        }
        ACTIVE_SETUP_MESSAGES[msg.chat.id] = [msg.id]

    @classmethod
    def get_back_to_settings_buttons(cls) -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(
                "Back to Settings", callback_data=f"back_to_settings"
            )
        )
        return markup

    @classmethod
    def set_topics(cls, poll: types.PollAnswer):
        is_setup = Settings.get_completed(poll.user.id)
        print("is_setup: ", is_setup)

        topics = []
        active_poll = ACTIVE_POLLS[poll.user.id]
        topic_options = active_poll["options"]

        reply_markup = types.ReplyKeyboardRemove()
        if is_setup:
            reply_markup = cancel_markup

        for topic_id in poll.option_ids:
            topics.append(topic_options[topic_id])

        resp = requests.patch(
            SERVER_URL + f"/topics",
            params={"chat_id": poll.user.id},
            json=topics,
        )

        if response_wrapper(resp, [200, 201], chat_id=poll.user.id):
            if is_setup:
                msg = bot.send_message(
                    chat_id=poll.user.id,
                    text=f"✅ Topic preferences were updated!",
                    parse_mode="Markdown",
                    reply_markup=markup,
                )
                ACTIVE_SETTINGS_MESSAGES[poll.user.id] = [msg.id]
            try:
                bot.delete_messages(poll.user.id, ACTIVE_SETUP_MESSAGES[poll.user.id])
            except:
                pass
            if not is_setup:
                cls.send_text_format(chat_id=poll.user.id)

    @classmethod
    def get_text_formats(cls, chat_id: int) -> types.InlineKeyboardMarkup:
        response = requests.get(SERVER_URL + f"/text_format")
        if response_wrapper(response, [200, 201], chat_id=chat_id):
            json_data = response.json()
            if json_data["text_formats"]:
                return json_data["text_formats"]

    @classmethod
    def get_text_formats_buttons(
        cls, chat_id: int, show_cancel: bool = True
    ) -> types.InlineKeyboardMarkup:
        text_formats = cls.get_text_formats(chat_id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            *[
                types.InlineKeyboardButton(
                    text_format.title(),
                    callback_data=f"text_format_{text_format.lower()}",
                )
                for text_format in text_formats
            ],
        )
        if show_cancel:
            markup.add(
                types.InlineKeyboardButton(
                    "Cancel",
                    callback_data=f"cancel",
                ),
            )
        return markup

    @classmethod
    def send_text_format(cls, chat_id: int):
        is_setup = Settings.get_completed(chat_id)
        text = "What text style do you prefer?"
        if not is_setup:
            text = "*Step 2/3*\n\n" + text
        msg = bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=cls.get_text_formats_buttons(
                chat_id=chat_id, show_cancel=is_setup
            ),
        )
        ACTIVE_SETUP_MESSAGES[msg.chat.id] = [msg.id]

    @classmethod
    def set_text_format(cls, call: types.CallbackQuery):
        is_setup = Settings.get_completed(call.message.chat.id)
        text_format_selected = call.data.split("_")[-1].title()
        resp = requests.patch(
            SERVER_URL + f"/text_format",
            params={
                "format": text_format_selected,
                "chat_id": call.message.chat.id,
            },
        )
        if response_wrapper(resp, [200, 201], chat_id=call.message.chat.id):
            if is_setup:
                msg = bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"✅ Set your preferred text style to `{text_format_selected}`",
                    parse_mode="Markdown",
                    reply_markup=markup,
                )
                ACTIVE_SETTINGS_MESSAGES[call.message.chat.id] = [msg.id]
            try:
                bot.delete_messages(
                    call.message.chat.id, ACTIVE_SETUP_MESSAGES[call.message.chat.id]
                )
            except:
                pass
            if not is_setup:
                cls.send_reply_mode(message=call.message)

    @classmethod
    def get_reply_mode_buttons(
        cls, show_cancel: bool = True
    ) -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("💬 Text", callback_data="reply_mode_text"),
            types.InlineKeyboardButton("🎙 Audio", callback_data="reply_mode_voice"),
        )
        if show_cancel:
            markup.add(
                types.InlineKeyboardButton(
                    "Cancel",
                    callback_data=f"cancel",
                ),
            )
        return markup

    @classmethod
    def send_reply_mode(cls, message: types.Message):
        is_setup = Settings.get_completed(message.chat.id)
        text = "How would you prefer me to answer you?"
        if not is_setup:
            text = "*Step 3/3*\n\n" + text
        msg = bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode="Markdown",
            reply_markup=cls.get_reply_mode_buttons(show_cancel=is_setup),
        )
        ACTIVE_SETUP_MESSAGES[msg.chat.id] = [msg.id]

    @classmethod
    def set_reply_mode(cls, call: types.CallbackQuery):
        is_setup = Settings.get_completed(call.message.chat.id)
        reply_mode_selected = call.data.split("_")[-1]
        reply_mode = REPLY_MODES[reply_mode_selected]

        resp = requests.patch(
            SERVER_URL + f"/mode",
            params={
                "mode": reply_mode,
                "chat_id": call.message.chat.id,
            },
        )
        if response_wrapper(
            resp, good_status_codes=[200], chat_id=call.message.chat.id
        ):
            if is_setup:
                msg = bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"✅ Set your preferred reply mode to `{call.data.split('_')[-1].capitalize()}`",
                    parse_mode="Markdown",
                    reply_markup=markup,
                )
                ACTIVE_SETTINGS_MESSAGES[call.message.chat.id] = [msg.id]
            try:
                bot.delete_messages(
                    call.message.chat.id, ACTIVE_SETUP_MESSAGES[call.message.chat.id]
                )
            except:
                pass
            if not is_setup:
                cls.complete_setup(message=call.message)

    @classmethod
    def complete_setup(cls, message: types.Message):
        resp = requests.patch(
            SERVER_URL + f"/user/is_completed/{message.chat.id}",
            params={"chat_id": message.chat.id, "is_completed": True},
        )

        if response_wrapper(resp, good_status_codes=[200], chat_id=message.chat.id):
            msg = bot.send_message(
                chat_id=message.chat.id,
                text=HELP_MESSAGE,
                parse_mode="Markdown",
                reply_markup=markup,
            )

    @classmethod
    def get_completed(cls, chat_id: int) -> bool:
        resp = requests.get(
            SERVER_URL + f"/user/is_completed/{chat_id}",
            params={"chat_id": chat_id},
        )
        if response_wrapper(resp, good_status_codes=[200], chat_id=chat_id):
            json_data = resp.json()
            return json_data["is_completed"]
        return False

    @classmethod
    def check_completed(cls, chat_id: int) -> bool:
        is_completed = cls.get_completed(chat_id)
        if not is_completed:
            cls.handle_not_completed(chat_id)
        return is_completed

    @classmethod
    def handle_not_completed(cls, chat_id: int):
        bot.send_message(
            chat_id=chat_id,
            text="Before using the bot, press /setup to complete the setup of the bot!",
            parse_mode="Markdown",
            reply_markup=setup_markup,
        )

    @classmethod
    def get_settings_buttons(cls) -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("Topics", callback_data="settings_topics"),
            types.InlineKeyboardButton(
                "Text Style", callback_data="settings_textstyle"
            ),
            types.InlineKeyboardButton("Reply Mode", callback_data="settings_mode"),
        )
        return markup

    @classmethod
    def get_reply_mode(cls, chat_id: int) -> bool:
        resp = requests.get(
            SERVER_URL + f"/mode/{chat_id}",
            params={"chat_id": chat_id},
        )
        if response_wrapper(resp, good_status_codes=[200], chat_id=chat_id):
            json_data = resp.json()
            return json_data["mode"]
        return False


def response_wrapper(
    response: requests.Response,
    good_status_codes: list[int],
    chat_id: int,
) -> bool:
    if response.status_code not in good_status_codes:
        bot.send_message(
            chat_id=chat_id,
            text="Sorry, the service is currently unavailable. Please, try again later!",
        )
        return False
    return True


class HandleContent:

    @classmethod
    def create_user(cls, user: User, chat_id: int) -> bool:
        # check if user exists
        response = requests.get(
            SERVER_URL + f"/user/{user.chat_id}",
        )

        if response_wrapper(response, good_status_codes=[200], chat_id=chat_id):
            user_exists = response.json()["is_user"]
            print("User exists: ", user_exists)
            if not user_exists:

                # if does not exist, then create
                response = requests.put(
                    SERVER_URL + "/user",
                    json={
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                        "chat_id": user.chat_id,
                    },
                )

                return response_wrapper(
                    response, good_status_codes=[200, 201], chat_id=chat_id
                )

            return True
        return False

    @classmethod
    def reply_summary(
        cls,
        chat_id: int,
        text: str,
        reply_markup=types.ReplyKeyboardRemove(),
        reply_to_message_id: int = None,
    ):
        if Settings.get_reply_mode(chat_id):
            binary = kit.text_to_speech(text)
            binary = io.BytesIO(binary)
            bot.send_voice(
                chat_id,
                binary,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        else:
            msg = bot.send_message(
                chat_id,
                text,
                parse_mode="Markdown",
                reply_markup=markup,
                reply_to_message_id=reply_to_message_id,
            )

    @classmethod
    def get_content_buttons(cls) -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("✂️ Compress", callback_data="compress"),
        )
        return markup

    @classmethod
    def handle_recent_news(cls, message: types.Message):
        msg = bot.send_message(
            message.chat.id,
            "⌛️Loading...",
            parse_mode="Markdown",
            reply_markup=markup,
        )
        response = requests.get(
            SERVER_URL + f"/news/{message.chat.id}", params={"hours": 6}
        )
        # bot.delete_message(chat_id=message.chat.id, message_id=msg.id)
        if response_wrapper(
            response, good_status_codes=[200, 402], chat_id=message.chat.id
        ):
            if response.status_code == 402:
                bot.send_message(
                    message.chat.id,
                    "No recent news found for the selected topics!",
                    parse_mode="Markdown",
                    reply_markup=markup,
                )
            else:
                text = f"🔥 *Recent News*\n\n"
                json_data = response.json()["news"]
                for item in json_data:
                    text += f"*{item['topic']}*\n{item['summary']}\n\n"

                today = datetime.datetime.fromtimestamp(message.date)
                today = today.strftime("%B %d, %Y")
                text += today
                HandleContent.reply_summary(
                    chat_id=message.chat.id,
                    text=text,
                    reply_markup=HandleContent.get_content_buttons(),
                )

    @classmethod
    def handle_daily_news(cls, message: types.Message):
        msg = bot.send_message(
            message.chat.id,
            "⌛️Loading...",
            parse_mode="Markdown",
            reply_markup=markup,
        )
        response = requests.get(
            SERVER_URL + f"/news/{message.chat.id}", params={"hours": 24}
        )
        # bot.delete_message(chat_id=message.chat.id, message_id=msg.id)
        if response_wrapper(response, good_status_codes=[200], chat_id=message.chat.id):
            text = f"📰 *Daily News*\n\n"
            json_data = response.json()["news"]
            for item in json_data:
                text += f"*{item['topic']}*\n{item['summary']}\n\n"

            today = datetime.datetime.fromtimestamp(message.date)
            today = today.strftime("%B %d, %Y")
            text += today
            HandleContent.reply_summary(
                chat_id=message.chat.id,
                text=text,
                reply_markup=HandleContent.get_content_buttons(),
            )

    @classmethod
    def handle_urls(cls, message: types.Message, urls: list[str]):
        response = requests.post(
            SERVER_URL + "/summary/url",
            params={"chat_id": message.chat.id},
            json={"url": urls[0]},
        )
        print(response.json())
        if response_wrapper(response, good_status_codes=[200], chat_id=message.chat.id):
            json_resp = response.json()
            text = f"*{json_resp['title']}*\n\n{json_resp['summary']}"
            HandleContent.reply_summary(
                chat_id=message.chat.id,
                text=text,
                reply_markup=HandleContent.get_content_buttons(),
            )

    @classmethod
    def handle_youtube(cls, message: types.Message, url: str):
        msg = bot.send_message(
            message.chat.id,
            "⌛️Loading...",
            parse_mode="Markdown",
            reply_markup=markup,
        )
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0]

        response = requests.post(
            SERVER_URL + "/summary/video",
            params={"chat_id": message.chat.id, "video_id": video_id},
        )
        print(response)
        if response_wrapper(
            response, good_status_codes=[200, 404], chat_id=message.chat.id
        ):
            if response.status_code == 200:
                json_data = response.json()
                title = json_data["title"]
                text = json_data["summary"]
                text = f"*{title}*\n\n{text}"
                HandleContent.reply_summary(
                    chat_id=message.chat.id,
                    text=text,
                    reply_markup=markup,
                    reply_to_message_id=message.id,
                )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="⚠️ Unable to process the video!",
                    parse_mode="Markdown",
                    reply_to_message_id=message.id,
                    reply_markup=markup,
                )

    @classmethod
    def handle_compress(cls, call: types.CallbackQuery):
        msg = bot.send_message(
            call.message.chat.id,
            "⌛️Loading...",
            parse_mode="Markdown",
            reply_markup=markup,
        )
        text = call.message.text.split("\n\n")
        title = text[0]
        if "compressed" not in title.lower():
            title += " (compressed)"
        date = None
        if "news" in title.lower():
            date = text[-1]
            text.pop()

        text.pop(0)
        summarized_text = [f"*{title}*"]
        print(title)

        for t in text:
            topic = t.split("\n")
            if "news" in title.lower():
                topic_title = topic[0]
                topic.pop(0)
            topic_text = " ".join(topic)
            response = requests.post(
                SERVER_URL + f"/summary/compress",
                params={"chat_id": call.message.chat.id},
                json={"text": topic_text},
            )
            if response_wrapper(
                response, good_status_codes=[200], chat_id=call.message.chat.id
            ):
                summarized_topic_text = ""
                if "news" in title.lower():
                    summarized_topic_text = f"*{topic_title}*" + "\n"
                json_data = response.json()
                summarized_topic_text += json_data["text"]
                summarized_text.append(summarized_topic_text)

        print(summarized_text)
        if date is not None:
            summarized_text.append(date)
        summarized_text = "\n\n".join(summarized_text)
        HandleContent.reply_summary(
            chat_id=call.message.chat.id,
            text=text,
            reply_markup=HandleContent.get_content_buttons(),
        )

    @classmethod
    def handle_question(cls, message: types.Message):
        response = requests.post(
            SERVER_URL + "/summary/model_text_control",
            params={"chat_id": message.chat.id},
            json={"message": message.text},
        )
        if response_wrapper(
            response, good_status_codes=[200, 404], chat_id=message.chat.id
        ):
            json_resp = response.json()
            if response.status_code == 200:
                HandleContent.reply_summary(
                    chat_id=message.chat.id,
                    text=json_resp["summary"],
                    reply_to_message_id=message.id,
                )
            elif response.status_code == 404:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Please, send content first!",
                    parse_mode="Markdown",
                    reply_to_message_id=message.id,
                )

    @classmethod
    def handle_voice_question(cls, message: types.Message):
        file_info = bot.get_file(message.voice.file_id)
        voice_data = bot.download_file(file_info.file_path)
        voice_bytes = io.BytesIO(voice_data)

        response = requests.post(
            url=SERVER_URL + "/summary/model_voice_control",
            params={"chat_id": message.chat.id},
            files={"file": ("audio.ogg", voice_bytes, "audio/ogg")},
        )
        if response_wrapper(
            response, good_status_codes=[200, 404], chat_id=message.chat.id
        ):
            json_resp = response.json()
            if response.status_code == 200:
                HandleContent.reply_summary(
                    chat_id=message.chat.id,
                    text=json_resp["summary"],
                    reply_markup=markup,
                    reply_to_message_id=message.id,
                )
            elif response.status_code == 404:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Please, send content first!",
                    parse_mode="Markdown",
                    reply_to_message_id=message.id,
                )

    @classmethod
    def handle_cancel(cls, message: types.Message):
        try:
            # bot.send_message(
            #     chat_id=message.chat.id,
            #     text="Action cancelled",
            #     reply_markup=markup,
            # )
            bot.delete_messages(message.chat.id, ACTIVE_SETUP_MESSAGES[message.chat.id])
        except Exception as e:
            print(e)
            if type(e) is str and not "inline keyboard expected" in e:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Something went wrong, aborting!",
                    reply_markup=markup,
                )

    @classmethod
    def handle_settings(cls, message: types.Message):
        msg = bot.send_message(
            chat_id=message.chat.id,
            text="*Settings*\n\nYou may change your topics of interest, preferred text style and output mode!",
            parse_mode="Markdown",
            reply_markup=Settings.get_settings_buttons(),
        )

    @classmethod
    def handle_help(cls, message: types.Message):
        text = HELP_MESSAGE
        bot.send_message(
            message.chat.id, text, parse_mode="Markdown", reply_markup=markup
        )


@bot.message_handler(commands=["start"])
def start_handler(message: types.Message):
    text = START_TEXT

    bot.send_message(
        message.chat.id, text, parse_mode="Markdown", reply_markup=setup_markup
    )
    user = User(
        chat_id=message.chat.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
    )
    create_user_resp = HandleContent.create_user(user, chat_id=message.chat.id)
    if create_user_resp:
        resp = requests.patch(
            SERVER_URL + f"/user/is_completed/{message.chat.id}",
            params={"chat_id": message.chat.id, "is_completed": False},
        )
        print(resp)
        response_wrapper(resp, good_status_codes=[200], chat_id=message.chat.id)
        resp = requests.patch(
            SERVER_URL + f"/summary/clear_cache",
            params={"chat_id": message.chat.id},
        )
        print(resp)
        response_wrapper(resp, good_status_codes=[200], chat_id=message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: types.CallbackQuery):
    is_setup = False
    try:
        if IS_SETUP[call.message.chat.id] is not None:
            is_setup = True
    except KeyError:
        pass
    if "cancel" == call.data:
        HandleContent.handle_cancel(call.message)
    elif "text_format_" in call.data:
        Settings.set_text_format(call)
    elif "reply_mode_" in call.data:
        Settings.set_reply_mode(call)
    elif "back_to_settings" == call.data:
        try:
            bot.delete_messages(
                call.message.chat.id, ACTIVE_SETTINGS_MESSAGES[call.message.chat.id]
            )
            del ACTIVE_SETTINGS_MESSAGES[call.message.chat.id]
        except:
            pass
    elif "compress" == call.data:
        HandleContent.handle_compress(call)
    elif "settings_" in call.data:
        parameter = call.data.split("_")[-1]
        if parameter == "topics":
            Settings.send_topics_poll(message=call.message)
        elif parameter == "textstyle":
            Settings.send_text_format(chat_id=call.message.chat.id)
        elif parameter == "mode":
            Settings.send_reply_mode(message=call.message)


@bot.message_handler(commands=["help"])
def help_handler(message: types.Message):
    if Settings.check_completed(message.chat.id):
        HandleContent.handle_help(message)


@bot.message_handler(commands=["menu"])
def menu_handler(message: types.Message):
    if Settings.check_completed(message.chat.id):
        HandleContent.handle_help(message)


@bot.message_handler(commands=["cancel"])
def cancel_handler(message: types.Message):
    if Settings.check_completed(message.chat.id):
        HandleContent.handle_cancel(message)


@bot.message_handler(commands=["recent_news"])
def recent_news_handler(message: types.Message):
    if Settings.check_completed(message.chat.id):
        HandleContent.handle_recent_news(message)


@bot.message_handler(commands=["daily_news"])
def daily_news_handler(message: types.Message):
    if Settings.check_completed(message.chat.id):
        HandleContent.handle_daily_news(message)


@bot.message_handler(commands=["setup"])
def handle_setup(message: types.Message):
    resp = requests.patch(
        SERVER_URL + f"/user/is_completed/{message.chat.id}",
        params={"chat_id": message.chat.id, "is_completed": False},
    )
    print(resp)
    response_wrapper(resp, good_status_codes=[200], chat_id=message.chat.id)
    resp = requests.patch(
        SERVER_URL + f"/summary/clear_cache",
        params={"chat_id": message.chat.id},
    )
    print(resp)
    response_wrapper(resp, good_status_codes=[200], chat_id=message.chat.id)
    Settings.send_topics_poll(message)


# @bot.message_handler(commands=["summary"])
# def handle_setup(message: types.Message):
#     if Settings.check_completed(message.chat.id):
#         response = requests.post(
#             SERVER_URL + "/summary/text",
#             params={"chat_id": message.chat.id},
#             json={"text": message.text[9:]},
#         )
#         if response_wrapper(response, good_status_codes=[200], chat_id=message.chat.id):
#             json_resp = response.json()
#             text = f"*{json_resp['title']}*\n{json_resp['summary']}"
#             bot.send_message(
#                 chat_id=message.chat.id,
#                 text=text,
#                 parse_mode="Markdown",
#                 reply_markup=HandleContent.get_content_buttons(),
#             )


@bot.message_handler(commands=["settings"])
def handle_settings(message: types.Message):
    if Settings.check_completed(message.chat.id):
        HandleContent.handle_settings(message)


@bot.message_handler(content_types=["audio"])
def handle_audio(message: types.Message):
    if Settings.check_completed(message.chat.id):
        file_info = bot.get_file(message.audio.file_id)
        audio_data = bot.download_file(file_info.file_path)
        audio_bytes = io.BytesIO(audio_data)

        response = requests.post(
            url=SERVER_URL + "/summary/audio",
            params={
                "chat_id": message.chat.id,
            },
            files={"file": ("audio.ogg", audio_bytes, "audio/ogg")},
        )

        if response_wrapper(
            response, good_status_codes=[200, 404], chat_id=message.chat.id
        ):
            if response.status_code == 404:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="The audio file does not contain any words",
                    reply_to_message_id=message.id,
                    parse_mode="Markdown",
                )

            else:
                json_data = response.json()
                HandleContent.reply_summary(
                    chat_id=message.chat.id,
                    text=json_data["summary"],
                    reply_markup=markup,
                    reply_to_message_id=message.id,
                )


@bot.message_handler(content_types=["document"])
def handle_document(message: types.Message):
    if Settings.check_completed(message.chat.id):
        file_info = bot.get_file(message.document.file_id)
        document_data = bot.download_file(file_info.file_path)
        document_bytes = io.BytesIO(document_data)

        if message.document.file_name.split(".")[-1] == "pdf":
            response = requests.post(
                url=SERVER_URL + "/summary/pdf",
                params={
                    "chat_id": message.chat.id,
                },
                files={
                    "file": (
                        message.document.file_name,
                        document_bytes,
                        message.document.mime_type,
                    )
                },
            )

        else:
            response = requests.post(
                url=SERVER_URL + "/summary/file",
                params={
                    "chat_id": message.chat.id,
                },
                files={
                    "file": (
                        message.document.file_name,
                        document_bytes,
                        message.document.mime_type,
                    )
                },
            )

        if response_wrapper(
            response, good_status_codes=[200, 404], chat_id=message.chat.id
        ):
            if response.status_code == 404:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="⚠️ Unable to detect any text",
                    reply_to_message_id=message.id,
                    parse_mode="Markdown",
                )

            else:
                json_data = response.json()
                text = f"*{json_data['title']}*\n\n{json_data['summary']}"
                HandleContent.reply_summary(
                    chat_id=message.chat.id,
                    text=text,
                    reply_markup=markup,
                    reply_to_message_id=message.id,
                )


@bot.message_handler(content_types=["text"])
def text_handler(message: types.Message):
    if Settings.check_completed(message.chat.id):
        if message.text == "Recent News":
            HandleContent.handle_recent_news(message)
        elif message.text == "Daily News":
            HandleContent.handle_daily_news(message)
        elif message.text == "Settings":
            HandleContent.handle_settings(message)
        elif message.text == "Menu":
            HandleContent.handle_help(message)
        else:
            # check for youtube links
            youtube = re.search(
                "http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?",
                message.text,
            )
            if youtube:
                HandleContent.handle_youtube(message, youtube.group(0))

            else:
                links = re.findall("(?P<url>http(?:s?)://[^\s]+)", message.text)
                if len(links) > 0:
                    HandleContent.handle_urls(message=message, urls=links)

                else:
                    HandleContent.handle_question(message)


@bot.message_handler(content_types=["photo"])
def handle_image(message: types.Message):
    photos = []
    for photo in message.photo:
        file_info = bot.get_file(photo.file_id)
        photo_data = bot.download_file(file_info.file_path)
        photos.append(io.BytesIO(photo_data))

    response = requests.post(
        url=f"http://{host}:{port}/voice_message",
        files={"file": ("audio.ogg", photos, "audio/ogg")},
    )


@bot.message_handler(content_types=["voice"])
def voice_handler(message: types.Message):
    if Settings.check_completed(message.chat.id):
        HandleContent.handle_voice_question(message)


@bot.poll_answer_handler()
def handle_poll_answer(poll: types.PollAnswer):
    is_setup = False
    try:
        if IS_SETUP[poll.user.id] is not None:
            is_setup = True
    except KeyError:
        pass
    Settings.set_topics(poll)


if __name__ == "__main__":
    # while True:
    #     try:
    #         bot.polling(none_stop=True, skip_pending=True)
    #     except Exception as e:
    #         print(e)
    #         print("Restarting...")
    bot.polling(none_stop=True, skip_pending=True)
