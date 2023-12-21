import speech_recognition as sr
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import io
import base64
import mysql.connector

recognizer = sr.Recognizer()

def recognize_speech(audio_file):
    with sr.AudioFile(audio_file) as source:
        try:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

            sample_rate, audio = wavfile.read(audio_file)
            num_channels = len(audio.shape)
            if num_channels > 1:
                num_channels = audio.shape[1]
            audio_length = len(audio) / sample_rate
            decibel = 20 * np.log10(np.max(np.abs(audio)))
            bit_depth = audio.dtype.itemsize * 8

            time = np.arange(0, len(audio)) / sample_rate
            plt.figure(figsize=(12, 6))
            plt.subplot(2, 1, 1)
            plt.plot(time, audio, lw=0.5)
            plt.title("Audio Signal")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            audio_signal_bytes = buffer.getvalue()
            audio_signal_base64 = base64.b64encode(audio_signal_bytes).decode('utf-8')

            plt.figure(figsize=(12, 6))
            plt.subplot(2, 1, 1)
            plt.specgram(audio, Fs=sample_rate)
            plt.title("Spectrogram")
            plt.xlabel("Time (s)")
            plt.ylabel("Frequency (Hz)")
            plt.colorbar(label="Intensity (dB)")

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            spectrogram_bytes = buffer.getvalue()
            spectrogram_base64 = base64.b64encode(spectrogram_bytes).decode('utf-8')

            plt.close()  # Close the plot

            # Convert 'float64' types to Python floats
            decibel = float(decibel)
            bit_depth = float(bit_depth)

            # Establish MySQL connection
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Devalla@1234",
                database="speech"
            )
            cursor = conn.cursor()

            # Alter the column type to accommodate larger data
            alter_query = "ALTER TABLE results MODIFY COLUMN spectrogram_base64 LONGTEXT"
            cursor.execute(alter_query)

            insert_query = "INSERT INTO results (text, sample_rate, num_channels, decibel, bit_depth, audio_length, audio_signal_base64, spectrogram_base64) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            data = (text, sample_rate, num_channels, decibel, bit_depth, audio_length, audio_signal_base64, spectrogram_base64)

            cursor.execute(insert_query, data)
            conn.commit()

            cursor.close()
            conn.close()

            return {
                "text": text,
                "sample_rate": sample_rate,
                "num_channels": num_channels,
                "decibel": decibel,
                "bit_depth": bit_depth,
                "audio_length": audio_length,
                "audio_signal_base64": audio_signal_base64,
                "spectrogram_base64": spectrogram_base64
            }

        except sr.UnknownValueError:
            return "Speech not recognized"
        except sr.RequestError as e:
            return f"Recognition request failed: {e}"
