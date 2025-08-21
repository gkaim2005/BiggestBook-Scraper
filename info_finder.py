import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed

def product_exists(driver, sku):
    url = f"https://www.biggestbook.com/ui#/itemDetail?itemId={sku}"
    driver.get(url)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc"))
        )
        return True
    except Exception:
        return False

def scrape_product(driver, sku):
    url = f"https://www.biggestbook.com/ui#/itemDetail?itemId={sku}"
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    time.sleep(2)

    product_name = ""
    description = ""
    specifications = ""
    shipping_info = ""
    main_image = ""

    try:
        el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc")))
        product_name = el.text.strip()
    except Exception as e:
        print(f"Error getting product name for SKU {sku}: {e}")

    try:
        el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-desc-info")))
        description = el.text.strip()
    except Exception as e:
        print(f"Error getting description for SKU {sku}: {e}")

    try:
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-content div.w-100.mr-4.ng-star-inserted table")))
        html = table.get_attribute("outerHTML")
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("tbody tr")
        specs_list = []
        for row in rows:
            label = row.select_one("td.ess-detail-table-name")
            value = row.select_one("td.ess-detail-table-values")
            if label and value:
                specs_list.append(f"{label.get_text(strip=True)}: {value.get_text(strip=True)}")
        specifications = "\n".join(specs_list)
    except Exception as e:
        print(f"Error getting specifications for SKU {sku}: {e}")

    try:
        shipping_label = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td#pd-weight-label.text-left.ess-detail-table-name")))
        shipping_table = shipping_label.find_element(By.XPATH, "./ancestor::table")
        shipping_html = shipping_table.get_attribute("outerHTML")
        soup_ship = BeautifulSoup(shipping_html, "html.parser")
        rows_ship = soup_ship.select("tbody tr")
        ship_items = []
        for row in rows_ship:
            label = row.select_one("td.ess-detail-table-name")
            value = row.select_one("td.ess-detail-table-values")
            if label and value:
                ship_items.append(f"{label.get_text(strip=True)}: {value.get_text(strip=True)}")
        shipping_info = "\n".join(ship_items)
    except Exception as e:
        print(f"Error getting shipping weight & dimensions for SKU {sku}: {e}")

    try:
        img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.ngxImageZoomThumbnail")))
        main_image = img.get_attribute("src")
        if main_image.startswith("//"):
            main_image = "https:" + main_image
    except Exception as e:
        print(f"Error getting main product image for SKU {sku}: {e}")

    return {
        "SKU": sku,
        "Product Name": product_name,
        "Description": description,
        "Specifications": specifications,
        "Shipping Weight & Dimensions": shipping_info,
        "Main Image": main_image
    }

def handle_sku(sku):
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=opts)
    try:
        if not product_exists(driver, sku):
            print(f"SKU {sku} is not listed. Skipping.")
            return None
        return scrape_product(driver, sku)
    except Exception as e:
        print(f"Error processing SKU {sku}: {e}")
        return None
    finally:
        driver.quit()

def main():
    input_file = "skus.txt"
    output_file = "products.csv"

    with open(input_file, "r", encoding="utf-8") as f:
        skus = [line.strip() for line in f if line.strip()]

    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = [
            "SKU",
            "Product Name",
            "Description",
            "Specifications",
            "Shipping Weight & Dimensions",
            "Main Image"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        max_workers = 9
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(handle_sku, sku): sku for sku in skus}
            for fut in as_completed(futures):
                sku = futures[fut]
                try:
                    product_data = fut.result()
                    if product_data is not None:
                        writer.writerow(product_data)
                        print(f"Data for SKU {sku} saved.")
                    else:
                        print(f"SKU {sku} skipped.")
                except Exception as e:
                    print(f"Error processing SKU {sku}: {e}")

    print(f"All data saved to {output_file}")

if __name__ == "__main__":
    main()
