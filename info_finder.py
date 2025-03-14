import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_product_details(driver, sku):
    #Gets wesbite url and uses 
    url = f"https://www.biggestbook.com/ui#/itemDetail?itemId={sku}"
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    
    product_name = ""
    description = ""
    specifications = ""
    main_image = ""

    # 1. Extract Product Name
    try:
        product_name_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc"))
        )
        product_name = product_name_elem.text
    except Exception as e:
        print(f"Error getting product name for SKU {sku}: {e}")

    # 2. Extract Description
    try:
        description_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-desc-info"))
        )
        description = description_elem.text
    except Exception as e:
        print(f"Error getting description for SKU {sku}: {e}")

    # 3. Extract Specifications (example approach)
    try:
        specs_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-content div.w-100.mr-4.ng-star-inserted table"))
        )
        rows = specs_table.find_elements(By.CSS_SELECTOR, "tbody tr")
        all_specs = []
        for row in rows:
            try:
                label = row.find_element(By.CSS_SELECTOR, "td.ess-detail-table-name").text.strip()
                value = row.find_element(By.CSS_SELECTOR, "td.ess-detail-table-values").text.strip()
                all_specs.append(f"{label}: {value}")
            except Exception as e:
                print(f"Error parsing a spec row for SKU {sku}: {e}")
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
    input_file = "skus.txt"
    output_file = "products.csv"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    
    with open(input_file, "r", encoding="utf-8") as f:
        skus = [line.strip() for line in f if line.strip()]
    
    # Use quoting=csv.QUOTE_ALL to ensure multiline fields are preserved.
    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["SKU", "Product Name", "Description", "Specifications", "Main Image"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for sku in skus:
            print(f"Scraping SKU: {sku}")
            product_data = get_product_details(driver, sku)
            writer.writerow(product_data)
            print(f"Data for SKU {sku} saved.")
    
    driver.quit()
    print(f"All data saved to {output_file}")

if __name__ == "__main__":
    main()
