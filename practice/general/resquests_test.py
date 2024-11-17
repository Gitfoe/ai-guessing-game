import requests

response = requests.get("http://info.cern.ch/hypertext/WWW/TheProject.html")
print(response.text)  # prints the request body (here: HTML content)

print("--------")

print(response.status_code)  # if everything went well, this will be 200

print("--------")

headers = response.headers
print(headers['Content-Type'])  # tells us, what kind of content we have. Should be starting with 'text/html' here

print("--------")

custom_headers = {'User-Agent': 'customAgent'}  # another could be Accept-Language (see session 1)
response = requests.get("http://info.cern.ch/hypertext/WWW/TheProject.html", headers=custom_headers)

#response = requests.get("http://info.cern.ch/hypertext/WWW/TheProject.html", timeout=5)  # timeout after 5 second