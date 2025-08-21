# Web Scraper for Product Data  

This project is a Python-based web scraper I built for my internship at Price Reporter to extract product information from **BiggestBook.com** using SKUs. It automates collecting data like product names, descriptions, specifications, shipping details, and images.  

## What My Program Uses  
- **Selenium** → to automate browsing and load dynamic content  
- **BeautifulSoup** → to parse HTML and extract structured data  
- **ThreadPoolExecutor** → to run multiple product scrapers in parallel for much faster performance  
- **CSV** → to save all the final product data in a structured format so it can be utilized  

## How It Works  
1. My program simply reads SKUs from `skus.txt`  
2. For each SKU, the program:  
   - Opens the product page  
   - Checks if the product exists on the website; otherwise, it can be skipped to save time   
   - Extracts all the important details for products that exist(name, description, specs, shipping info, and main image)
   - Handles errors gracefully and allows retry attempts in case HTML takes longer to load and fails to get extracted
3. Writes all product data individually into `products.csv`  

## Deployment Method  
Since scraping large datasets can take hours/days and stress local hardware like my Mac, I deployed this on a rented remote Linux server. Running it on the server allowed me to:  
- Speed up automation with multithreading since remote servers generally have more CPU cores and RAM  
- Let the scraper run for long periods without worrying about my laptop staying on, running out of battery, or overheating
- Store results directly on the server for later use and then download/transfer the scraped data from the server back to my local computer
