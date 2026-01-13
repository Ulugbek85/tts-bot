import os
import uuid
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from TTS.api import TTS

# =====================
# TOKENNI SHU YERGA QO‘YING
# =====================
TOKEN = os.getenv("BOT_TOKEN")

# =====================
# MODELLAR (LOCAL)
# =====================
MODELS = {
    "uz_male": "tts_models/uz/mai_tts/vits",
    "en_male": "tts_models/en/ljspeech/tacotron2-DDC",
    "en_female": "tts_models/en/vctk/vits"
}

tts_objects = {}
user_voice = {}

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🇺🇿 Uzbek Erkak"],
        ["🇬🇧 English Erkak", "🇬🇧 English Ayol"]
    ]
    await update.message.reply_text(
        "Til va ovozni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# =====================
# OVOZ TANLASH
# =====================
async def choose_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.effective_user.id

    if "Uzbek" in text:
        user_voice[uid] = "uz_male"
        await update.message.reply_text("✅ O‘zbek erkak ovozi tanlandi.\nMatn yuboring.")
    elif "English Erkak" in text:
        user_voice[uid] = "en_male"
        await update.message.reply_text("✅ English male voice selected.\nSend text.")
    elif "English Ayol" in text:
        user_voice[uid] = "en_female"
        await update.message.reply_text("✅ English female voice selected.\nSend text.")

# =====================
# MATNNI AUDIOGA AYLANTIRISH
# =====================
async def tts_convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if uid not in user_voice:
        await update.message.reply_text("⚠️ Avval /start bosib ovoz tanlang.")
        return

    voice = user_voice[uid]

    if voice not in tts_objects:
        tts_objects[voice] = TTS(
            model_name=MODELS[voice],
            progress_bar=False,
            gpu=False
        )

    tts = tts_objects[voice]

    filename = f"{OUTPUT_DIR}/{uuid.uuid4().hex}.wav"

    # 🔹 UZUN MATN — O‘ZI BO‘LIB O‘QILADI
    tts.tts_to_file(
        text=text,
        file_path=filename
    )

    await update.message.reply_audio(
        audio=open(filename, "rb"),
        caption="🎧 Tayyor audio"
    )

# =====================
# MAIN
# =====================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, choose_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tts_convert))

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
