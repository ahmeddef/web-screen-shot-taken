import time
import os
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import re
from tqdm import tqdm

# وظيفة لقراءة الروابط من ملف وإضافة البروتوكول إذا كان مفقودًا
def read_links_from_file(file_path):
    with open(file_path, 'r') as file:
        links = file.readlines()
    
    # إضافة البروتوكول إذا كان مفقودًا
    links = [add_protocol(link.strip()) for link in links]
    return links

# وظيفة لإضافة البروتوكول (http:// أو https://)
def add_protocol(url):
    # إذا كان الرابط لا يحتوي على http:// أو https:// نضيف https:// افتراضيًا
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    return url

# وظيفة لالتقاط لقطة شاشة للموقع
def take_screenshot(url, output_dir):
    # إعداد Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # وضع التشغيل بدون واجهة رسومية
    options.add_argument('--disable-gpu')  # تعطيل تسريع الرسومات
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # تسجيل المعلومات
    logging.info(f"Open the URL: {url}")

    # فتح الرابط
    driver.get(url)

    # الانتظار قليلاً لتحميل الصفحة
    time.sleep(3)  # يمكن ضبط الوقت بناءً على سرعة الإنترنت

    # تنظيف الرابط لاستخدامه في اسم الصورة
    clean_url = re.sub(r'https?://(www\.)?', '', url)  # إزالة https:// و www. إن وجدت
    clean_url = clean_url.replace('/', '_')  # استبدال / بـ _
    screenshot_path = os.path.join(output_dir, f"{clean_url}.jpg")

    # التقاط صورة الشاشة
    driver.save_screenshot(screenshot_path)
    
    logging.info(f"successful saving screen shot: {screenshot_path}")

    # إغلاق المتصفح بعد التقاط الصورة
    driver.quit()

# دالة لتنظيم المدخلات من سطر الأوامر
def parse_arguments():
    parser = argparse.ArgumentParser(description="A tool to take screenshots of websites from links in a file.")
    parser.add_argument('-w', '--websites', type=str, required=True, help="urls file path (LIKE: links.txt)")
    parser.add_argument('-o', '--output', type=str, required=True, help="For a folder to save images")
    return parser.parse_args()

# البرنامج الرئيسي
def main():
    # إعداد logging لعرض الأنشطة في الخلفية
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    # تحليل المدخلات من سطر الأوامر
    args = parse_arguments()

    # التأكد من وجود المجلد لحفظ الصور
    os.makedirs(args.output, exist_ok=True)

    # قراءة الروابط من الملف
    links = read_links_from_file(args.websites)

    # عرض شريط تقدم باستخدام tqdm
    with tqdm(total=len(links), desc="loading", unit="URL") as pbar:
        # التقاط لقطات الشاشة لكل رابط
        for link in links:
            take_screenshot(link, args.output)
            pbar.update(1)  # تحديث شريط التقدم بعد كل رابط

if __name__ == "__main__":
    main()
