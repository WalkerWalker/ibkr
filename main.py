import requests

baseUrl = "https://localhost:5000/v1/portal"

def getAccountId():
    url = baseUrl + "/portfolio/accounts"
    content = requests.get(url, verify=False)
    id = content.json()[0]["accountId"]
    return id


accountId = getAccountId()
print(accountId)
