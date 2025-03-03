import time
import yt_dlp

class AudioDownloader:
    def __init__(self, inf_dir):
        self.audio_dir = inf_dir
        self.audio_type = 'mp3'
    
    # query를 바탕으로 youtube에서 검색
    # return url, video_title
    def search_youtube(self, query, result_index=1):    
        ydl_opts = {
            'default_search': f'ytsearch{result_index}',
            'quiet': True,
            'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)
            if 'entries' in result and result['entries']:
                video = result['entries'][result_index-1]
                return video['webpage_url'], video['title']

        return None, None

    # download audio file 
    # return video_title
    def download_audio(self, youtube_url):
        time.sleep(2)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.audio_dir}/audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_type,
                'preferredquality': '192',  # bit rate; aduio_type='wav'일 시 무시됨
            }],
            # sampling rate 16000Hz
            'postprocessor_args': [
                '-ar', str(16000)
            ],
            # Mono(1)/Stereo(2) type
            'postprocessor_args': [
                '-ac', '1'  # Mono
            ],
            # Netscape 쿠키 파일 설정 필요
            'cookiefile': 'cookies.txt'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)

        title = info.get("title", "Not found")
        return title

    def manage_download(self):
        mode = int(input("1. Input youtube url\n2. Input query\n>> "))
        
        # youtube url 존재하면 바로 다운로드드
        if mode == 1:
            youtube_url = input("url: ")

            try:
                video_title = self.download_audio(youtube_url)
                print(f"Download {video_title}")

                return video_title
            except Exception as e:
                print(e)

                return None

        # query 기반으로 youtube 검색
        elif mode == 2:
            query = input("query: ")
            
            # 최대 10번까지 재검색 허용
            for i in range(1, 11):
                youtube_url, video_title = self.search_youtube(query, i)

                accept = input(f"Accpet \"{video_title}\"? (y/n)")
                if accept == 'y':
                    try:
                        video_title = self.download_audio(youtube_url)
                        print(f"Download {video_title}")

                        return video_title
                    except Exception as e:
                        print(e)

                        return None

            print("Not found")
            
            return None