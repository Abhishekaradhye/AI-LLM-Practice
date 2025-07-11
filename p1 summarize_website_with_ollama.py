# We will get a url and provide a summary of that website using Beautiful Soup and latwe use OLLAMA 

import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display

Ollama_api = "http://mylocalhost/api/chat"
headers = {"Content-Type": "application/json"}
model = "llama3.2"

system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

class Website:

    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

print(":)")

# See how this function creates exactly the format above

def prompt(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]
print(":)")


# And now: call the OpenAI API.
def summarize(url):
    website = Website(url)
    payload = {
    "model" : "llama3.2",
    "messages" : prompt(website),
    "stream" : False
}
    response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
    summary = response.json()["message"]["content"]
    display(Markdown(summary))
    return response.json()["message"]["content"]



summarize("https://www.icc-cricket.com/")
