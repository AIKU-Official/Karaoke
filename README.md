# 프로젝트명

📢 2025년 겨울학기 [AIKU](https://github.com/AIKU-Official) 활동으로 진행한 프로젝트입니다
🎉 20##년 1/여름/2/겨울학기 AIKU Conference 열심히상 수상!

## 소개

세상에는 많은 노래가 있고 부르고 싶은 노래도 많습니다. 그러나 노래방은 업데이트가 느립니다. 예능 프로그램에서 타가수나 유튜브에서 일반인이 커버한 노래 같은 경우는 큰 인기를 끌지 않은 이상 노래방에 들어오지 않습니다. 우리가 원하는 노래를 그때 그때 노래방 형태로 만들 수 있다면 어떨까요? 

목표: 유튜브 링크를 넣었을 때 MR, 가사, 이미지가 하나의 영상으로 결과물이 나오는 것이 목표!

## 방법론
### 1. 모델링
- 크롤링: 유튜브 링크를 통해 제목과 mp3파일을 가져옵니다.
  
- 이미지 생성: DALLE에 유튜브 영상 제목을 prompt로 넣어 배경 이미지를 생성합니다.
  
- 유튜브 음원(mp3) 분리: demucs 모델을 이용하여 mp3를 vocals.wav와 no_vocals.wav로 분리합니다.
  
- 가사 & timestep 추출: Whisperx 모델을 통해 vocals.wav에서 가사와 timestamp을 추출합니다.
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
### 모델 학습

## 환경 설정

(Requirements, Anaconda, Docker 등 프로젝트를 사용하는데에 필요한 요구 사항을 나열해주세요)

## 사용 방법

(프로젝트 실행 방법 (명령어 등)을 적어주세요.)

## 예시 결과

(사용 방법을 실행했을 때 나타나는 결과나 시각화 이미지를 보여주세요)

## 팀원

(프로젝트에 참여한 팀원의 이름과 깃헙 프로필 링크, 역할을 작성해주세요)

- [홍길동](홍길동의 github link): (수행한 역할을 나열)
