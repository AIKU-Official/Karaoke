from src import whisperx
import torch
from itertools import chain
import json

class LyricsGenerator:
    def __init__(self, inf_dir, gpu_id, batch_size=4):        
        self.inf_dir = inf_dir
        self.json_path = inf_dir + "/alignment.json"
        
        self.batch_size = batch_size    # reduce if low on GPU mem
        self.gpu_id = gpu_id
        self.device = None
        self.model = None
        
        self.audio = None
        self.transcript = None
        self.segments = []
        self.sentence = []
        self.word = []
        self.sentence_ts = []
        self.word_ts = []
        
    def transcribe(self):        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        compute_type = "float32"
        whisper_model = "large-v2"
        vocal_file = self.inf_dir + "/mdx_extra/audio/vocals.wav"
        
        self.model = whisperx.load_model(whisper_model, self.device, device_index=self.gpu_id, compute_type=compute_type)
        self.audio = whisperx.load_audio(vocal_file)
        
        self.transcript = self.model.transcribe(self.audio, batch_size=self.batch_size, chunk_size=20)
        
        print("Before alignment, just whisper: ")
        print(self.transcript["segments"])
    
    def alignment(self):
        result = []
        
        # , desc="Aligning..."
        for idx, segment in enumerate(self.transcript['segments']):
            seg = [segment]
            model_a, metadata = whisperx.load_align_model(language_code=segment["language"], device=self.device)
            alignment = whisperx.align(seg, model_a, metadata, self.audio, self.device, return_char_alignments=False)
            result.append(alignment["segments"])    
            
        output = list(chain(*result))
        
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        
        print(f"{self.json_path}이 저장되었습니다. ")

    def load_json(self, interval=10):
        """
        JSON 데이터를 불러와 단어의 timestamp를 기준으로 10초 단위로 문장을 나눕니다.
        """
        with open(self.json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        current_segment = []
        segment_text = []
    
        # `json_data`가 리스트일 경우 첫 번째 요소에서 words
        if isinstance(json_data, list):
            words = []
            for segment in json_data:
                words.extend(segment["words"])  # 모든 words 합치기
        else:
            words = json_data["words"]  # 일반적인 dict 구조일 경우
    
        segment_start = words[0]["start"]
    
        for word in words:
            if word["start"] - segment_start >= interval:
                self.segments.append({
                    "start": segment_start,
                    "end": current_segment[-1]["end"],
                    "text": " ".join(segment_text),
                    "words": current_segment
                })
                current_segment = []
                segment_text = []
                segment_start = word["start"]
    
            current_segment.append(word)
            segment_text.append(word["word"])
    
        if current_segment:
            self.segments.append({
                "start": segment_start,
                "end": current_segment[-1]["end"],
                "text": " ".join(segment_text),
                "words": current_segment
            })


    def json_to_lyrics(self, max_length=30):
        """
        문자열이 특정 길이를 초과하면 띄어쓰기 부분을 기준으로 개행 문자를 삽입하는 함수.

        Args:
            sentences (list): 변환할 문자열 리스트
            max_length (int): 최대 허용 길이 (기본값: 30)

        Returns:
            list: 개행이 삽입된 문자열 리스트
        """
        sentences = [str(segment["text"]) for segment in self.segments]
        for text in sentences:
            if len(text) > max_length:
                mid = len(text) // 2  # 문자열의 중간 위치 찾기

                # 공백 위치 찾기 (중앙에 가까운 것 선택)
                space_index = [i for i, char in enumerate(text) if char == " "]
                closest_space = min(space_index, key=lambda x: abs(x - mid), default=None)

                if closest_space is not None:
                    # 띄어쓰기 위치에 개행 문자 삽입
                    new_str = text[:closest_space] + "\n" + text[closest_space + 1:]
                else:
                    # 띄어쓰기가 없으면 기존 방식 유지
                    new_str = text[:mid] + "\n" + text[mid:]

                self.sentence.append(new_str)
            else:
                self.sentence.append(text)
                
        self.word = [str(word["word"]) for segment in self.segments for word in segment["words"]]
        
        # time stamp from json 
        self.sentence_ts = [(segment["start"], segment["end"]) for segment in self.segments]
        self.word_ts = [(word["start"], word['end']) for segment in self.segments for word in segment["words"]]
        
    def process_all(self):
        self.transcribe()
        self.alignment()
        
        self.load_json()
        self.json_to_lyrics()
        
        lyrics = self.sentence # or word 
        timestamps = self.sentence_ts # or word_ts 
        
        return lyrics, timestamps
        