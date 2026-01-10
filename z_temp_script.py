from google import genai

client = genai.Client(api_key="AIzaSyDzbwrCAkSiTfpkUKVFzhlVBgfGGfjPdKI")

for m in client.models.list():
    print(m.name)
