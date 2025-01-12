from playwright.sync_api import sync_playwright
import os
import requests
import re
import shutil

def scrape_images(base_url, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(base_url)

        page.wait_for_selector("section:has-text('Nasze gazetki')")

        offer_elements = page.locator("section:has-text('Nasze gazetki') a:has-text('OFERTA WAŻNA OD')")
        offer_count = offer_elements.count()
        if offer_count == 0:
            print("No offers found on the homepage.")
            return

        print(f"Found {offer_count} offers.")
        offer_links = []

        for offer_index in range(offer_count):
            offer_link = offer_elements.nth(offer_index).get_attribute("href")
            offer_links.append(offer_link)
            if not offer_link:
                continue
        print(offer_links)

        for link in offer_links:
            print(f"Processing offer: {link}")
            page.goto(link)
            page.wait_for_selector('body')

            date_match = re.search(r'oferta-wazna-od-([\d-]+)-do-([\d-]+)', link)
            if date_match:
                date_range = f"od-{date_match.group(1)}-do-{date_match.group(2)}"
                print(f"Extracted date range: {date_range}")
                specific_output_folder = os.path.join(output_folder, date_range)
                os.makedirs(specific_output_folder, exist_ok=True)
            else:
                print("Could not extract date range from the URL. Skipping this offer.")
                continue

            page.goto(link)
            page.wait_for_selector('body')

            page_number = 1
            previous_page_content = None
            identical_page_count = 0
            downloaded_images = set()

            while True:
                if page_number > 1 and page_number % 2 != 0:
                    print(f"Skipping odd page number {page_number}")
                    page_number += 1
                    continue

                current_url = f"{link.rsplit('/page/', 1)[0]}/page/{page_number}"

                try:
                    page.goto(current_url)
                    page_number += 1

                    page.wait_for_selector("body")

                    final_url = page.url
                    print(f"Redirected to: {final_url}")

                    correct_url = final_url.replace("/ar/0/page/", "/view/flyer/page/")
                    print(f"Using correct URL format: {correct_url}")
                    correct_url = correct_url[:-1]
                    correct_url = correct_url + f"{page_number}"

                    page.goto(correct_url)
                    print(f"Attempting to scrape: {correct_url}")

                    current_page_content = page.locator("div.page__wrapper").first.inner_html()

                    if previous_page_content and current_page_content == previous_page_content:
                        identical_page_count += 1
                        print(f"Identical content detected. Count: {identical_page_count}")
                    else:
                        identical_page_count = 0

                    if identical_page_count > 2:
                        print("No new content found for 3 consecutive pages. Stopping.")
                        break

                    page.wait_for_selector("img")

                    img_elements = page.locator('img')
                    count = img_elements.count()

                    for i in range(count):
                        img_url = img_elements.nth(i).get_attribute("src")
                        if img_url and img_url.endswith(".jpg") and img_url not in downloaded_images:
                            print(f"Downloading image {i + 1}: {img_url}")
                            try:
                                img_data = requests.get(img_url).content
                                img_filename = os.path.join(specific_output_folder,
                                                            f'page_{page_number}_image_{i + 1}.jpg')
                                with open(img_filename, 'wb') as img_file:
                                    img_file.write(img_data)
                                print(f"Image {i + 1} from page {page_number} saved.")

                                downloaded_images.add(img_url)

                            except Exception as e:
                                print(f"Failed to download {img_url}: {e}")

                    previous_page_content = current_page_content

                except Exception as e:
                    print(f"Error loading page {current_url}: {e}")
                    break

        browser.close()

website_url = "https://www.lidl.pl/"
output_directory = "C:\\Users\\Marta\\Desktop\\scrape"
# folders = os.listdir(output_directory)
# for folder in folders:
#     shutil.rmtree(os.path.join(output_directory, folder))

scrape_images(website_url, output_directory)
