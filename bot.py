import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from googletrans import Translator
from PyPDF2 import PdfMerger
from PIL import Image
import img2pdf
import pytesseract
import io
import os
import tempfile
import docx2txt

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

translator = Translator()

# Payment info
ZAIN_CASH_NUMBER = "2581562424"
KI_CARD_NUMBER = "2581562424"
PAYMENT_AMOUNT = 5000  # Iraqi Dinar

# States for payment verification
waiting_for_payment_screenshot = False
waiting_for_file_after_payment = False
file_to_translate_after_payment = None
translation_direction_after_payment = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the multifunctional Telegram bot!\n"
        "Commands:\n"
        "/translate_line - Translate file line by line (Arabic-English and vice versa)\n"
        "/image_to_pdf - Convert images to PDF\n"
        "/word_to_pdf - Convert Word documents to PDF\n"
        "/merge_pdf - Merge PDF files\n"
        "/professional_translate - Professional file translation (5000 IQD payment required)\n"
        "/ocr - Extract text from image\n"
        "/get_book - Get books or sources by name and author\n"
        "Send a command to start."
    )

async def translate_line(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send the file you want to translate line by line.")

async def handle_file_line_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file:
        await update.message.reply_text("Please send a valid file.")
        return
    file_obj = await file.get_file()
    file_bytes = await file_obj.download_as_bytearray()
    text = file_bytes.decode('utf-8', errors='ignore')
    lines = text.splitlines()
    translated_lines = []
    for line in lines:
        if line.strip():
            translated = translator.translate(line, src='ar', dest='en').text if is_arabic(line) else translator.translate(line, src='en', dest='ar').text
            translated_lines.append(translated)
        else:
            translated_lines.append('')
    translated_text = "\n".join(translated_lines)
    await update.message.reply_text(f"Translated text:\n{translated_text}")

def is_arabic(text):
    for ch in text:
        if '\u0600' <= ch <= '\u06FF' or '\u0750' <= ch <= '\u077F' or '\u08A0' <= ch <= '\u08FF':
            return True
    return False

async def image_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send the image file(s) you want to convert to PDF.")

async def handle_image_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = update.message.photo
    document = update.message.document
    files = []
    if photos:
        for photo in photos:
            file_obj = await photo.get_file()
            file_bytes = await file_obj.download_as_bytearray()
            files.append(file_bytes)
    elif document:
        file_obj = await document.get_file()
        file_bytes = await file_obj.download_as_bytearray()
        files.append(file_bytes)
    else:
        await update.message.reply_text("Please send image files.")
        return
    pdf_bytes = img2pdf.convert([io.BytesIO(f) for f in files])
    await update.message.reply_document(document=InputFile(io.BytesIO(pdf_bytes), filename="converted.pdf"))

async def word_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send the Word document you want to convert to PDF.")

async def handle_word_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document or not document.file_name.endswith(('.doc', '.docx')):
        await update.message.reply_text("Please send a valid Word document (.doc or .docx).")
        return
    file_obj = await document.get_file()
    file_bytes = await file_obj.download_as_bytearray()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    text = docx2txt.process(tmp_path)
    os.unlink(tmp_path)
    # Convert text to PDF using reportlab
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    textobject = c.beginText(40, 750)
    for line in text.splitlines():
        textobject.textLine(line)
    c.drawText(textobject)
    c.save()
    buffer.seek(0)
    await update.message.reply_document(document=InputFile(buffer, filename="converted.pdf"))

async def merge_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send the PDF files you want to merge.")

async def handle_merge_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    documents = update.message.document
    if not documents:
        await update.message.reply_text("Please send PDF files.")
        return
    files = []
    if isinstance(documents, list):
        for doc in documents:
            if not doc.file_name.endswith('.pdf'):
                await update.message.reply_text("All files must be PDFs.")
                return
            file_obj = await doc.get_file()
            file_bytes = await file_obj.download_as_bytearray()
            files.append(io.BytesIO(file_bytes))
    else:
        if not documents.file_name.endswith('.pdf'):
            await update.message.reply_text("File must be a PDF.")
            return
        file_obj = await documents.get_file()
        file_bytes = await file_obj.download_as_bytearray()
        files.append(io.BytesIO(file_bytes))
    merger = PdfMerger()
    for f in files:
        merger.append(f)
    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    await update.message.reply_document(document=InputFile(output, filename="merged.pdf"))

async def professional_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_for_payment_screenshot
    waiting_for_payment_screenshot = True
    await update.message.reply_text(
        f"To use professional translation, please pay {PAYMENT_AMOUNT} IQD via Zain Cash or Ki Card.\n"
        f"Zain Cash Number: {ZAIN_CASH_NUMBER}\n"
        f"Ki Card Number: {KI_CARD_NUMBER}\n"
        "After payment, please send a screenshot of the payment."
    )

async def handle_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_for_payment_screenshot, waiting_for_file_after_payment, file_to_translate_after_payment, translation_direction_after_payment
    if not waiting_for_payment_screenshot:
        return
    photo = update.message.photo
    document = update.message.document
    if not photo and not document:
        await update.message.reply_text("Please send a screenshot image or document of the payment.")
        return
    # Here, we just accept the screenshot and ask for the file to translate
    waiting_for_payment_screenshot = False
    waiting_for_file_after_payment = True
    await update.message.reply_text("Payment screenshot received. Please send the file you want to translate professionally.")

async def handle_file_after_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_for_file_after_payment
    if not waiting_for_file_after_payment:
        return
    document = update.message.document
    if not document:
        await update.message.reply_text("Please send a valid file.")
        return
    # For simplicity, just echo back that translation is done
    waiting_for_file_after_payment = False
    await update.message.reply_text("File received. Professional translation will be done shortly (simulated).")

async def ocr_extract(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send the image to extract text from.")

async def handle_ocr_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo
    document = update.message.document
    if not photo and not document:
        await update.message.reply_text("Please send an image file.")
        return
    file_obj = None
    if photo:
        file_obj = await photo[-1].get_file()
    elif document:
        file_obj = await document.get_file()
    file_bytes = await file_obj.download_as_bytearray()
    image = Image.open(io.BytesIO(file_bytes))
    text = pytesseract.image_to_string(image)
    await update.message.reply_text(f"Extracted text:\n{text}")

async def get_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send the book name and author.")

async def handle_book_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # For demonstration, just echo back the request
    await update.message.reply_text(f"Fetching book: {text}\n(This is a placeholder response)")

def main():
    application = ApplicationBuilder().token("7776505238:AAEXe1c5hSWYMi4IRvSs0UG4QdbYwDz7qRI").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("translate_line", translate_line))
    application.add_handler(CommandHandler("image_to_pdf", image_to_pdf))
    application.add_handler(CommandHandler("word_to_pdf", word_to_pdf))
    application.add_handler(CommandHandler("merge_pdf", merge_pdf))
    application.add_handler(CommandHandler("professional_translate", professional_translate))
    application.add_handler(CommandHandler("ocr", ocr_extract))
    application.add_handler(CommandHandler("get_book", get_book))

    application.add_handler(MessageHandler(filters.Document.ALL & filters.Regex(r'.*'), handle_file_line_translation))
    application.add_handler(MessageHandler(filters.Document.ALL & filters.Regex(r'.*'), handle_file_after_payment))
    application.add_handler(MessageHandler(filters.Document.ALL & filters.Regex(r'.*'), handle_word_to_pdf))
    application.add_handler(MessageHandler(filters.Document.ALL & filters.Regex(r'.*'), handle_merge_pdf))
    application.add_handler(MessageHandler(filters.Photo.ALL, handle_image_to_pdf))
    application.add_handler(MessageHandler(filters.Photo.ALL, handle_ocr_image))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_payment_screenshot))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_book_request))

    application.run_polling()

if __name__ == '__main__':
    main()
