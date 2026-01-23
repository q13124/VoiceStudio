import requests

url = "https://cursor.com/api/dashboard/export-usage-events-csv?startDate=1766124000000&endDate=1768715999999&strategy=tokens"
response = requests.get(url)
response.raise_for_status()

with open("cursor_usage.csv", "wb") as f:
    f.write(response.content)

print("Downloaded to cursor_usage.csv")
