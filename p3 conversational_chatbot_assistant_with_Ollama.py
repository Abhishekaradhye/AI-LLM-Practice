import os
import json
import requests
import gradio as gr

OLLAMA_API = "http://localhost:11434/api/chat"
MODEL = "llama3.2"
HEADERS = {"Content-Type": "application/json"}

print(":)")

ticket_prices = {
    "London": "₹30,000",
    "Paris": "₹25,800",
    "Tokyo": "₹27,400",
    "Berlin": "₹20,100",
    "Delhi": "₹7,300",
    "Ahmedabad": "₹2,200"
}


system_message = "You are a helpful assistant for an Airline called Happy Flight Airlines."
system_message += "Give short, courteous answers, no more than 1 sentence. Be proffessional and revert politely redirecting the responses towards context of chat"
system_message += f"Always be accurate. If you don't know the answer, say so. {ticket_prices}"


print(":)")

def chat(message, history):
    messages = [{"role": "system", "content": system_message}]
    for turn in history:
        if isinstance(turn, list) and len(turn) == 2:
            user_msg, assistant_msg = turn
            print("User:", user_msg)
            print("Assistant:", assistant_msg)
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": message})
            
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    print(f"\nuser: {message}")                 # print user input
    response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)    # your existing Ollama request code
    result = response.json().get("message") or response.json().get("response")
    print(f"assistant: {result}")
    return result

print(":)")


gr.ChatInterface(fn=chat, type="messages").launch()

