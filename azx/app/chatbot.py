from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
import openai
import gradio as gr
from typing import Any, List
import requests
from dataclasses import dataclass
from datetime import datetime

import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")

llm = ChatOpenAI(temperature=1.0, model='gpt-3.5-turbo-0613')

@dataclass
class WeatherAlert:
    lat: float
    lon: float
    type: str
    description: str
    starts: datetime
    expires: datetime

def get_alerts(lat:float, lon:float) -> List[WeatherAlert]:
    
	endpoint = "https://api.weather.gov/alerts/active"

	params = {
		"point": f"{lat},{lon}"
	}

	response = requests.get(url=endpoint, params=params)

	if response.status_code == 200:
		# We succeeded

		data = response.json()

		ret = list()

		for feature in data['features']:

			props = feature['properties']
			
			alert = WeatherAlert(
				lat=lat,
				lon=lon,
				type=props['event'],
				description=props['description'],
				starts=props['onset'],
				expires=props['expires']
			)

			ret.append(alert)
		
		return ret

def format_alerts(alerts):
    outputs = []
    for i, alert in enumerate(alerts):
        output = str(alert.type)
        outputs.append(output)
    #return "\n\n".join(outputs)
    return outputs

def process_alerts(lat, lon):
    alerts = get_alerts(lat, lon)

    if alerts is None:
        return "Search unsuccessful. Please try again."
    if alerts == []:
        return "No alerts currently in this area!"
    return format_alerts(alerts)

def alert_chatbot(dropdown, chat_history):
    message = f"The NWS has issued an alert of type {dropdown} in my area. What should I do?" 
    bot_message = predict(message, chat_history)
    chat_history.append((message, bot_message))
    return "", chat_history

def predict(message, history):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))
    gpt_response = llm(history_langchain_format)
    return gpt_response.content

def respond(message, chat_history):
    bot_message = predict(message, chat_history)
    chat_history.append((message, bot_message))
    return "", chat_history

def update_dropdown(lat, lon):
    # For testing/demonstration purposes
    if lat == "10" and lon == "10":
        alerts = ["Heat Advisory", "Drought Advisory"]
        return gr.Dropdown(alerts, 
            label="Select an Alert in your Area", 
            allow_custom_value=True, 
            value=alerts[0]
        )

    alerts = process_alerts(lat, lon)

    if isinstance(alerts, list):
        return gr.Dropdown(alerts, 
            label="Select an Alert in your Area", 
            allow_custom_value=True, 
            value=alerts[0]
        )

    none_found = ["NO ALERT FOUND"]
    return gr.Dropdown(none_found, 
        label="Alert not found. Try different coordinates", 
        allow_custom_value=True,
        value=none_found[0]
    )

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            lat = gr.Textbox(label="Latitude", type="text")
            lon = gr.Textbox(label="Longitude", type="text")

            dropdown_button = gr.Button(value="Enter coordinates")
            dropdowns = [gr.Dropdown([], label="Complete above form", allow_custom_value=True)]

            advice_button = gr.Button(value="Click for Chatbot Advice")

        with gr.Column():
            chatbot = gr.Chatbot()
            msg = gr.Textbox()

        msg.submit(respond, [msg, chatbot], [msg, chatbot])

        lat.submit(update_dropdown, [lat, lon], [dropdowns[0]])
        lon.submit(update_dropdown, [lat, lon], [dropdowns[0]])
        dropdown_button.click(update_dropdown, [lat, lon], [dropdowns[0]])

        advice_button.click(alert_chatbot, [dropdowns[0], chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()