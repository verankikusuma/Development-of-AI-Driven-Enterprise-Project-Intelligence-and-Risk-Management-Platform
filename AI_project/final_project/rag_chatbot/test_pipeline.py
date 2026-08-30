import sys

from rag_chatbot import ingest_project_documents, ask


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "ingest":
        if len(sys.argv) < 3:
            print("Usage: python test_pipeline.py ingest <folder_path>")
            return
        folder = sys.argv[2]
        print(f"Ingesting documents from: {folder}")
        result = ingest_project_documents(folder)
        print(f"Documents processed: {result['documents_processed']}")
        print(f"Chunks stored:       {result['chunks_stored']}")

    elif command == "ask":
        if len(sys.argv) < 3:
            print("Usage: python test_pipeline.py ask \"<your question>\"")
            return
        question = sys.argv[2]
        print(f"Question: {question}\n")
        result = ask(question)
        print("Answer:")
        print(result["answer"])
        print(f"\nSources: {', '.join(result['sources']) if result['sources'] else '(none found)'}")

    else:
        print(f"Unknown command '{command}'.")
        print(__doc__)


if __name__ == "__main__":
    main()