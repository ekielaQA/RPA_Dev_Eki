from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import time
import zipfile
import os



@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotsSpareBin Industries Inc.
    Saves the order HTML receipt as PDF file.
    Saves the screenshot of the ordreed robot.
    Embed the screenshot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    close_annoying_modal()
    download_order_file()
    page = browser.page()
    orders = get_orders()
    
    for order in orders:
        fill_the_form(order)
        screenshot = screenshot_robot(order)
        submit_the_order()
        html_receipt = None  # Default value before the if-else block
        print("Before calling store_receipt_as_pdf")
        while page.is_visible("div[class='alert alert-danger']"):
            page.click("button:text('ORDER')", strict=True)
            
        pdf_path = store_receipt_as_pdf(order) #tam gdzie używałam tutaj html_receipt w embed zmienić na tą pdf_path


        # if page.locator(".alert", has_text="Error"): #whle dopóki nie ma sukcesu. zobacz czy div istnieje jeśli błędu nie ma; page is element visible  
        #     page.click("button:text('ORDER')", strict=True)
        #     html_receipt = store_receipt_as_pdf(order)
        # elif page.locator("#receipt").inner_html(): #
        #     html_receipt = store_receipt_as_pdf(order)
        # else: 
        #     html_receipt = store_receipt_as_pdf(order)



        # if page.locator(".alert", has_text="Error"):
        #     page.click("button:text('ORDER')", strict=True)
        # else:
        #     print("Attempting to store receipt as PDF")
        #     html_receipt = store_receipt_as_pdf(order)

        # if screenshot is not None and html_receipt is not None:
        #     embed_screenshot_to_receipt(screenshot, html_receipt, order['Order number'])
        # else:
        #    print(f"Skipping embedding for order {order['Order number']} due to missing files.")
        embed_screenshot_to_receipt(screenshot, pdf_path, order['Order number'])
        order_another_robot()
        
    archive_receipts()
        

def open_robot_order_website():
    """Mavigates to the given URL."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")



def download_order_file():
   """Downloads order template file."""
   http = HTTP()
   http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    """Reads the CSV file as a table and returns orders."""
    csv = Tables()
    orders = csv.read_table_from_csv("orders.csv", header=True) #csv.read_orders_form_csv("orders.csv", header=True)
    return orders 

def close_annoying_modal():
    """Closes the annoying modal."""
    page = browser.page()
    page.click("button:text('OK')")
    
def fill_the_form(order):
    """Fills in the order form and displays the robot preview."""
    page = browser.page()
    page.select_option("#head", order['Head'])
    page.check(f"#id-body-{order['Body']}")
    page.get_by_placeholder("Enter the part number for the legs").fill(order['Legs'])
    page.fill(f"#address", order['Address'])
    time.sleep(1)
    page.click(f"#preview", strict=True)
    
def screenshot_robot(order):
    """Takes & saves the screenshot of the robot for each order number."""
    page = browser.page()
    screenshot_path = f"output/order_number-{order['Order number']}.png"
    page.screenshot(path=screenshot_path)
    return screenshot_path
    
def submit_the_order():
    """Submits the order."""
    page = browser.page()
    page.click(f"button:text('ORDER')", strict=True)
        
def store_receipt_as_pdf(order):
    """Saves HTLM receipt as a PDF file and returns the path to the PDF file."""
    page = browser.page()
    html_receipt = page.locator("#receipt").inner_html()
    if html_receipt is not None:
       pdf = PDF()
       pdf_path = f"output/order-receipt-{order['Order number']}.pdf"
       pdf.html_to_pdf(html_receipt, pdf_path)
    return pdf_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path, order_number): #skąd mi tu ten order_number ie skąd ma się wziąć
    """Embeds the Robot screenshot into the PDF receipt file."""
    pdf = PDF()
    final_receipt_path = f"output/order-receipt-{order_number}.pdf"
    pdf.add_files_to_pdf(files=[screenshot_path], target_document=final_receipt_path, append=True)

def order_another_robot():
    """Proceeds with ordering the next Robot and closes the annoying modal."""
    page = browser.page()
    page.click("#order-another")
    close_annoying_modal()

def archive_receipts():
    """Creates the ZIP archive with all PDF files."""
    archive = Archive()
    archive.archive_folder_with_zip(folder='output', include='*.pdf', archive_name='receipts_files.zip')
