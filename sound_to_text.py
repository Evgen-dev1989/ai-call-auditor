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



if __name__ == '__main__':
    FOLDER_ID = '1dpKG-eaFg2glOovkI4sYgLyPo3mW9Ilg' 
    SAVE_DIR = r'F:\it\Python\files'  

    AUDIO_EXTENSIONS = ('.mp3', '.wav', '.m4a', '.flac', '.ogg')
    
    audio_file = None
    for file in os.listdir(SAVE_DIR):
        if file.lower().endswith(AUDIO_EXTENSIONS):
            audio_file = os.path.join(SAVE_DIR, file)
            print(f"find files: {file}")
            break 

    if audio_file:
        text = transcribe_audio(audio_file)

        print(text)
        
        output_txt = os.path.join(SAVE_DIR, "result.txt")
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"\n2. text save in {output_txt}")
    else:
        print(f"In {SAVE_DIR} empty {AUDIO_EXTENSIONS}")