import gradio as gr
from predict import create_price_prediction_tab
from eligibility import create_eligibility_tab

with gr.Blocks() as interface:
    with gr.Tabs():
        create_price_prediction_tab()
        create_eligibility_tab()

interface.launch(server_name="localhost", server_port=8080, debug=True)