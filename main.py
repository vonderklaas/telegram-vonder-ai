import replicate
import os
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
BOT_NAME = os.getenv('BOT_NAME')

print(f"TELEGRAM_API_KEY: {TELEGRAM_API_KEY}, REPLICATE_API_TOKEN: {REPLICATE_API_TOKEN}, BOT_NAME: {BOT_NAME}, ")

# COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    intro_text = (
        "Welcome to Vonder!\n\n"
        "You're interacting with an AI, not a human.\n"
        "While the AI aims to generate accurate content, the results are fully computer-generated and may not always be perfect.\n\n"
        "You can use the following commands to interact with me:\n\n"
        "/start — Get familiar with Vonder\n"
        "/help — Get an example of how to construct prompts\n"
        "/enhance — Tips to enhance your prompts\n"
        "/generate [prompt] — Generate an image based on your prompt\n\n"
        "Invite friends & get perks 🎁"
    )
    await update.message.reply_text(intro_text)

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text
    if len(command.split()) < 2:
        await update.message.reply_text("Please provide a prompt after the /generate command.", reply_to_message_id=update.message.message_id)
        return

    _, after_command = command.split(' ', 1)
    await update.message.reply_text("Generating...", reply_to_message_id=update.message.message_id)
    
    try:
        image_url = await generate_image(after_command)
        print("generate_command image_url:", image_url)
        if image_url:
            await update.message.reply_photo(
                photo=image_url, 
                caption="Done, enjoy 🤗",
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text("Sorry, I couldn't generate the image.", reply_to_message_id=update.message.message_id)
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}. Please try a different prompt.", reply_to_message_id=update.message.message_id)

async def ehance_prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    intro_text = (
        "Few tips on better prompts:\n\n"
        "1. Talk to the Vonder like it is a human\n"
        "2. Set the stage and provide context\n"
        "3. Provide details, like 'happy' or 'dynamic shot'\n"
        "4. Don't be afraid to experiment\n\n"
        "Good luck 🩵"
    )
    await update.message.reply_text(intro_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    demo_prompt = "an astronaut riding a horse on mars, hd, dramatic lighting"
    await update.message.reply_text("Let me generate an image to show how prompts work.", reply_to_message_id=update.message.message_id)
    
    try:
        image_url = await generate_image(demo_prompt)
        if image_url:
            await update.message.reply_photo(
                photo=image_url, 
                caption="To achieve this, I used:\n\n\"an astronaut riding a horse on mars, hd, dramatic lighting\"",
                reply_to_message_id=update.message.message_id
            )            
            await update.message.reply_text("Now it's your turn!\n\n Use /generate followed by your prompt to create your own image.", reply_to_message_id=update.message.message_id)
        else:
            await update.message.reply_text("Sorry, I couldn't generate the example image.", reply_to_message_id=update.message.message_id)
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}. Please try again later.", reply_to_message_id=update.message.message_id)

async def handle_response(text: str) -> str:
    processed: str = text.lower()
    print('handle_response text:', processed)

    if 'hello' in processed:
        return f'Hey!'
    return 'Sorry, I am not able to communicate (yet)'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'user ({update.message.chat.id}) in {message_type}: {text}')

    if message_type in ['group', 'supergroup']:
        if BOT_NAME.lower() in text.lower():
            new_text: str = text.replace(BOT_NAME, '').strip()
            response: str = await handle_response(new_text)
        else:
            return
    else:
        response: str = await handle_response(text)

    print(f'vonder: {response}')
    await update.message.reply_text(response)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that command. Please use one of the available commands from the list.")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error: {context.error}')

# GENERATE IMAGE
async def generate_image(prompt: str):
    output = replicate.run('black-forest-labs/flux-dev', input={
            "prompt": prompt,
            "guidance": 3.5,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "webp",
            "output_quality": 80,
            "prompt_strength": 0.8,
            "num_inference_steps": 50
        }
    )
    return output[0]

if __name__ == '__main__':
    print('starting Vonder...')
    app = Application.builder().token(TELEGRAM_API_KEY).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('generate', generate_command))
    app.add_handler(CommandHandler('enhance', ehance_prompt_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_error_handler(error)

    print('polling...')
    app.run_polling(poll_interval=3)
