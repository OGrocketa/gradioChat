import os

import gradio as gr

from controllers import CrewController, FileController


class GradioView:

    def __init__(self):
        self.crew_controller = CrewController()
        self.file_controller = FileController()
        self.demo = self._build_ui()


    def _build_ui(self) -> gr.Blocks:
        crew_names = self.crew_controller.list_crews()
        default_crew = crew_names[0] if crew_names else None

        def get_agent_tools(crew_name: str) -> list[str]:
            return self.crew_controller.list_tools(crew_name)

        def get_preloaded_files(crew_name: str) -> list[str]:
            return self.crew_controller.preloaded_files(crew_name)

        def get_task_vars(crew_name: str) -> list[str]:
            return self.crew_controller.task_variables(crew_name)

        with gr.Blocks() as demo:
            gr.Markdown("# CrewAI Demo")
            uploaded_files_state = gr.BrowserState([])

            with gr.Row():
                with gr.Column(scale=1):
                    agent_selection = gr.Dropdown(
                        label="Select Agent",
                        choices=crew_names,
                        value=default_crew,
                        interactive=True,
                    )

                    agent_config = gr.CheckboxGroup(
                        label="Agent Config",
                        interactive=True,
                        choices=get_agent_tools(default_crew) if default_crew else [],
                    )

                    files = gr.File(label="Upload Files", file_count="multiple")

                    preloaded_files = gr.File(
                        label="Preloaded Files",
                        file_count="multiple",
                        value=get_preloaded_files(default_crew) if default_crew else [],
                        visible=bool(get_preloaded_files(default_crew)) if default_crew else False,
                    )

                    @gr.render(inputs=[agent_selection])
                    def render_variable_inputs(agent):
                        user_inputs = [gr.Textbox(label=v) for v in get_task_vars(agent)]
                        submit_btn = gr.Button("Submit")

                        @submit_btn.click(
                            inputs=user_inputs + [agent_selection, process_logs, agent_config],
                            outputs=[output, process_logs],
                        )
                        def _get_answer(*args):
                            user_vals = args[:-3]
                            sel_agent, log_text, sel_tools = args[-3:]
                            log_text = log_text or ""

                            gen = self.crew_controller.get_crew_response(
                                *user_vals, sel_agent, log_text, sel_tools
                            )

                            final_resp = None
                            for resp, live_logs in gen:
                                if live_logs is not None:
                                    log_text = live_logs
                                    yield None, log_text
                                if resp is not None:
                                    final_resp = resp
                            yield final_resp, log_text

                with gr.Column(scale=2):
                    process_logs = gr.Textbox(
                        lines=5, label="Logs", autoscroll=True, interactive=False
                    )
                    output = gr.Textbox(lines=5, label="Output Box")

            def _relocate_files(agent, new_files, logs, uploaded):
                # wipe old uploaded files
                for f in uploaded:
                    if os.path.exists(f):
                        os.remove(f)
                uploaded.clear()

                # copy new files (if any) to crew knowledge dir
                if new_files:
                    logs, uploaded = self.file_controller.handle_file_upload(
                        new_files, logs, agent, uploaded
                    )

                return (
                    gr.update(choices=get_agent_tools(agent), value=[]),
                    uploaded,
                )

            agent_selection.change(
                fn=_relocate_files,
                inputs=[agent_selection, files, process_logs, uploaded_files_state],
                outputs=[agent_config, uploaded_files_state],
            )

            def _update_preloaded(agent):
                pl = get_preloaded_files(agent)
                return gr.update(value=pl, visible=bool(pl))

            agent_selection.change(
                fn=_update_preloaded,
                inputs=[agent_selection],
                outputs=[preloaded_files],
            )

            @files.upload(
                inputs=[files, process_logs, agent_selection, uploaded_files_state],
                outputs=[process_logs, uploaded_files_state],
            )
            def _upload(new, logs, agent, uploaded):
                return self.file_controller.handle_file_upload(new, logs, agent, uploaded)

            @files.delete(
                inputs=[process_logs, uploaded_files_state],
                outputs=[process_logs, uploaded_files_state],
            )
            def _delete(deleted: gr.DeletedFileData, logs, uploaded):
                return self.file_controller.handle_file_deletion(deleted, logs, uploaded)

            @files.clear(
                inputs=[process_logs, uploaded_files_state],
                outputs=[process_logs, uploaded_files_state],
            )
            def _clear(logs, uploaded):
                return self.file_controller.handle_files_clear(logs, uploaded)

        return demo

    def launch(self, server_name="0.0.0.0"):
        return self.demo.launch(server_name=server_name)
