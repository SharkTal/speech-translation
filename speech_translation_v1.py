import os
import time
import azure.cognitiveservices.speech as speechsdk
import gradio as gr
from pydub import AudioSegment


def mp3_to_wav(input_file):
    """
    Convert an MP3 or MP4 file to WAV format.

    :param input_file: The input MP3 or MP4 file.
    :return: The converted WAV file.
    """
    # Get the file extension
    file_extension = os.path.splitext(input_file.name)[1].lower()

    # Load the audio file
    if file_extension == ".mp3":
        audio = AudioSegment.from_mp3(input_file.name)
    elif file_extension == ".mp4":
        audio = AudioSegment.from_file(input_file.name, format="mp4")
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    # Export as WAV file
    wav_file_path = input_file.name.replace(file_extension, ".wav")
    audio.export(wav_file_path, format="wav")

    return wav_file_path

def recognize_from_long_audio_file(audio_file_path, to_language):
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=os.environ.get("SPEECH_KEY"),
        region=os.environ.get("SPEECH_REGION"),
    )
    speech_translation_config.speech_recognition_language = "zh-CN"  # zh-Hans does not work for some reason

    speech_translation_config.add_target_language(to_language)

    audio_config = speechsdk.audio.AudioConfig(
        filename=audio_file_path
    )
    translation_recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=speech_translation_config, audio_config=audio_config
    )

    translations = []

    def recognized_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            print("Recognized: {}".format(evt.result.text))
            print("""Translated into '{}': {}""".format(
                to_language, 
                evt.result.translations[to_language]))
               # Append the recognized language to the translated text
            translated_text = "{} (Original language: {})".format(
            evt.result.translations[to_language],
            evt.result.text
        )
            translations.append(evt.result.translations[to_language])
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(evt.result.no_match_details))
        elif evt.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
            else:
                print("Recognition canceled but not due to an error.")

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the translation recognizer
    translation_recognizer.recognized.connect(recognized_callback)
    translation_recognizer.session_stopped.connect(stop_cb)
    translation_recognizer.canceled.connect(stop_cb)

    # Start continuous recognition
    translation_recognizer.start_continuous_recognition()

    while not done:
        time.sleep(0.5)

    # Stop recognition
    translation_recognizer.stop_continuous_recognition()

    # Save translations to a file
    output_file = f"{os.path.splitext(audio_file_path)[0]}_translation.txt"
    print(f"Attempting to write {len(translations)} translations to {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        for translation in translations:
            print(f"Writing translation: {translation}")
            f.write(translation + "\n")

    print(f"Translations saved to {output_file}")
    return output_file

def create_interface():
    with gr.Blocks() as demo:
        gr.Markdown("Convert MP3 and MP4 to WAV")
        with gr.Row():
            mp3_file = gr.File(label="Upload MP3 OR MP4 File", type="filepath")
            wav_file = gr.File(label="Download WAV File")
        convert_button = gr.Button("Convert")
        convert_button.click(mp3_to_wav, inputs=mp3_file, outputs=wav_file)

        clear_button = gr.Button("Clear")
        clear_button.click(lambda: (None, None), inputs=[], outputs=[mp3_file, wav_file])

        gr.Markdown("Azure Speech Translation- Chinese to English, es,fr,de, Only WAV audio supported")
        with gr.Row():
            audio_file = gr.File(label="Upload WAV format Audio File", type="filepath")
            language = gr.Dropdown(["en", "es", "fr", "de"], label="Select Target Language")
        output_file = gr.File(label="Download Translated File")
        translate_button = gr.Button("Translate")
        translate_button.click(recognize_from_long_audio_file, inputs=[audio_file, language], outputs=output_file)

    demo.launch()

if __name__ == "__main__":
    create_interface()