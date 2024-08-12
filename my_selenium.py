import time
import threading
import random
import platform  # Import platform module
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import chromedriver_autoinstaller
from random import shuffle

# Automatically install the ChromeDriver and get its path
chromedriver_autoinstaller.install()

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
]

def create_driver(user_agent):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Check if the OS is Ubuntu and enable headless mode if true
    if platform.system() == 'Linux' and 'ubuntu' in platform.version().lower():
        chrome_options.add_argument("--headless")

    chrome_options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scroll_down(driver):
    for _ in range(10):
        driver.execute_script("window.scrollBy(0, 300);")
        random_delay(1, 3)

def random_delay(min_seconds=1, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))

def perform_human_like_actions(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    random_delay(0.5, 1.0)
    offset_x = random.randint(-element.size['width'] // 4, element.size['width'] // 4)
    offset_y = random.randint(-element.size['height'] // 4, element.size['height'] // 4)
    actions.move_by_offset(offset_x, offset_y).click().perform()
    print(f"Clicked at offset ({offset_x}, {offset_y})")
    actions.move_by_offset(-offset_x, -offset_y).perform()

def run_thread(links, thread_id):
    MAX_DRIVERS = 5  # Reduce the number of drivers per thread
    drivers = []

    for i in range(min(len(links), MAX_DRIVERS)):
        driver = create_driver(user_agents[i % len(user_agents)])
        drivers.append(driver)
        try:
            driver.get(links[i])
            perform_human_like_actions(driver, driver.find_element(By.XPATH, '//body'))  # Adjust based on actual elements
        except Exception as e:
            print(f"Error with driver {i}: {e}")

    run_time = random.randint(600, 1800)
    start_time = time.time()

    while time.time() - start_time < run_time:
        sleep_time = random.randint(60, 300)
        time.sleep(sleep_time)
        for j in range(len(drivers)):
            try:
                sleep_time = random.randint(1, 10)
                time.sleep(sleep_time)
                drivers[j].refresh()
                perform_human_like_actions(drivers[j], drivers[j].find_element(By.XPATH, '//body'))  # Adjust based on actual elements
                drivers[j].save_screenshot(f"screenshot_{thread_id}_{time.time()}.png")
                print(f"Screenshot taken for URL {links[j]} by thread {thread_id}")
            except Exception as e:
                print(f"Error with driver {j}: {e}")

    for drv in drivers:
        drv.quit()

def main():
    user_agent = random.choice(user_agents)
    driver = create_driver(user_agent)
    driver.get("https://www.youtube.com/@mediapipe_and_workout/videos")
    driver.implicitly_wait(10)
    
    links = []
    while len(links) < 5:
        elements = driver.find_elements(By.XPATH, '//a[@id="video-title-link"]')
        new_links = [element.get_attribute('href') for element in elements]
        links.extend([link for link in new_links if link not in links])
        print(f"Number of unique links: {len(links)}")
        scroll_down(driver)
    
    driver.quit()

    # Shuffle the links to randomize their order
    shuffle(links)
    
    chunk_size = 8  # Adjust chunk size to reduce load
    chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]
    
    threads = []
    for i, chunk in enumerate(chunks):
        thread = threading.Thread(target=run_thread, args=(chunk, i))
        threads.append(thread)
        random_delay(60, 300)
        thread.start()

        if len(threads) >= 5:  # Reduce the number of concurrent threads
            for t in threads:
                t.join()
            threads = []
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
