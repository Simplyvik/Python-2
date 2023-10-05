from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import time
import os


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    #browser = browser()
    open_robot_order_website()
    close_annoying_modal()
    orders= download_robot_orders()
    for row in orders:
        print(row)
        fill_the_form(row)
        submit_the_order(row["Order number"])
    archive_receipts()

    close_robot_order_website()

def open_robot_order_website():

    #browser = browser()

    # Open a new browser in headless mode
    #browser.new_browser(headless=False)

    # Navigate to a website
    browser.goto('https://robotsparebinindustries.com/#/robot-order')
    
    #return browser

def close_annoying_modal():
    #get rid of pop-up
    page=browser.page()
    page.click(".btn.btn-dark")


def close_robot_order_website():
    # Close the browser at the end
    page=browser.page()
    page.close()
    print("closing the brwser")

def download_robot_orders():
    http_local= HTTP()
    orders_csv= http_local.download('https://robotsparebinindustries.com/orders.csv', overwrite=True)
    orders_local= Tables()  
    orders_table= orders_local.read_table_from_csv('orders.csv',header=True)
    return orders_table

def fill_the_form(row):
    page = browser.page()
    index = row["Head"]
    page.select_option("id=head", row["Head"])
    #page.select_option_by_index("Head", row["Head"])
    #page.select_option("Head", row["Head"])
    #browser.select_options_by("Head","index",row["Head"])
    body = "id=" + "id-body-" + row["Body"]
    print(body)
    page.click(body)
    page.fill("input[placeholder='Enter the part number for the legs']",row["Legs"])
    page.fill("id=address",row["Address"])

def submit_the_order(order_id):
    page=browser.page()
    while True:
        try:
            page.click("id=order") #,timeout=5000
            #time.sleep(1)
            page.wait_for_selector("id=receipt",timeout=1000)
            pdf= store_receipt_as_pdf(order_id)
            screenshot= screenshot_robot(order_id)
            embed_screenshot_to_receipt(screenshot,pdf)
            page.click("id=order-another")
            close_annoying_modal()
            break
        except:
            time.sleep(1)
            print("Faild to enter order")

def store_receipt_as_pdf(order_id):
    page=browser.page()
    http=HTTP()
    pdf=PDF()
    element= page.query_selector("id=receipt")
    outer_html= element.evaluate("element => element.outerHTML")
    file="order-" + order_id + ".pdf"
    path_file= os.path.join("output",file)
    pdf.html_to_pdf(outer_html,path_file)
    return path_file

def screenshot_robot(order_id):
    page=browser.page()
    file="order-" + order_id + ".png"
    path_file= os.path.join("output",file)
    element= page.query_selector("id=robot-preview-image")
    element.screenshot(path=path_file)
    return path_file

def embed_screenshot_to_receipt(screenshot,pdf):
    local_pdf= PDF()
    list_screenshot=[screenshot]
    local_pdf.add_files_to_pdf(list_screenshot,pdf,True)

def archive_receipts():
    
    lib = Archive()
    lib.archive_folder_with_zip('./output', './output/order_archive.zip', include='*.pdf')