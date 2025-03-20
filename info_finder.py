import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_product_details(driver, sku):
    #url hold the full URL but allows the SKU to be a variable that loads into each specific product page
    url = f"https://www.biggestbook.com/ui#/itemDetail?itemId={sku}"
    driver.get(url)
    
    #Depending on how slow the page loads I set a 15 second wait in case it takes longer to pull info
    wait = WebDriverWait(driver, 15)
    #Short sleep timer to make sure the page is settled before any scrapping for product information begins
    time.sleep(2)
    
    product_name = ""
    description = ""
    specifications = ""
    shipping_info = ""
    main_image = ""

    #Gets full product name and prints error if unsuccessful
    try:
        product_name_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc"))
        )
        product_name = product_name_elem.text.strip()
    except Exception as e:
        print(f"Error getting product name for SKU {sku}: {e}")

    #Gets product description and prints error if unsuccessful
    try:
        description_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-desc-info"))
        )
        description = description_elem.text.strip()
    except Exception as e:
        print(f"Error getting description for SKU {sku}: {e}")

    #Gets product specifications in "label: value" format and prints error if unsuccessful and takes static snapshot of the table to prevent stale elements in process
    try:
        specs_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-content div.w-100.mr-4.ng-star-inserted table"))
        )
        #Takes the HTML from the specifications table from product page
        table_html = specs_table.get_attribute("outerHTML")
        
        #Parses using BeautifulSoup to avoid any stale element references that may occur
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
        
        #Joins all the specifications on a new line within one cell in the SKU row 
        specifications = "\n".join(all_specs)
    except Exception as e:
        print(f"Error getting specifications for SKU {sku}: {e}")

    try:
        # Locate the shipping label cell.
        shipping_label_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td#pd-weight-label.text-left.ess-detail-table-name"))
        )
        # Find the parent row (assumes the shipping info is in the same row).
        shipping_row = shipping_label_elem.find_element(By.XPATH, "./ancestor::tr")
        shipping_html = shipping_row.get_attribute("outerHTML")
        soup_shipping = BeautifulSoup(shipping_html, "html.parser")
        label_cell = soup_shipping.select_one("td#pd-weight-label.text-left.ess-detail-table-name")
        value_cell = soup_shipping.select_one("td.text-left.ess-detail-table-values")
        if label_cell and value_cell:
            shipping_info = f"{label_cell.get_text(strip=True)}: {value_cell.get_text(strip=True)}"
    except Exception as e:
        print(f"Error getting shipping weight & dimensions for SKU {sku}: {e}")

    #Gets the one big image that appears on every product page and prints error if unsuccessful
    try:
        image_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.ngxImageZoomThumbnail"))
        )
        main_image = image_elem.get_attribute("src")
        if main_image.startswith("//"):
            main_image = "https:" + main_image
    except Exception as e:
        print(f"Error getting main product image for SKU {sku}: {e}")
    
    return{
        "SKU": sku, #Single line string
        "Product Name": product_name, #Single line string
        "Description": description, #Single line string
        "Specifications": specifications, #Multi-line string since each specification is on a new line within cell
        "Shipping Weight & Dimensions": shipping_info,
        "Main Image": main_image #Single line string
    }

def main():
    input_file = "skus.txt" #Reads the input file skus.txt that contains list of any amount of SKUs
    output_file = "products.csv" #Output file that will list the organized product information in a CSV table 
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options) #Enables webdriver 
    
    #Reads each individual line in skus.txt input file
    with open(input_file, "r", encoding="utf-8") as f: 
        skus = [line.strip() for line in f if line.strip()]
    
    #Opens CSV file and allows for multiline fields with quoting for my specifications list
    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["SKU", "Product Name", "Description", "Specifications", "Shipping Weight & Dimensions", "Main Image"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        #Processes and saves product data in a new row in products.csv for each SKU pulled from skus.txt
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
