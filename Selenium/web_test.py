from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "http://127.0.0.1:9000/"


def build_driver(headless: bool = False) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")

    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=opts)


def wait_for_new_assistant_message(driver: webdriver.Chrome, wait: WebDriverWait, prev_count: int) -> str:
    """
    chatMessages içinde .message.assistant sayısı artana kadar bekler ve son mesajın text'ini döndürür.
    """
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#chatMessages .message.assistant")) > prev_count)
    messages = driver.find_elements(By.CSS_SELECTOR, "#chatMessages .message.assistant .message-content")
    return messages[-1].text.strip() if messages else ""


def main():
    driver = build_driver(headless=False)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(BASE_URL)

        # Sayfa temel elementleri hazır mı?
        wait.until(EC.visibility_of_element_located((By.ID, "chatMessages")))
        wait.until(EC.visibility_of_element_located((By.ID, "messageInput")))
        wait.until(EC.element_to_be_clickable((By.ID, "sendButton")))

        # Önce mevcut assistant mesaj sayısını al (sayfada 1 tane başlangıç mesajı var)
        prev_assistant_count = len(driver.find_elements(By.CSS_SELECTOR, "#chatMessages .message.assistant"))

        # Mesaj gönder
        message_input = driver.find_element(By.ID, "messageInput")
        message_input.clear()
        message_input.send_keys("Merhaba! Selenium ile test mesajı gönderiyorum.")

        driver.find_element(By.ID, "sendButton").click()

        # Typing indicator eklenirse, kaybolmasını bekle (olmayan durumda da sorun yok)
        try:
            wait.until(EC.presence_of_element_located((By.ID, "typingIndicator")))
            wait.until(EC.invisibility_of_element_located((By.ID, "typingIndicator")))
        except TimeoutException:
            # typingIndicator hiç gelmemiş olabilir veya hızlı geçmiştir; problem değil
            pass

        # Yeni assistant mesajını bekle
        reply_text = wait_for_new_assistant_message(driver, wait, prev_assistant_count)

        print("\n✅ Test bitti. Son assistant mesajı:")
        print(reply_text)

        input("\nTarayıcı açık. Kapatmak için Enter...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
