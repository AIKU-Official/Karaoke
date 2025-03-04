from src.audio_downloader import AudioDownloader
from src.audio_processor import AudioProcessor
from src.video_generator import VideoGenerator
from src.lyrics_generator import LyricsGenerator


def main(id):
    inf_dir = f"/home/proj-karaoke/datasets/inference/{id}"

    # 음원 다운로드
    downloader = AudioDownloader(inf_dir=inf_dir)
    video_title = downloader.manage_download()

    # GPU 3번 사용
    # os.environ["CUDA_VISIBLE_DEVICES"] = "3"

    # vocie/non voice 분리 및 음원 전처리
    processor = AudioProcessor(inf_dir=inf_dir)
    processor.process_all()

    # GPU 세팅 초기화
    # os.environ["CUDA_VISIBLE_DEVICES"] = initial_cuda_devices
    # torch.cuda.device_count()

    # 타임스탬프와 함께 가사 생성
    lyrics_generator = LyricsGenerator(inf_dir=inf_dir, gpu_id=[5, 6, 7], batch_size=4)
    lyrics, timestamps = lyrics_generator.process_all()

    # 가라오케 영상 생성
    generator = VideoGenerator(
        inf_dir=inf_dir, video_title=video_title, lyrics=lyrics, timestamps=timestamps
    )
    generator.process_all()


if __name__ == "__main__":
    id = 1001

    main(id)
