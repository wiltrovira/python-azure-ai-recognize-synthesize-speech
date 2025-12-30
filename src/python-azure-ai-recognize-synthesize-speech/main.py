from dotenv import load_dotenv
from datetime import datetime
import os
from pathlib import Path

# Import namespaces
import azure.cognitiveservices.speech as speech_sdk


def main():
    try:
        global speech_config

        # Get Configuration Settings
        ENV_PATH = Path(__file__).resolve().parent / ".env"  # Path to .env file
        load_dotenv(dotenv_path=ENV_PATH)  # Load .env file

        cog_key = os.getenv("COG_SERVICE_KEY")  # Get cognitive service key
        cog_region = os.getenv("COG_SERVICE_REGION")  # Get cognitive service region

        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(
            cog_key, cog_region
        )  # Create speech configuration

        print(
            "Ready to use speech service in:", speech_config.region
        )  # Print the region being used

        # Get spoken input
        command = TranscribeCommand()  # Transcribe spoken command
        if command.lower() == "what time is it?":
            TellTime()

    except Exception as ex:
        print(ex)


def TranscribeCommand():
    command = ""

    # Configure speech recognition
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    print("Habla ahora..")

    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()  # Recognize speech
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:  # Check result
        command = speech.text  # Get recognized text
        print(command)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    # Return the command
    return command


def TellTime():
    now = datetime.now()
    response_text = "Son las {}:{:02d}".format(now.hour, now.minute)

    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = "es-CO-GonzaloNeural"  # Set voice
    speech_synthesizer = speech_sdk.SpeechSynthesizer(
        speech_config
    )  # Create synthesizer

    # Synthesize spoken output
    # https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=stt
    # https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
    responseSsml = " \
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' \
            xml:lang='es-CO'> \
            <voice name='es-CO-GonzaloNeural'> \
                {} \
                <break strength='weak'/> \
                Hora de terminar este laboratorio! \
            </voice> \
        </speak>".format(
        response_text
    )  # Create SSML response

    speak = speech_synthesizer.speak_ssml_async(responseSsml).get()  # Synthesize speech

    if (
        speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted
    ):  # Check result
        print(speak.reason)  # Print reason if not completed

    # Print the response
    print(response_text)


if __name__ == "__main__":
    main()
