from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import re
import os

# ================== 설정 ==================
URL = "https://www.gangnamunni.com/events?q=%EB%B3%B4%ED%86%A1%EC%8A%A4"
DEBUG = True
SCROLL_PAUSE_TIME = 2  # 스크롤 후 대기 시간
# ==========================================

def setup_driver():
    """Chrome 드라이버 설정"""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options
    )
    return driver

def scroll_and_load_all(driver):
    """페이지 끝까지 스크롤하며 모든 콘텐츠 로드"""
    print("페이지를 스크롤하며 콘텐츠를 로딩합니다...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # 천천히 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        
        # 더보기 버튼 찾아서 클릭 시도
        try:
            more_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
            for btn in more_buttons:
                btn_text = btn.text.strip()
                if "더보기" in btn_text or "더 보기" in btn_text or "more" in btn_text.lower():
                    driver.execute_script("arguments[0].click();", btn)
                    print("더보기 버튼 클릭!")
                    time.sleep(2)
                    break
        except Exception as e:
            pass
        
        # 새로운 높이 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # 한 번 더 시도
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("더 이상 로드할 콘텐츠가 없습니다.")
                break
        
        last_height = new_height

def save_page_source(driver):
    """디버그용 페이지 소스 저장"""
    try:
        with open('page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"✅ page.html 저장 완료: {os.path.abspath('page.html')}")
    except Exception as e:
        print(f"❌ 페이지 소스 저장 실패: {e}")

def extract_price(text):
    """텍스트에서 가격 추출"""
    # 할인가 우선 추출 (예: 175,000원)
    match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*원', text)
    if match:
        return match.group(1).replace(',', '')
    
    # 숫자만 있는 경우
    match = re.search(r'(\d{1,3}(?:,\d{3})*)', text)
    if match:
        return match.group(1).replace(',', '')
    
    return ""

def extract_rating(text):
    """텍스트에서 평점 추출 (예: 9.8, 10)"""
    # 평점 패턴: 숫자.숫자 또는 숫자만
    match = re.search(r'(\d+\.\d+|\d+)', text)
    if match:
        rating = match.group(1)
        # 10점 만점 기준 (0~10 사이)
        try:
            rating_float = float(rating)
            if 0 <= rating_float <= 10:
                return rating
        except:
            pass
    return ""

def find_items_with_selectors(driver, selectors):
    """여러 셀렉터로 항목 찾기"""
    for selector in selectors:
        try:
            items = driver.find_elements(By.CSS_SELECTOR, selector)
            if items and len(items) > 3:  # 최소 3개 이상 찾았을 때
                print(f"✅ 항목 발견: {selector} ({len(items)}개)")
                return items, selector
        except Exception:
            continue
    return [], None

def extract_data(driver):
    """데이터 추출"""
    print("\n데이터 수집 시작...")
    
    # 다양한 셀렉터 시도 (카드 전체)
    ITEM_SELECTORS = [
        "a[href*='/events/']",  # 이벤트 링크
        "div[class*='event']",  # event 클래스 포함
        "div[class*='card']",   # card 클래스 포함
        "article",
        "li[class*='item']",
    ]
    
    items, used_selector = find_items_with_selectors(driver, ITEM_SELECTORS)
    
    if not items:
        print("❌ 항목을 찾을 수 없습니다. page.html을 확인하세요.")
        return []
    
    data_list = []
    
    print(f"\n총 {len(items)}개 항목 처리 중...\n")
    
    for idx, item in enumerate(items, 1):
        try:
            title = ""
            price = ""
            rating = ""
            
            # 시술명 찾기 - h2[role="doc-subtitle"]
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, 'h2[role="doc-subtitle"]')
                title = title_elem.text.strip()
            except:
                # 대체 방법: h2 태그
                try:
                    title_elem = item.find_element(By.TAG_NAME, 'h2')
                    title = title_elem.text.strip()
                except:
                    pass
            
            # 가격 찾기 - h3 태그 (가격은 보통 h3에)
            try:
                h3_elements = item.find_elements(By.TAG_NAME, 'h3')
                for h3 in h3_elements:
                    h3_text = h3.text.strip()
                    if '원' in h3_text or re.search(r'\d{1,3}(?:,\d{3})+', h3_text):
                        price = extract_price(h3_text)
                        if price:
                            break
            except:
                pass
            
            # 평점 찾기 - span 태그에서
            try:
                span_elements = item.find_elements(By.TAG_NAME, 'span')
                for span in span_elements:
                    span_text = span.text.strip()
                    # 평점으로 보이는 패턴
                    pattern = r'^\d+\.\d+$|^10$|^\d$'
                    if re.match(pattern, span_text):
                        rating = extract_rating(span_text)
                        if rating:
                            break
            except:
                pass
            
            # 평점을 못 찾았으면 전체 텍스트에서 찾기
            if not rating:
                full_text = item.text
                # ⭐ 다음에 나오는 숫자 찾기
                lines = full_text.split('\n')
                for i, line in enumerate(lines):
                    if '⭐' in line or '★' in line:
                        # 같은 줄 또는 다음 줄에서 평점 찾기
                        if i < len(lines):
                            rating = extract_rating(lines[i])
                            if not rating and i + 1 < len(lines):
                                rating = extract_rating(lines[i + 1])
                            if rating:
                                break
            
            # 가격을 못 찾았으면 전체 텍스트에서 찾기
            if not price:
                full_text = item.text
                for line in full_text.split('\n'):
                    if '원' in line:
                        price = extract_price(line)
                        if price:
                            break
            
            # 시술명도 못 찾았으면 전체 텍스트에서 첫 줄 사용
            if not title:
                lines = item.text.split('\n')
                for line in lines[:3]:
                    if line and len(line) > 3 and not any(x in line for x in ['서울', '⭐', '평점', '리뷰']):
                        title = line.strip()
                        break
            
            if title and price:
                data_list.append([title, price, rating if rating else ""])
                print(f"{idx}. {title[:30]}... → {price}원 (평점: {rating if rating else 'N/A'})")
        
        except Exception as e:
            if DEBUG:
                print(f"항목 {idx} 처리 오류: {e}")
            continue
    
    return data_list

def save_to_csv(data_list, save_dir='data/gangnamsis'):
    """CSV 파일로 저장"""
    try:
        # 폴더 생성 (없으면)
        os.makedirs(save_dir, exist_ok=True)
        
        # 타임스탬프 파일명 생성
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'gangnamsis_{timestamp}.csv'
        filepath = os.path.join(save_dir, filename)
        
        # CSV 저장
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['시술종류', '가격', '평점'])
            writer.writerows(data_list)
        
        print(f"\n✅ 완료! 총 {len(data_list)}개 데이터를 '{filename}'에 저장했습니다.")
        print(f"📂 파일 위치: {os.path.abspath(filepath)}")
    except Exception as e:
        print(f"❌ CSV 저장 실패: {e}")

def main():
    driver = None
    try:
        # 드라이버 설정
        driver = setup_driver()
        
        # 페이지 로드
        print(f"페이지 로딩 중: {URL}")
        driver.get(URL)
        time.sleep(3)
        
        # 스크롤하며 모든 콘텐츠 로드
        scroll_and_load_all(driver)
        
        # 디버그용 페이지 소스 저장
        if DEBUG:
            save_page_source(driver)
        
        # 데이터 추출
        data_list = extract_data(driver)
        
        # CSV 저장
        if data_list:
            save_to_csv(data_list)
        else:
            print("\n❌ 추출된 데이터가 없습니다.")
            print("💡 page.html 파일을 확인하여 정확한 셀렉터를 찾아주세요.")
        
        # 브라우저 유지
        input("\n브라우저를 닫으려면 엔터키를 누르세요...")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()