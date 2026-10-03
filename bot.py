import os
import subprocess
import threading
import telebot
from telebot import types

# Replace with your actual bot token
BOT_TOKEN = '8811086887:AAFZWDz3vDtCE6IDbCxBk_SFZcKTGqT1Woo'
bot = telebot.TeleBot(BOT_TOKEN)

# To prevent multiple scans at the same time
is_scanning = False

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_scan = types.KeyboardButton('/scan')
    btn_status = types.KeyboardButton('/status')
    markup.add(btn_scan, btn_status)
    
    welcome_text = (
        "🤖 *Welcome to the Jio Gemini Activation Bot!*\n\n"
        "Commands:\n"
        "/scan - Start the activation scanning process\n"
        "/status - Check if a scan is currently running"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['status'])
def send_status(message):
    global is_scanning
    if is_scanning:
        bot.reply_to(message, "⏳ A scan is currently *running*.", parse_mode='Markdown')
    else:
        bot.reply_to(message, "✅ No scan is currently running. Use /scan to start one.", parse_mode='Markdown')

@bot.message_handler(commands=['scan'])
def run_scan(message):
    global is_scanning
    if is_scanning:
        bot.reply_to(message, "⚠️ A scan is already running! Please wait for it to finish.", parse_mode='Markdown')
        return

    is_scanning = True
    bot.reply_to(message, "🚀 *Starting the scan...*\nThis might take a while. I will notify you when it's done and send the results.", parse_mode='Markdown')

    # Run the scanner in a separate thread so it doesn't block the bot
    def scan_thread(chat_id):
        global is_scanning
        try:
            # Run the scanning script
            process = subprocess.run(
                ['python', 'gemini18msc.py'], 
                capture_output=True, 
                text=True
            )
            
            # Send notification that it finished
            bot.send_message(chat_id, "✅ *Scan Completed!*\nSending results...", parse_mode='Markdown')
            
            # Send the files if they exist
            links_file = 'gemini_activation_links.txt'
            results_file = 'gemini_results.csv'
            
            sent_files = 0
            if os.path.exists(links_file):
                with open(links_file, 'rb') as f:
                    bot.send_document(chat_id, f)
                sent_files += 1
            
            if os.path.exists(results_file):
                with open(results_file, 'rb') as f:
                    bot.send_document(chat_id, f)
                sent_files += 1
                
            if sent_files == 0:
                bot.send_message(chat_id, "ℹ️ The scan finished, but no new links or results were generated.")
                
        except Exception as e:
            bot.send_message(chat_id, f"❌ *Error during scan:*\n`{str(e)}`", parse_mode='Markdown')
        finally:
            is_scanning = False

    t = threading.Thread(target=scan_thread, args=(message.chat.id,))
    t.start()

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
