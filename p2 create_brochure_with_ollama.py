import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display

# A class to represent a Webpage

# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Getting website content
class Website:
    """
    A utility class to represent a Website that we have scraped, now with links
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

  ws = Website("https://www.thelivelovelaughfoundation.org/")


# Crafting prompting for getting only useful links from all links from website

link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a brochure about the company, \
such as links to an About page, or a Company page, or Careers/Jobs pages.\
ignore links that potentially lead to social media handles, lectures, social programs and campaigns. This will get us only our useful content\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
    ]
}
"""

def get_links_user_prompt(website):
    return [
        {"role": "system", "content": link_system_prompt},
        {"role": "user", "content": f"""Here is the list of links on the website of {website.url} - 
Please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. 
Do not include Terms of Service, Privacy, email links.\n
Links (some might be relative links):\n
{chr(10).join(website.links)}"""}


OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
model = "llama3.2"

def get_links(url):
    website = Website(url)
    payload = {
    "model" : model,
    "messages" : get_links_user_prompt(website),
    "stream" : False }
    response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
    result = response.json()["message"]["content"]
    return json.loads(result)


# Got links that make sese for brochure, now going throught the content for brochure

def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    print("Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result



# Crafted comprehensive prompt for generating brochure

system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
Include details of company culture, customers and careers/jobs if you have the information."

# Or uncomment the lines below for a more humorous brochure - this demonstrates how easy it is to incorporate 'tone':

# system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
# and creates a short humorous, entertaining, jokey brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
# Include details of company culture, customers and careers/jobs if you have the information."


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:7000] # Truncate if more than 5,000 characters
    return user_prompt

# FINAL STEP... Let's create brochure for relevant website using Ollama

def create_brochure(company_name, url):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
        "stream": False
    }
    response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
    result = response.json().get("response") or response.json().get("message", {}).get("content")
    display(Markdown(result))

print(":)")

create_brochure("the live love laugh foundation", "https://www.thelivelovelaughfoundation.org/")

# Brochure Created as you can see in brochure.txt file
