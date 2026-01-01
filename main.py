import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- AYARLAR ---
URUN_LISTESI = [
     "https://www.bershka.com/tr/f%C4%B1r%C3%A7alanm%C4%B1%C5%9F-efektli-desenli-s%C3%BCveter-c0p200314447.html?colorId=800",
    "https://www.bershka.com/tr/teknik-spor-ceket-c0p189277209.html?colorId=401"
]
HEDEF_BEDEN = "M"
TELEGRAM_TOKEN = "8495759843:AAHsFKuoITm87HdEBUEkAC8QiudWFWlddnc"
CHAT_ID = "1564732604"

def send_telegram_message(message):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": message})
    except: pass

def toplu_kontrol():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        for link in URUN_LISTESI:
            print(f"Kontrol ediliyor: {link}")
            try:
                driver.get(link)
                time.sleep(5) 
                
                xpath = f"//span[normalize-space()='{HEDEF_BEDEN}'] | //button[normalize-space()='{HEDEF_BEDEN}']"
                elements = driver.find_elements(By.XPATH, xpath)
                
                for el in elements:
                    if not el.is_displayed(): continue
                    # Class kontrolü
                    classes = (el.get_attribute("class") or "") + " " + \
                              (el.find_element(By.XPATH, "./..").get_attribute("class") or "")
                    
                    if "disabled" not in classes.lower() and "no-stock" not in classes.lower():
                        msg = f"🚨 MÜJDE! {HEDEF_BEDEN} stokta!\n{link}"
                        print(msg)
                        send_telegram_message(msg)
                        break # Bu linkte bulduk, diğerine geç
                
                time.sleep(2) # Bershka şüphelenmesin diye ufak bekleme
            except: continue
            
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        if driver: driver.quit()

# --- SADECE TEK SEFER ÇALIŞTIR VE BİTİR ---
if __name__ == "__main__":
    toplu_kontrol()