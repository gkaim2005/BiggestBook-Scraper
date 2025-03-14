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

    # 1. Extract Product Name: using id="pd-item-desc" with class="ess-detail-desc"
    try:
        product_name_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pd-item-desc.ess-detail-desc"))
        )
        product_name = product_name_elem.text
    except Exception as e:
        print(f"Error getting product name for SKU {sku}: {e}")

    # 2. Extract Description: div with class="ess-detail-desc-info"
    try:
        description_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-desc-info"))
        )
        description = description_elem.text
    except Exception as e:
        print(f"Error getting description for SKU {sku}: {e}")

    # 3. Extract Specifications:
    # Locate the specifications table using a simplified selector and iterate through its rows.
    try:
        specs_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ess-detail-content div.w-100.mr-4.ng-star-inserted table"))
        )
        # Get all rows in the table body
        rows = specs_table.find_elements(By.CSS_SELECTOR, "tbody tr")
        all_specs = []
        for row in rows:
            try:
                # Extract the label from <td class="ess-detail-table-name">
                label = row.find_element(By.CSS_SELECTOR, "td.ess-detail-table-name").text.strip()
                # Extract the value from <td class="ess-detail-table-values">
                value = row.find_element(By.CSS_SELECTOR, "td.ess-detail-table-values").text.strip()
                all_specs.append(f"{label}: {value}")
            except Exception as e:
                print(f"Error parsing a spec row for SKU {sku}: {e}")
        # Join all specs with newlines so each appears on its own line in the CSV cell
        specifications = "\n".join(all_specs)
    except Exception as e:
        print(f"Error getting specifications for SKU {sku}: {e}")

    # 4. Extract Main Product Image: img with class="ngxImageZoomThumbnail"
    try:
        image_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.ngxImageZoomThumbnail"))
        )
        main_image = image_elem.get_attribute("src")
        # If src is relative (starting with "//"), prepend "https:"
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
