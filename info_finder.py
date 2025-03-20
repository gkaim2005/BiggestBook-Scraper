import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_product_listed(driver, sku):
    """
    Quickly checks if the product page for the given SKU shows the expected product element.
    Returns True if the product is listed; otherwise, False.
    """
    url = f"https://www.biggestbook.com/ui#/itemDetail?itemId={sku}"
    driver.get(url)
    try:
        # Use a short wait (5 seconds) for the product name element.
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc"))
        )
        return True
    except Exception:
        return False

def get_product_details(driver, sku):
    # Construct the URL for the product page using the SKU.
    url = f"https://www.biggestbook.com/ui#/itemDetail?itemId={sku}"
    driver.get(url)
    
    wait = WebDriverWait(driver, 15)
    time.sleep(2)
    
    product_name = ""
    description = ""
    specifications = ""
    shipping_info = ""
    main_image = ""

    # 1. Extract Product Name.
    try:
        product_name_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc"))
        )
        product_name = product_name_elem.text.strip()
    except Exception as e:
        print(f"Error getting product name for SKU {sku}: {e}")

    # 2. Extract Product Description.
    try:
        description_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-desc-info"))
        )
        description = description_elem.text.strip()
    except Exception as e:
        print(f"Error getting description for SKU {sku}: {e}")

    # 3. Extract Specifications.
    try:
        specs_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-content div.w-100.mr-4.ng-star-inserted table"))
        )
        table_html = specs_table.get_attribute("outerHTML")
        soup = BeautifulSoup(table_html, "html.parser")
        rows = soup.select("tbody tr")
        all_specs = []
        for row in rows:
            label_cell = row.select_one("td.ess-detail-table-name")
            value_cell = row.select_one("td.ess-detail-table-values")
            if label_cell and value_cell:
                label_text = label_cell.get_text(strip=True)
                value_text = value_cell.get_text(strip=True)
                all_specs.append(f"{label_text}: {value_text}")
        specifications = "\n".join(all_specs)
    except Exception as e:
        print(f"Error getting specifications for SKU {sku}: {e}")

    # 4. Extract Shipping Weight & Dimensions.
    try:
        shipping_label_elem = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "td#pd-weight-label.text-left.ess-detail-table-name")
            )
        )
        shipping_table_elem = shipping_label_elem.find_element(By.XPATH, "./ancestor::table")
        shipping_html = shipping_table_elem.get_attribute("outerHTML")
        soup_shipping = BeautifulSoup(shipping_html, "html.parser")
        rows_shipping = soup_shipping.select("tbody tr")
        shipping_info_list = []
        for row in rows_shipping:
            label_cell = row.select_one("td.ess-detail-table-name")
            value_cell = row.select_one("td.ess-detail-table-values")
            if label_cell and value_cell:
                label_text = label_cell.get_text(strip=True)
                value_text = value_cell.get_text(strip=True)
                shipping_info_list.append(f"{label_text}: {value_text}")
        shipping_info = "\n".join(shipping_info_list)
    except Exception as e:
        print(f"Error getting shipping weight & dimensions for SKU {sku}: {e}")

    # 5. Extract Main Product Image.
    try:
        image_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.ngxImageZoomThumbnail"))
        )
        main_image = image_elem.get_attribute("src")
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

def process_sku(sku):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # First check if the product is listed.
        if not is_product_listed(driver, sku):
            print(f"SKU {sku} is not listed. Skipping.")
            return None  # Return None if product isn't listed.
        else:
            data = get_product_details(driver, sku)
    except Exception as e:
        print(f"Error processing SKU {sku}: {e}")
        data = None
    finally:
        driver.quit()
    return data

def main():
    input_file = "skus.txt"   # File containing the list of SKUs.
    output_file = "products.csv"
    
    # Read all SKUs from input file.
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
        
        max_workers = 9  # Set the number of workers.
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_sku, sku): sku for sku in skus}
            for future in as_completed(futures):
                sku = futures[future]
                try:
                    product_data = future.result()
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
