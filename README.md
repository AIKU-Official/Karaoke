# Karaoke

📢 2025년 겨울학기 [AIKU](https://github.com/AIKU-Official) 활동으로 진행한 프로젝트입니다

## 소개

세상에는 많은 노래가 있고 부르고 싶은 노래도 많습니다. 그러나 노래방은 업데이트가 느립니다. 예능 프로그램에서 타가수나 유튜브에서 일반인이 커버한 노래 같은 경우는 큰 인기를 끌지 않은 이상 노래방에 들어오지 않습니다. 우리가 원하는 노래를 그때 그때 노래방 형태로 만들 수 있다면 어떨까요? 

목표: 유튜브 링크를 넣었을 때 정확한 MR, 가사, 이미지가 하나의 영상으로 잘 나오면 성공!

## 방법론
### 1. 모델링
- 크롤링: 유튜브 링크를 통해 제목과 mp3파일을 가져옵니다.
  
- 이미지 생성: DALLE에 유튜브 영상 제목을 prompt로 넣어 배경 이미지를 생성합니다.
  
- 유튜브 음원(mp3) 분리: demucs 모델을 이용하여 mp3를 vocals.wav와 no_vocals.wav로 분리합니다.
  
- 가사 & timestep 추출: Whisperx 모델을 통해 vocals.wav에서 가사와 timestamp을 추출합니다.
  ![image](https://github.com/user-attachments/assets/47d2cd4e-0bd3-4504-9069-419b2cb5dc0b)
  - 기존에는 오디오 첫 30초만 듣고 language detecting 하여 해당하는 phoneme model을 선택했지만, 단어마다 language detecting 하여 phoneme model 선택하도록 변경
  - input audio :
    - wav file, 16000Hz sampling rate, monotype
  - VAD :
    - audio 파일 안에서 인간의 목소리가 나오는 부분을 추출한다
    - 일정 길이(10-30초)에 맞춰서 오디오를 잘라서 chunk 를 만든다
  - Whisper :
    - audio chunk 를 넣어서 transcript 생성
  - Phoneme model :
    - audio chunk 를 넣어서 transcript & time stamp 생성
  - Forced alignment
    - whisper, phoneme model 의 결과물을 비교하여 정렬 과정 수행
  - output :
    - Transcript + word-level timestamps
- 노래방 영상 완성: 이미지, no_vocals.wav, 가사, timestamp을 합쳐 최종 노래방 영상을 완성합니다.
### 2. 모델 학습
![image](https://github.com/user-attachments/assets/8ebc3ca7-b310-4de2-998e-34e44dc62443)
![image](https://github.com/user-attachments/assets/98e5a045-760b-41fb-8707-b7b7d80e7892)
- 100 epoch, lr 5e-5, ADAMW warmup 500 step,
- WER :
    - best model : 0.7
    - latest model : 0.64
- validation loss 가 가장 낮았던 checkpoint 를 최종적으로 선택

## 결과

validation loss 가 증가하려고 해서 overfitting 되었음을 확인 

validation loss 가 가장 낮았던 checkpoint 를 최종적으로 선택 

- 결과 분석
    - 당신과는 천천히 (장범준)
        - WER : 19.44 %
        - CER : 9.02 %
    - …사랑했잖아… (고경표)
        - WER: 16.67%
        - CER: 8.48%
        - whoa 와 같은 추임새 제거 했을 때
            - WER: 14.47%
            - CER: 4.43%
    - 봄여름가을겨울 (빅뱅)
        - WER: 50.23%
        - CER: 30.60%
            - la la la → 랄랄라 랄라라 랄라라
            - 가을 타 → 카이 타
            - 비스듬히 씩 → 비스듬식
            - 노래를 부를 때 생략하거나 과장되게 가사를 부르는 경우일수록 WER, CER 이 높았음

## 환경 설정

`environment.yml` 및 `requirements.txt` 참고해 주시길 바랍니다.

## 사용 방법

- youtube 검색을 위해 쿠키 파일이 필요합니다. Netscape 쿠키를 `cookies.txt`에 저장해 주시길 바랍니다.

- Dall-E 사용을 위한 API 키가 필요합니다. `.env` 파일 생성 후, `OPENAI_API_KEY`로 지정해주면 됩니다.

```
OPEN_API_KEY="your_api_key"
```

main.py를 실행한 후 youtube url 또는 쿼리를 넣어 노래방 영상을 생성할 수 있습니다.
```
$ python main.py
```

## 예시 결과

<p align="center">
<img src="https://github.com/user-attachments/assets/2d5074f1-b0b6-4ce7-a1d4-b89a6fc5c0a4" width="49%">
<img src="https://github.com/user-attachments/assets/d50bba40-df24-408f-bb0c-f6b3ec79ea8b" width="49%">
</p>

## 팀원
  | 팀원                            | 역할                                       |
| ----------------------------- | ---------------------------------------- |
| [권도영](https://github.com/douyoung89) |   dataset 전처리 & 모델 fine-tuning    |
| [김민준](https://github.com/ddomjun)     |    dataset 수집/전처리 & 음원분리/영상변환   |
| [구영서](https://github.com/andless2004)        |    dataset 수집 & 전체 pipeline 정리 & github 정리   |
