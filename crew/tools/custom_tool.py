from crewai.tools import tool

@tool("PdfSummaryTool")
def text_summary_tool(question: str) -> str:
    """This tool helps with pdf summarization. Converts pdf to text and extract the necessary chunks"""
    # Function logic here
    return "Result from your custom tool"
