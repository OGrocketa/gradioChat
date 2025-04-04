from crewai.tools import tool
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os


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
    source = "/Users/yaraslausedach/Code/gradioChat/crew/knowledge"
    llm = ChatOpenAI(model= "gpt-4o-mini",max_retries=2, temperature=0.5 )

    for filename in os.listdir(source):
        file_path = os.path.join(source,filename)
        if os.path.isdir(file_path):
            continue
        
        try:
            options = PdfPipelineOptions()
            options.generate_page_images = True
            
            converter = DocumentConverter(format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=options)
            })

            result = converter.convert(file_path)
            mdFile = result.document.export_to_markdown()

            prompt = f"Summarize the following document:\n\n{mdFile}"

            response = llm([HumanMessage(content=prompt)])
            summary = f"File name: {filename}", response.content.strip()
            summaries.append(summary)
        except Exception as e:
            summaries.append("Error Occurred:", e)

    return summaries
