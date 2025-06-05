import os

import gradio as gr

from .crew_data_fetch import (
    discover_agent_tools,
    discover_available_crews,
    extract_variables_from_tasks,
    get_preloaded_files,
)
from .file_handling import handle_file_deletion, handle_file_upload, handle_files_clear
from .get_crew_response import get_crew_response


def create_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# CrewAI Demo")
        uploaded_files = gr.BrowserState([])

        with gr.Row():
            with gr.Column(scale=1):
                agent_selection = gr.Dropdown(
                    choices=discover_available_crews(),
                    label="Select Agent",
                    interactive=True,
                    value=discover_available_crews()[0],
                )
                agent_config = gr.CheckboxGroup(
                    label="Agent Config",
                    interactive=True,
                    choices=discover_agent_tools(discover_available_crews()[0]),
                )
                files = gr.File(label="Upload Files", file_count="multiple")
                preloaded_files = gr.File(
                    label="Preloaded Files",
                    file_count="multiple",
                    value=get_preloaded_files(discover_available_crews()[0]),
                    visible=(
                        len(get_preloaded_files(discover_available_crews()[0])) > 0
                    ),
                )

                @gr.render(inputs=[agent_selection])
                def render_variable_inputs(agent):
                    variables = extract_variables_from_tasks(agent)
                    user_input = []
                    for var in variables:
                        textbox = gr.Textbox(label=var)
                        user_input.append(textbox)

                    submit_btn = gr.Button("Submit")

                    @submit_btn.click(
                        inputs=user_input + [agent_selection, process_logs, agent_config],
                        outputs=[output, process_logs],
                    )
                    def get_answer(*args):
                        user_inputs = args[:-3]  # All but last 3 args are user inputs
                        selected_agent = args[-3]  # Second to last is agent selection
                        current_logs = args[-2]  # Second to last is process logs
                        selected_config = args[-1]  # Last is agent config

                        response_generator = get_crew_response(
                            *user_inputs, selected_agent, current_logs, selected_config
                        )

                        final_response = None
                        current_logs = current_logs or ""

                        for response, logs in response_generator:
                            if response is not None:
                                final_response = response
                            if logs is not None:
                                current_logs = logs
                                yield None, current_logs

                        yield final_response, current_logs

            with gr.Column(scale=2):
                process_logs = gr.Textbox(
                    lines=5, label="Logs", autoscroll=True, interactive=False
                )
                output = gr.Textbox(lines=5, label="Output Box")

        def update_agent_config(agent):
            return gr.update(choices=discover_agent_tools(agent))

        def relocate_files(agent, files, logs, uploaded_files):
            for file in uploaded_files:
                if os.path.exists(file):
                    os.remove(file)
            uploaded_files.clear()
            if files is not None:
                upload_files(files, logs, agent, uploaded_files)

            return gr.update(
                choices=discover_agent_tools(agent), value=[]
            ), uploaded_files

        agent_selection.change(
            fn=relocate_files,
            inputs=[agent_selection, files, process_logs, uploaded_files],
            outputs=[agent_config, uploaded_files],
        )

        def update_preloaded_files(agent):
            files = get_preloaded_files(agent)
            return gr.update(value=files, visible=(len(files) > 0))

        agent_selection.change(
            fn=update_preloaded_files, inputs=[agent_selection], outputs=[preloaded_files]
        )

        @files.upload(
            inputs=[files, process_logs, agent_selection, uploaded_files],
            outputs=[process_logs, uploaded_files],
        )
        def upload_files(files, logs, agent_selection, uploaded_files):
            return handle_file_upload(files, logs, agent_selection, uploaded_files)

        @files.delete(
            inputs=[process_logs, uploaded_files],
            outputs=[process_logs, uploaded_files],
        )
        def remove_file(deleted_data: gr.DeletedFileData, logs, uploaded_files):
            return handle_file_deletion(deleted_data, logs, uploaded_files)

        @files.clear(
            inputs=[process_logs, uploaded_files],
            outputs=[process_logs, uploaded_files],
        )
        def remove_all_files(logs, uploaded_files):
            return handle_files_clear(logs, uploaded_files)

    return demo
