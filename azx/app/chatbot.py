import os

import gradio as gr
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage

from rag import build_rag_chain
from utils import get_nws_alerts, resolve_address, resolve_coordinates

openai.api_key = os.environ.get("OPENAI_API_KEY")

llm = ChatOpenAI(temperature=0, model='gpt-4-1106-preview')

# Import the rag chain
rag_chain = build_rag_chain(os.path.join(os.path.dirname(__file__), "azx_data.tsv"), llm)


# Utility functions for the chatbot

def process_alerts(lat, lon):
    """ Fetches alerts from NWS api and builds a string suitable for the LLM chatbot"""
    outputs = []
    alerts = get_nws_alerts(float(lat), float(lon))

    if alerts is None:
        return "Search unsuccessful. Please try again."
    if not alerts:
        return "No alerts currently in this area!"
    else:

        for i, alert in enumerate(alerts):
            key = alert.type + ": " + alert.description[:10] + "..."
            message = f"{alert.type}: {alert.description}".replace("\n", " ")
            outputs.append((key, message))
        # return "\n\n".join(outputs)
        return outputs


def llm_predict(message, history):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))
    # If the chat is empty (i.e. new interaction), use the rag chain, otherwise use the llm directly
    if len(history) == 0:
        first_response = rag_chain.invoke(message)
        return first_response.content
    else:
        gpt_response = llm(history_langchain_format)
        return gpt_response.content


##############################################

# Event Handlers

def start_conversation(alert_text, location):
    # bot_message = predict(message, chat_history)
    contextualized_template = PromptTemplate.from_template(
        "The NWS has issued an alert for {location}. Alert text: ```{alert_text}```")
    message = contextualized_template.format(location=location, alert_text=alert_text)
    bot_message = rag_chain.invoke(alert_text)
    chat_history = [(message, bot_message.content)]
    return "", chat_history


def follow_up_conversation(message, chat_history):
    bot_message = llm_predict(message, chat_history)
    chat_history.append((message, bot_message))
    return "", chat_history


def build_alerts_dropdown(lat, lon):
    alerts = process_alerts(lat, lon)

    if isinstance(alerts, list):
        return gr.Dropdown(choices=alerts,
                           label="Select an Alert in your Area",
                           allow_custom_value=True,
                           type="value",
                           value=alerts[0][0]
                           )
    else:
        none_found = ["NO ALERT FOUND"]
        return gr.Dropdown(none_found,
                           label="Alert not found. Try different coordinates",
                           allow_custom_value=True,
                           value=none_found[0]
                           )


def address_box_handler(address: str):
    # Resolve the coordinates of the chosen address
    location = resolve_address(address)
    # Get the dropdown elements from the chosen location
    alerts = build_alerts_dropdown(location.latitude, location.longitude)
    # Update the  address, coordinates and drop down items
    return location.address, location.latitude, location.longitude, alerts


def coordinates_boxs_handler(lat, lon):
    """ Takes coordinates, fetches alerts and builds a dropdown with the alerts in from the dropdown menu"""
    location = resolve_coordinates(lat, lon)
    # For testing/demonstration purposes
    if lat == "10" and lon == "10":
        alerts = [("Heat Advisory", "Heat Advisory"), ("Drought Advisory", "Drought Advisory"),
                  ("Hard Freeze Warning", "Hard Freeze Warning")]
        return gr.Dropdown(alerts,
                           label="Select an Alert in your Area",
                           allow_custom_value=True,
                           value=alerts[0][0]
                           ), location.address
    ###################################

    return build_alerts_dropdown(lat, lon), location.address


# UI Layout begins here

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            with gr.Tab("Address"):
                address_box = gr.Textbox(label="Address", type="text", elem_id="addr")
                addr_dropdown_button = gr.Button(value="Submit Address")
            with gr.Tab("Coordinates"):
                lat_box = gr.Textbox(label="Latitude", type="text")
                lon_box = gr.Textbox(label="Longitude", type="text")
                coord_dropdown_button = gr.Button(value="Submit Coordinates")

            dropdown = gr.Dropdown([], label="Complete above form", allow_custom_value=True)
            coord_dropdown_button.click(coordinates_boxs_handler, [lat_box, lon_box], [dropdown, address_box])
            addr_dropdown_button.click(address_box_handler, [address_box],
                                       outputs=[address_box, lat_box, lon_box, dropdown])

            advice_button = gr.Button(value="Click for Chatbot Advice")

        with gr.Column():
            chatbot = gr.Chatbot()
            msg = gr.Textbox(interactive=True)
            submit_msg = gr.Button("Submit Message")
            clear = gr.ClearButton([msg, chatbot])

        msg.submit(follow_up_conversation, [msg, chatbot], [msg, chatbot])
        submit_msg.click(follow_up_conversation, [msg, chatbot], [msg, chatbot])

        address_box.submit(address_box_handler, [address_box], [address_box, lat_box, lon_box, dropdown])
        lat_box.submit(coordinates_boxs_handler, [lat_box, lon_box], [dropdown, address_box])
        lon_box.submit(coordinates_boxs_handler, [lat_box, lon_box], [dropdown, address_box])

        advice_button.click(start_conversation, [dropdown, address_box], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()
