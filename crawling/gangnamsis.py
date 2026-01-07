from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import re

# ================== [여기만 수정하세요] ==================
import os
URL = "https://www.gangnamunni.com/events?q=%EC%A7%80%EB%B0%A9%EC%84%B1%ED%98%95"
DEBUG = True
 

# 1. '더보기' 버튼의 선택자 (우클릭 > Copy > Copy Selector)
MORE_BUTTON_SELECTOR = "#screenMain > div.flex.flex-col.pt-4 > div.p-4 > button"  # 예시입니다. 꼭 바꿔주세요!
 


# 2. 상품 카드 (반복되는 박스)
ITEM_SELECTOR = ".item-card" 

# 3. 제목
TITLE_SELECTOR = ".title-text"

# 4. 가격
PRICE_SELECTOR = ".price-bold"
# ========================================================

# 디버그 및 후보 셀렉터들 (ITEM_SELECTOR 등 정의 이후에 위치)
DEBUG = True

CANDIDATE_ITEM_SELECTORS = [
    ITEM_SELECTOR,
    ".event-card",
    ".card",
    "ul li",
    "div.list > div",
    "article",
    "a[href*='/events/']",
]

CANDIDATE_TITLE_SELECTORS = [
    TITLE_SELECTOR,
    ".title",
    "h3",
    "h2",
]

CANDIDATE_PRICE_SELECTORS = [
    PRICE_SELECTOR,
    ".price",
    ".cost",
    ".amount",
]

def run_crawler():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True) # 브라우저 꺼짐 방지 옵션
    options.add_argument("--start-maximized") # 창 최대화 (버튼 잘 눌리게)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(URL)
    time.sleep(3) # 페이지 로딩 대기

    # --- [파트 1: 천천히 스크롤하며 더보기 클릭] ---
    print("천천히 스크롤하며 더보기 버튼을 찾습니다...")
    
    while True:
        # 1. 천천히 스크롤 내리기 (사람처럼)
        current_height = driver.execute_script("return window.pageYOffset;")
        target_height = driver.execute_script("return document.body.scrollHeight;")
        
        # 500픽셀씩 끊어서 바닥까지 내림
        for i in range(current_height, target_height, 500):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(0.3) # 내리는 속도 조절

        try:
            # 2. 더보기 버튼이 보일 때까지 잠깐 대기 (최대 3초)
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # 버튼이 클릭 가능한 상태가 될 때까지 기다림
            more_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, MORE_BUTTON_SELECTOR))
            )
            
            # 3. 버튼 클릭
            # 일반 click()이 안 먹힐 때를 대비해 자바스크립트로 직접 클릭
            driver.execute_script("arguments[0].click();", more_btn)
            print("더보기 클릭 완료!")
            time.sleep(2) # 새 데이터 로딩 대기
            
        except Exception as e:
            # 더보기 버튼이 더 이상 안 보이면 스크롤을 한 번 더 끝까지 내리고 종료
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("더보기 버튼을 찾을 수 없습니다. (수집 단계로 이동)")
            break

    # --- [파트 2: 데이터 수집] ---
    print("데이터 수집 시작...")
    # 디버그: 페이지 소스 저장
    try:
        with open('page.html', 'w', encoding='utf-8') as pf:
            pf.write(driver.page_source)
        if DEBUG:
            print(f"page.html로 페이지 소스 저장됨 ({os.path.abspath('page.html')})")
    except Exception as e:
        print("페이지 소스 저장 실패:", e)

    def find_any(selectors):
        for sel in selectors:
            try:
                found = driver.find_elements(By.CSS_SELECTOR, sel)
                if found:
                    return sel, found
            except Exception:
                continue
        return None, []

    sel_used, items = find_any([ITEM_SELECTOR])
    if not items:
        print("기본 셀렉터로 항목을 찾지 못했습니다. 후보 셀렉터들로 검사합니다...")
        sel_used, items = find_any(CANDIDATE_ITEM_SELECTORS)
        if sel_used:
            print(f"탐지된 항목 셀렉터: {sel_used} (개수: {len(items)})")
        else:
            print("후보 셀렉터들에서도 항목을 찾지 못했습니다. page.html을 확인하세요.")

    data_list = []

    for item in items:
        try:
            try:
                title = item.find_element(By.CSS_SELECTOR, TITLE_SELECTOR).text.strip()
            except:
                title = item.text.strip().split('\n')[0]

            try:
                price_raw = item.find_element(By.CSS_SELECTOR, PRICE_SELECTOR).text.strip()
            except:
                price_raw = item.text

            # 가격 숫자만 추출 (콤마 포함 가능)
            m = re.search(r"[\d,]+", price_raw)
            if m:
                price = m.group(0).replace(',', '').strip()
            else:
                price = ''

            data_list.append([title, price])
        except Exception:
            continue

    # --- [파트 3: 저장] ---
    with open('result.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['시술종류', '가격'])
        writer.writerows(data_list)
        
    print(f"완료! 총 {len(data_list)}개 저장됨.")
    
    # [중요] 프로그램이 바로 안 꺼지게 엔터키 입력 대기
    input("브라우저를 닫으려면 엔터키를 누르세요...") 
    driver.quit()

if __name__ == "__main__":
    run_crawler()