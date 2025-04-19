
Built by https://www.blackbox.ai

---

```markdown
# Multifunctional Telegram Bot

## Project Overview

The Multifunctional Telegram Bot is a powerful and versatile chatbot built using Python that integrates various functionalities such as file translation, image and document conversion, and text extraction from images. This bot utilizes popular libraries like `googletrans` for translation, `PyPDF2` for PDF manipulation, and `pytesseract` for Optical Character Recognition (OCR). It is designed to assist users with their document and conversion needs directly through the Telegram messaging platform.

## Installation

To get started with this bot, follow the steps below to set it up in your local environment.

### Prerequisites

1. **Python 3.7 or higher**: Ensure that Python is installed on your system.
2. **pip**: Python package installer should be available.

### Steps to Install

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Install the required dependencies:

   ```bash
   pip install python-telegram-bot googletrans PyPDF2 pillow img2pdf pytesseract python-docx
   ```

3. Ensure that `pytesseract` is properly configured. You might need to install Tesseract OCR on your machine. Follow the [Tesseract installation guide](https://github.com/tesseract-ocr/tesseract).

4. Set your Telegram bot API token in the code (replace `YOUR_BOT_API_TOKEN`):

   ```python
   application = ApplicationBuilder().token("YOUR_BOT_API_TOKEN").build()
   ```

## Usage

1. Start your bot through Telegram. Use the `/start` command to initialize.

2. Use the following commands to interact with the bot:
   - `/translate_line`: Translate a file line by line (supports Arabic and English).
   - `/image_to_pdf`: Convert sent image files to a PDF.
   - `/word_to_pdf`: Convert sent Word documents (.doc or .docx) to a PDF.
   - `/merge_pdf`: Merge multiple PDF files into one.
   - `/professional_translate`: Request professional file translation (requires payment).
   - `/ocr`: Extract text from an image file.
   - `/get_book`: Request information about books by name and author.

## Features

- **File Translation**: Translate text files between Arabic and English.
- **File Conversion**: Convert images and Word documents to PDF format.
- **PDF Merging**: Combine multiple PDF files into a single document.
- **Professional Translation**: Accessible upon payment.
- **Optical Character Recognition**: Extract text from images.
- **Book Information**: Request details about books by name and author.

## Dependencies

This project requires the following Python packages, specified in `requirements.txt`:

- `python-telegram-bot`
- `googletrans`
- `PyPDF2`
- `Pillow`
- `img2pdf`
- `pytesseract`
- `python-docx`

To install all dependencies at once, you can create a `requirements.txt` file from the list above or use the command provided in the Installation section.

## Project Structure

```
.
├── bot.py                     # Main bot logic and command handlers
├── requirements.txt           # List of Python dependencies
└── README.md                  # Project documentation
```

Feel free to explore the bot's functionalities and contribute if you'd like to enhance its capabilities!
```