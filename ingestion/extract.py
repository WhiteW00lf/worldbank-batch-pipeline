from datetime import date
import time
import requests 
import json 
import boto3

indicators = ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "SP.DYN.LE00.IN", "SP.POP.GROW", "SP.URB.TOTL.IN.ZS"]
total_pages = None
URL = f"https://api.worldbank.org/v2/country/all/indicator/{indicators[0]}?format=json&per_page=1000&page=1"

s3 = boto3.client('s3')



def extract_data(url,indicator):
    data_of_pages = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            data_of_pages.extend(data[1])
            total_pages = data[0]['pages']
            for i in range(2, total_pages + 1):
                page_url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=1000&page={i}"
                page_response = requests.get(page_url)
                if page_response.status_code == 200:
                    page_data = page_response.json()
                    data_of_pages.extend(page_data[1])
                    # Process the data as needed
                    # print(f"Data for page {i}")
                    # print("=================================")
                    # print(page_data)
                   
                else:
                    print(f"Failed to retrieve data for page {i}. Status code: {page_response.status_code}")
            filename =  f"{date.today()}/{indicator}.json"
            s3.put_object(Bucket='worldbank-pipeline-surya', Key=f'bronze/{filename}', Body=json.dumps(data_of_pages))
           
            # with open(f"{indicator}.json", "w") as f:
            #     json.dump(data_of_pages, f)


        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error occurred while fetching data: {e}")
        
    


def lambda_handler(event, context):
    start = time.time()
    for indicator in indicators:
        URL = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=1000&page=1"
        extract_data(URL, indicator)
    elapsed_time = time.time() - start
    print(f"Upload completed in {elapsed_time:.2f} seconds.")
    return {
        'statusCode': 200,
        'body': json.dumps('Data extraction and upload completed successfully!')
    }   

# if __name__ == "__main__":
#     start = time.time()
#     for indicator in indicators:
#         URL = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=1000&page=1"
#         extract_data(URL, indicator)
#     elapsed_time = time.time() - start
#     print(f"Upload completed in {elapsed_time:.2f} seconds.")   