import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_product_details(driver, sku):
    # Construct the URL for the product detail page using the SKU
    url = f"https://www.biggestbook.com/ui#/itemDetail?itemId={sku}"
    driver.get(url)
    
    # Set up an explicit wait
    wait = WebDriverWait(driver, 10)
    
    product_name = ""
    description = ""
    specifications = ""
    main_image = ""

    # Extract Product Name (ID "pd-item-desc" + class "ess-detail-desc")
    try:
        product_name_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc"))
        )
        product_name = product_name_elem.text
    except Exception as e:
        print(f"Error getting product name for SKU {sku}: {e}")

    # Extract Description (div with class "ess-detail-desc-info")
    try:
        description_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-desc-info"))
        )
        description = description_elem.text
    except Exception as e:
        print(f"Error getting description for SKU {sku}: {e}")

    # Extract Specifications from the table with class "text-left ess-detail-table-values"
    try:
        table_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.text-left.ess-detail-table-values"))
        )
        # Find all table rows
        rows = table_elem.find_elements(By.TAG_NAME, "tr")
        
        specs_list = []
        for row in rows:
            # Each row should have at least two <td> cells (label & value)
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                label = cells[0].text.strip()
                value = cells[1].text.strip()
                specs_list.append(f"{label}: {value}")
        
        # Join them into a multiline string
        specifications = "\n".join(specs_list)
    except Exception as e:
        print(f"Error getting specifications for SKU {sku}: {e}")

    # Extract Main Product Image (img with class "ngxImageZoomThumbnail")
    try:
        image_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.ngxImageZoomThumbnail"))
        )
        main_image = image_elem.get_attribute("src")
        # If src starts with "//", prepend "https:"
        if main_image.startswith("//"):
            main_image = "https:" + main_image
    except Exception as e:
        print(f"Error getting main product image for SKU {sku}: {e}")
    
    # Return the collected product details in a dictionary
    return {
        "SKU": sku,
        "Product Name": product_name,
        "Description": description,
        "Specifications": specifications,
        "Main Image": main_image
    }

def main():
    input_file = "skus.txt"       # File containing SKUs (one per line)
    output_file = "products.csv"  # CSV file to save the scraped data
    
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    
    # Initialize the Chrome driver (make sure chromedriver is in your PATH)
    driver = webdriver.Chrome(options=chrome_options)
    
    # Read SKUs from the input file
    with open(input_file, "r", encoding="utf-8") as f:
        skus = [line.strip() for line in f if line.strip()]
    
    # Open a CSV file to write the scraped data
    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["SKU", "Product Name", "Description", "Specifications", "Main Image"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Loop through each SKU, scrape the product details, and write to CSV
        for sku in skus:
            print(f"Scraping SKU: {sku}")
            product_data = get_product_details(driver, sku)
            writer.writerow(product_data)
            print(f"Data for SKU {sku} saved.")
    
    driver.quit()
    print(f"All data saved to {output_file}")

if __name__ == "__main__":
    main()
