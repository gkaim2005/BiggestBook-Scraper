import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_product_details(driver, sku):
    """
    Navigates to the BiggestBook product page for the given SKU, scrapes the
    product details, and returns them as a dictionary.
    """
    url = f"https://www.biggestbook.com/ui#/itemDetail?itemId={sku}"
    driver.get(url)
    
    # Increase wait time if your connection or site response is slow
    wait = WebDriverWait(driver, 15)
    # Short sleep to let the page settle fully before scraping
    time.sleep(2)
    
    product_name = ""
    description = ""
    specifications = ""
    main_image = ""

    # 1. Extract Product Name
    try:
        product_name_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc"))
        )
        product_name = product_name_elem.text.strip()
    except Exception as e:
        print(f"Error getting product name for SKU {sku}: {e}")

    # 2. Extract Description
    try:
        description_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-desc-info"))
        )
        description = description_elem.text.strip()
    except Exception as e:
        print(f"Error getting description for SKU {sku}: {e}")

    # 3. Extract Specifications by taking a static snapshot of the table
    try:
        specs_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-content div.w-100.mr-4.ng-star-inserted table"))
        )
        # Get the entire HTML of the specs table
        table_html = specs_table.get_attribute("outerHTML")
        
        # Parse with BeautifulSoup to avoid stale element references
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
        
        # Join all specs with newlines so each appears on its own line in the CSV cell
        specifications = "\n".join(all_specs)
    except Exception as e:
        print(f"Error getting specifications for SKU {sku}: {e}")

    # 4. Extract Main Product Image
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
        "Specifications": specifications,  # multiline string
        "Main Image": main_image
    }

def main():
    """
    Reads SKUs from skus.txt, scrapes each product's details, and writes
    the results to products.csv. Each SKU is written as a new row.
    """
    input_file = "skus.txt"
    output_file = "products.csv"
    
    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    
    # Initialize the WebDriver (ensure chromedriver is in your PATH)
    driver = webdriver.Chrome(options=chrome_options)
    
    # Read all SKUs from the input file
    with open(input_file, "r", encoding="utf-8") as f:
        skus = [line.strip() for line in f if line.strip()]
    
    # Open the CSV file with quoting=csv.QUOTE_ALL to preserve multiline fields
    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["SKU", "Product Name", "Description", "Specifications", "Main Image"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        # Process each SKU in the list
        for sku in skus:
            print(f"Scraping SKU: {sku}")
            product_data = get_product_details(driver, sku)
            # Write the product data as a new row in the CSV
            writer.writerow(product_data)
            print(f"Data for SKU {sku} saved.")
    
    driver.quit()
    print(f"All data saved to {output_file}")

if __name__ == "__main__":
    main()
