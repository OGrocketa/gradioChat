from crew.crew import Testcrew
import gradio as gr


with gr.Blocks() as demo:
    gr.Markdown("# CrewAI Demo")
    userInput = gr.Textbox(lines=5, label="Enter your query")
    output = gr.Textbox(lines=5, label="Output Box")
    submitBtn = gr.Button("Submit")

    @submitBtn.click(inputs=userInput, outputs=output)
    def get_answer(userInput):
        crew = Testcrew().crew()
        response = crew.kickoff({"query": userInput})
        return response

demo.launch()