from openai import OpenAI
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip
import numpy as np
import os

from src.config import OPENAI_API_KEY

class VideoGenerator:
    def __init__(self, inf_dir, video_title, lyrics, timestamps):
        self.inf_dir = inf_dir
        self.prompt = f"Here is the title of a video that includes a song. Please generate an image that matches the mood of the song.:\n{video_title}"
        self.image_path = ""
        self.lyrics = lyrics
        self.timestamps = timestamps
        
        Image.ANTIALIAS = Image.Resampling.LANCZOS
        
    # dalle api로 배경 이미지 생성
    def generate_image(self):
        print("이미지 생성중")
                
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.images.generate(
          model="dall-e-3",
          prompt=self.prompt,
          size="1024x1024",
          quality="hd",
          n=1,
        )

        image_url = response.data[0].url
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data)).convert('RGB')
        self.image_path = self.inf_dir + "/gen_image.jpg"
        image.save(self.image_path, "JPEG")
        print("이미지 생성 완료.")
        
    def create_text_image(self, text, width=1280, height=300, font_size=50, line_spacing=10):
        """
        Pillow를 사용하여 검은색 배경에 흰 텍스트로 구성된 이미지를 생성합니다.
        """
        # 배경을 검은색으로 설정 (불투명)
        img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)

        # 한글과 영어 모두 지원하는 폰트를 지정합니다.
        # 폰트 파일의 경로는 시스템에 맞게 수정하세요.aiku
        try:
            font = ImageFont.truetype("NanumSquareRoundB.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # 텍스트 여러 줄로 나누기
        lines = text.split("\n")

        # 전체 텍스트 높이 계산
        total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] + line_spacing for line in lines)

        # 중앙 정렬 계산 (세로 위치)
        y = (height - total_text_height) // 2

        # 각 줄을 이미지에 그림
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2  # 가로 중앙 정렬
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
            y += bbox[3] - bbox[1] + line_spacing  # 다음 줄로 이동

        return np.array(img)
    
    def generate_video_file(self):
        mr_audio_path = self.inf_dir + "/mdx_extra/audio/no_vocals.wav"
        audio_clip = AudioFileClip(mr_audio_path)
        audio_duration = audio_clip.duration
        
        # 2. 배경 이미지 파일 (ssfw_image.jpg)
        # 배경 이미지를 1280x720 해상도로 리사이즈 후, 오디오 길이에 맞게 설정
        # generation image 
        background_clip = ImageClip(self.image_path).resize((1280, 720)).set_duration(audio_duration)
        
        # === 텍스트 클립 생성 및 타이밍 설정 ===
        text_clips = []
        cnt = 0 
        for lyric, (start_time, end_time) in zip(self.lyrics, self.timestamps):

            if cnt > 0 : 
                start_time -= 2 
                end_time += 4

            img_array = self.create_text_image(lyric, width=1280, height=150, font_size=50)
            clip = ImageClip(img_array).set_duration(end_time - start_time)
            # 하단 중앙에 표시 (화면 높이 720, 텍스트 높이 150, 50픽셀 여백)
            clip = clip.set_position(('center', 720 - 150 - 50)).set_start(start_time)
            #clip = clip.crossfadein(0.5).crossfadeout(0.5)

            text_clips.append(clip)

        # === 최종 영상 클립 합성 ===
        print("영상 클립 합성중")
        final_clip = CompositeVideoClip([background_clip, *text_clips]).set_audio(audio_clip)

        # === 영상 파일 내보내기 ===
        final_clip.write_videofile(f"{self.inf_dir}/output.mp4", fps=24)
        
    def process_all(self):
        self.generate_image()
        self.generate_video_file()