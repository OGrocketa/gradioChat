from crew.crew import Testcrew
import gradio as gr


with gr.Blocks() as demo:
    gr.Markdown("# CrewAI Demo")
    with gr.Row():
        with gr.Column(scale=1):
            gr.Dropdown(choices=['DataSummarizer','Some other agent'], label="Select Agent",interactive=True)
            userInput = gr.Textbox(lines=5, label="Enter your query")
            submitBtn = gr.Button("Submit")
    
        with gr.Column(scale=2):
            processLogs = gr.Textbox(lines=5, label="Logs", autoscroll=True, interactive=False)
            output = gr.Textbox(lines=5, label="Output Box")

    @submitBtn.click(inputs=userInput, outputs=output)
    def get_answer(userInput):
        crew = Testcrew().crew()
        response = crew.kickoff({"query": userInput})
        return response

demo.launch()