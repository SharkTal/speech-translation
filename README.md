# Speech Translation and Conversion Tool

This project provides a simple interface for converting MP3 and MP4 files to WAV format and translating the audio content from Chinese to other languages using Azure Cognitive Services.

## Features

- Convert MP3 and MP4 files to WAV format.
- Translate Chinese speech to English, Spanish, French, and German.
- Save translations to a text file.

## Prerequisites

- Python 3.6 or higher
- Azure Cognitive Services subscription key and region
- `azure-cognitiveservices-speech` Python package
- `gradio` Python package
- `pydub` Python package

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/speech-translation.git
   cd speech-translation

2. Install the required packages:
   ```bash
  pip install -r requirements.txt

3. Set up your Azure Cognitive Services subscription key and region in the `speech_translation.py` file.
    ```bash
    pip install -r requirements.txt

4. Run the application:
   ```bash
   python speech_translation.py