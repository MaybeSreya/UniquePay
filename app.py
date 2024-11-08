from flask import Flask, render_template, jsonify
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import threading
import os

app = Flask(__name__)
bot = Client("my_bot", api_id=22546858, api_hash="cdb9dc068a201f97b8296cf10265fa14", bot_token="7819085580:AAE1OhofRfqNli3JY8FhT4CQdoEQmGH4hQM")

moderator_message_id = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notify_payment', methods=['POST'])
def notify_payment():
    global moderator_message_id
    message = bot.send_message(
        chat_id="@unique_pays",
        text="Payment verification needed !",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Received ✅", callback_data="received"),
                InlineKeyboardButton("Failed ❌", callback_data="failed")
            ]
        ])
    )
    moderator_message_id = message.message_id
    return jsonify({"message": "Moderator will check your payments!"})

@bot.on_callback_query()
async def handle_callback_query(client, callback_query: CallbackQuery):
    global moderator_message_id
    if callback_query.message.message_id == moderator_message_id:
        if callback_query.data == "received":
            await callback_query.answer("Payment received!")
            update_website_status("Payment received!")
        elif callback_query.data == "failed":
            await callback_query.answer("Payment not received / payment failed!")
            update_website_status("Payment not received / payment failed!")
        await callback_query.message.delete()

def update_website_status(status_message):
    with app.test_request_context():
        app.config['LATEST_STATUS'] = status_message

@app.route('/get_latest_status')
def get_latest_status():
    latest_status = app.config.get('LATEST_STATUS', "Moderator will check your payments!")
    return jsonify({"message": latest_status})

if __name__ == "__main__":
    threading.Thread(target=app.run, kwargs={"use_reloader": False}).start()
    bot.run()
