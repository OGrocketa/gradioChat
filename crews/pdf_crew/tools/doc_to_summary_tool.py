import os

from crewai.tools import tool
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


@tool("DocToSummaryTool")
def doc_to_summary_tool() -> str:
    """
    <important> Summarizes files which user uploaded to the default directory </important>
    Converts a document into Markdown,
    splits the text into chunks using LangChain's semantic chunker, and summarizes each chunk using OpenAI.

    Returns:
      - A combined summary of all the chunks.
    """
    summaries = []
    source = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "crews",
        "pdf_crew",
        "knowledge",
    )
    llm = ChatOpenAI(model="gpt-4o-mini", max_retries=2, temperature=0.5)

    for filename in os.listdir(source):
        if not filename.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(source, filename)
        if os.path.isdir(file_path):
            continue

        try:
            options = PdfPipelineOptions()
            options.generate_page_images = True

            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=options)
                }
            )

            result = converter.convert(file_path)
            md_file = result.document.export_to_markdown()

            prompt = f"Summarize the following document:\n\n{md_file}"
            response = llm.invoke([HumanMessage(content=prompt)])
            summary = f"File name: {filename}", response.content.strip()
            summaries.append(summary)
        except Exception as e:
            summaries.append("Error Occurred:", e)

    return summaries
