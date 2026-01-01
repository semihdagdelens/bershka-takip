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
                
                # --- GÜNCELLENMİŞ SEÇİCİ ---
                # Sadece <li> (liste elemanı) içindeki span veya buttonları arıyoruz.
                # Bershka bedenleri genelde <ul> -> <li> içinde tutar.
                xpath = f"//li//span[normalize-space()='{HEDEF_BEDEN}'] | //li//button[normalize-space()='{HEDEF_BEDEN}']"
                elements = driver.find_elements(By.XPATH, xpath)
                
                found_real_stock = False

                for el in elements:
                    if not el.is_displayed(): continue # Görünür değilse atla
                    
                    # Elementin ve üst elementlerin classlarını al
                    parent = el.find_element(By.XPATH, "./..")
                    grandparent = parent.find_element(By.XPATH, "./..")
                    
                    classes = (el.get_attribute("class") or "") + " " + \
                              (parent.get_attribute("class") or "") + " " + \
                              (grandparent.get_attribute("class") or "")
                    classes = classes.lower()

                    # --- DEBUG LOG (Hata Ayıklama) ---
                    # Eğer yanlış alarm verirse GitHub loglarında bu satırı arayacağız
                    html_snippet = el.get_attribute("outerHTML")
                    print(f"Bulunan 'M' elementi HTML: {html_snippet}")
                    print(f"Class listesi: {classes}")

                    # --- ELEME MANTIĞI ---
                    # 1. 'disabled', 'no-stock', 'out-of-stock' varsa ATLA
                    if "disabled" in classes or "no-stock" in classes or "out-of-stock" in classes:
                        print("-> Elendi: Stok yok (Disabled/No-Stock)")
                        continue
                    
                    # 2. Eğer element bir 'beden tablosu' (guide) butonuysa ATLA
                    if "guide" in classes or "ruler" in classes or "modal" in classes:
                        print("-> Elendi: Beden tablosu veya modal")
                        continue

                    # 3. Eğer elementin tıklanabilirliği şüpheliyse
                    # Bershka'da stokta olan ürünün parent'ı genellikle 'selectable' veya benzeri bir şey olur
                    # Ama garanti olsun diye biz sadece NEGATİF kontrol yapalım şimdilik.

                    print("-> ✅ EŞLEŞTİ! Stok var görünüyor.")
                    found_real_stock = True
                    break 
                
                if found_real_stock:
                    msg = f"🚨 MÜJDE! {HEDEF_BEDEN} stokta!\n{link}"
                    print(msg)
                    send_telegram_message(msg)
                
                time.sleep(2)
            except Exception as e:
                print(f"Link hatası: {e}")
                continue
            
    except Exception as e:
        print(f"Genel Hata: {e}")
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    toplu_kontrol()
