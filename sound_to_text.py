import os
import warnings
from faster_whisper import WhisperModel

def transcribe_audio(file_path):

    local_model_path = "./whisper_model"
    
    model = WhisperModel("Systran/faster-whisper-large-v3", device="cuda", compute_type="float16")

    print(f"satrt: {os.path.basename(file_path)}...")
    
    segments, info = model.transcribe(file_path, language="ru", beam_size=1)
    
    full_text = []
    for segment in segments:
        full_text.append(segment.text)
        
    return "".join(full_text)