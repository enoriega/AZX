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

with gr.Blocks() as demo:
    def ask_cold_weather_question():
        return "How can I protect myself in cold weather?"
    def ask_desert_question():
        return "How can I protect myself in the desert?"

    def format_alerts(alerts):
        output = ""
        for i, alert in enumerate(alerts):
            output += "-"*45 + " Alert " + str(i + 1) + " " + "-"*45 + "\n\n" + alert.description + "\n\n"
        return output

    def process_alerts(lat, lon):
        alerts = get_alerts(lat, lon)

        if alerts is None:
            return "Search unsuccessful. Please try again."
        if alerts == []:
            return "No alerts currently in this area!"
        return format_alerts(alerts)
    
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

    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot()
            msg = gr.Textbox()
            clear = gr.ClearButton([msg, chatbot])
        with gr.Column():
            with gr.Row():
                cold_weather_button = gr.Button(ask_cold_weather_question, value="Ask about Cold Weather")
                desert_button = gr.Button(ask_desert_question, value="Ask about the Desert")
            lat = gr.Textbox(label="Latitude", type="text")
            lon = gr.Textbox(label="Longitude", type="text")
            gr.Interface(
                fn = process_alerts,
                inputs = [lat, lon],
                outputs = [gr.Textbox(label="Alerts", type="text")]
            )

            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            cold_weather_button.click(respond, [cold_weather_button, chatbot], [msg, chatbot])
            desert_button.click(respond, [desert_button, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()