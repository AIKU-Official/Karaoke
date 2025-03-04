import os
import demucs.separate
import subprocess

class AudioProcessor:
    def __init__(self, inf_dir):
        self.audio_dir = inf_dir
    
    # demucs를 이용해 voice와 non voice로 분리
    def separate_audio(self):
        print("Audio source separation start.")
        
        audio_path = self.audio_dir + "/audio.mp3"
        
        if os.path.exists(audio_path):
            print(f"Processing: {audio_path}")
            demucs.separate.main(["--two-stems", "vocals", "-n", "mdx_extra", "--out", self.audio_dir, audio_path])
        else:
            print(f"Source file not found: {audio_path}")
            return
        
        print("Audio source separation complete.")
    
    # 샘플레이트 16000Hz, 모노 채널로 오디오 형식 변환
    def convert_inferance_file(self):
        print(f"Convertion start.")
        
        # 원본 파일
        source_file = self.audio_dir + "/mdx_extra/audio/vocals.wav"
        # 변환 후 저장될 파일
        dest_file = self.audio_dir + "/vocal_p.wav"

        if not os.path.exists(source_file):
            print(f"Source file not found: {source_file}")
            return

        # ffmpeg 명령어 설정: 샘플레이트 16000Hz, 모노 채널
        command = [
            "ffmpeg",
            "-y",              # 기존 파일 덮어쓰기
            "-i", source_file,
            "-ar", "16000",
            "-ac", "1",
            dest_file
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            err = result.stderr.decode("utf-8")
            print(f"Error converting file: {err}")
        else:
            print("Conversion successful.")
            
    def process_all(self):
        self.separate_audio()
        self.convert_inferance_file()