import requests

baseUrl = "https://localhost:5000/v1/portal"

def getAccountId():
    url = baseUrl + "/portfolio/accounts"
    content = requests.get(url, verify=False)
    id = content.json()[0]["accountId"]
    return id

def getPositions(accountId):
    pageId = 0
    positions = []

    while True:
        url = baseUrl + "/portfolio/" + accountId + "/positions/" + str(pageId)
        content = requests.get(url, verify=False)
        for pos in content.json():
            positions.append(pos)
        if len(content.json()) == 30:
            pageId += 1
        else:
            break

    return positions


accountId = getAccountId()
positions = getPositions(accountId)
print(positions)
