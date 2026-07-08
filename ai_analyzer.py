import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate

class AIAnalyzer:
    def __init__(self):
        self._llm = None
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    @property
    def llm(self):
        if self._llm is None:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY is not set. Please provide it in your environment variables or Streamlit secrets.")
            self._llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
        return self._llm

    def analyze_document(self, text: str):
        # This is a placeholder. Real implementation would involve more sophisticated prompt engineering
        # and potentially multiple LLM calls for different aspects.
        prompt_template = """
        Analyze the following legal document and extract the following information:
        - Contract Type
        - Parties Involved
        - Effective Date
        - Expiry Date
        - Payment Terms
        - Renewal Clauses
        - Confidentiality Clauses
        - Termination Clauses
        - Responsibilities

        Also, identify any potential risks, missing clauses, high-risk conditions, ambiguous statements, unusual payment terms, and legal red flags. For each identified issue, provide a confidence score and explanation.

        Document: {text}

        Provide the output in a structured format, clearly labeling each section.
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
        chain = prompt | self.llm
        response = chain.invoke({"text": text})
        return response.content

    def summarize_document(self, text: str):
        docs = self.text_splitter.create_documents([text])
        prompt_template = """
        Write a concise executive summary of the following document. Also, extract key obligations, important dates, important clauses, and recommended actions.

        Document: {text}

        Provide the output in a structured format, clearly labeling each section.
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
        chain = load_summarize_chain(self.llm, chain_type="stuff", prompt=prompt)
        summary = chain.run(docs)
        return summary

    def semantic_search(self, document_content: str, query: str):
        # This is a simplified placeholder. A full implementation would use vector databases.
        # For now, we'll just do a keyword search and return relevant sentences.
        sentences = document_content.split(". ")
        results = [s for s in sentences if query.lower() in s.lower()]
        return ". ".join(results[:5]) # Return up to 5 relevant sentences

