import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, you are not authorized to use this bot."
        )
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I am your personal link generator bot. Forward any file to me, and I will generate a direct download link for you."
    )

async def generate_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    message = update.message
    
    # Check for any type of media or file
    if message.document or message.video or message.audio or message.photo:
        try:
            # Get the file object
            if message.document:
                file_id = message.document.file_id
            elif message.video:
                file_id = message.video.file_id
            elif message.audio:
                file_id = message.audio.file_id
            elif message.photo:
                file_id = message.photo[-1].file_id # Get the highest resolution photo
            else:
                await message.reply_text("Unsupported file type.")
                return

            file = await context.bot.get_file(file_id)
            
            # The file_path is what we need for the direct link
            # The link format is https://api.telegram.org/file/bot<token>/<file_path>
            download_link = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
            
            await message.reply_text(
                f"Here is your permanent direct download link:\n\n`{download_link}`",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error generating link: {e}")
            await message.reply_text("Sorry, something went wrong while generating the link.")
    else:
        await message.reply_text("Please forward a file, video, audio, or photo to generate a link.")

if __name__ == '__main__':
    if not BOT_TOKEN or not ADMIN_ID:
        logger.error("BOT_TOKEN or ADMIN_ID environment variables are not set!")
    else:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        start_handler = CommandHandler('start', start)
        link_generator_handler = MessageHandler(filters.ALL & (~filters.COMMAND), generate_link)
        
        application.add_handler(start_handler)
        application.add_handler(link_generator_handler)
        
        logger.info("Bot started...")
        application.run_polling()
