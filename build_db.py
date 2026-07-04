import os
import sys

from intelliquery.config import load_settings
from intelliquery.processing.pdf_loader import load_and_split_pdf
from intelliquery.providers.openai_provider import OpenAILLMProvider
from intelliquery.processing.summarizer import summarize_all_sections
from intelliquery.retrievers.vector_store import FAISSStoreManager

def main():
    settings = load_settings()
    pdf_path = "dune.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find {pdf_path}")
        sys.exit(1)
        
    print("1. Loading and splitting PDF into sections...")
    sections = load_and_split_pdf(pdf_path)
    print(f"   Found {len(sections)} sections.")
    
    print("2. Generating summaries using OpenAI...")
    provider = OpenAILLMProvider()
    llm = provider.build_chat_model(
        model_name=settings.llm.model_name,
        temperature=settings.llm.temperature,
    )
    summaries = summarize_all_sections(sections, llm, verbose=True)
    
    print("3. Building FAISS vector stores...")
    embeddings = provider.build_embeddings(model_name=settings.embeddings.model_name)
    store_mgr = FAISSStoreManager(embeddings=embeddings, persist_dir=settings.vector_store.persist_directory)
    
    print("   -> Building chunks index")
    store_mgr.build_from_documents(
        sections,
        index_name=settings.vector_store.chunks_index,
        chunk_size=settings.processing.chunk_size,
        chunk_overlap=settings.processing.chunk_overlap,
        split=True,
    )
    
    print("   -> Building summaries index")
    store_mgr.build_from_documents(
        summaries,
        index_name=settings.vector_store.summaries_index,
        split=False,
    )
    
    print("   -> Building quotes index")
    store_mgr.build_from_documents(
        sections,
        index_name=settings.vector_store.quotes_index,
        chunk_size=500,
        chunk_overlap=50,
        split=True,
    )
    
    print("\n✅ Success! All vector stores have been built and saved to the /data directory.")

if __name__ == "__main__":
    main()
