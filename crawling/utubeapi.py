import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()


class YouTubeCommentCrawler:
    def __init__(self, api_key):
        """
        YouTube Data API v3를 사용한 댓글 크롤러

        Args:
            api_key: YouTube Data API 키
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def extract_video_id(self, url):
        """
        YouTube URL에서 video ID 추출

        Args:
            url: YouTube 비디오 URL
        Returns:
            video_id: 추출된 비디오 ID
        """
        if 'v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        else:
            return url

    def get_comments(self, video_id, max_results=5000):
        """
        특정 비디오의 댓글 가져오기 (대댓글 제외)

        Args:
            video_id: YouTube 비디오 ID
            max_results: 가져올 최대 댓글 수
        Returns:
            comments: 댓글 리스트
        """
        comments = []

        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_results),
                order="relevance"  # 'time' 또는 'relevance'
            )

            while request and len(comments) < max_results:
                response = request.execute()

                for item in response['items']:
                    # 최상위 댓글만 수집
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        '댓글': comment['textDisplay'],
                        '좋아요': comment['likeCount']
                    })

                    if len(comments) >= max_results:
                        break

                # 다음 페이지
                if 'nextPageToken' in response and len(comments) < max_results:
                    request = self.youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=min(100, max_results - len(comments)),
                        pageToken=response['nextPageToken'],
                        order="relevance"
                    )
                else:
                    break

        except HttpError as e:
            print(f"오류 발생: {e}")
            if e.resp.status == 403:
                print("댓글이 비활성화되어 있거나 API 할당량을 초과했습니다.")

        return comments[:max_results]

    def save_to_csv(self, comments, filename=None, save_dir="data"):
        """
        댓글을 CSV 파일로 저장

        Args:
            comments: 댓글 리스트
            filename: 저장할 파일명
            save_dir: 저장할 폴더 경로 (기본값: data)
        """
        # 저장 폴더 생성 (없으면)
        os.makedirs(save_dir, exist_ok=True)
        
        if not filename:
            filename = f"youtube_comments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # 전체 경로 생성
        filepath = os.path.join(save_dir, filename)
        
        df = pd.DataFrame(comments)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"'{filepath}' 파일로 저장되었습니다. (총 {len(comments)}개 댓글)")


# 사용 예시
if __name__ == "__main__":
    # 환경 변수에서 API 키 로드
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    if not API_KEY:
        print("❌ API 키를 찾을 수 없습니다!")
        print("📝 .env 파일에 YOUTUBE_API_KEY를 설정해주세요.")
        exit(1)

    # 크롤러 초기화
    crawler = YouTubeCommentCrawler(API_KEY)

    # YouTube URL 또는 비디오 ID
    video_url = input('youtube_url을 입력하시오: ')
    video_id = crawler.extract_video_id(video_url)

    # 댓글 가져오기 (원하는 개수로 변경 가능)
    print(f"비디오 ID: {video_id}의 댓글을 가져오는 중...")
    comments = crawler.get_comments(video_id, max_results=5000)  # 5000개로 변경

    # 결과 출력
    print(f"\n총 {len(comments)}개의 댓글을 가져왔습니다.\n")
    for i, comment in enumerate(comments[:5], 1):
        print(f"{i}. {comment['댓글'][:50]}... (좋아요: {comment['좋아요']})\n")

    # CSV로 저장
     # crawler.save_to_csv(comments, save_dir="data/utube")