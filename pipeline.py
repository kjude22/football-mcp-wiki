import os
import sys
import argparse
from orchestrator import LLMWikiOrchestrator

def main():
    parser = argparse.ArgumentParser(
        description="LLM Wiki Multi-Agent & Maintenance System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py ingest --demo
  python pipeline.py query "what is mcp?"
  python pipeline.py maintain
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Operational Subcommands")
    
    # Subcommand: Ingest
    parser_ingest = subparsers.add_parser("ingest", help="Ingest a new raw knowledge item into the wiki database.")
    parser_ingest.add_argument("--demo", action="store_true", help="Run high-fidelity multi-agent ingestion simulation.")
    parser_ingest.add_argument("--raw", type=str, help="Raw text string to ingest.")
    parser_ingest.add_argument("--file", type=str, help="Path to a text file containing the content to ingest.")
    
    # Subcommand: Query
    parser_query = subparsers.add_parser("query", help="Query the wiki database and synthesize an answer.")
    parser_query.add_argument("query_string", type=str, help="The search query or question.")
    
    # Subcommand: Maintain
    parser_maintain = subparsers.add_parser("maintain", help="Run automated audits, resolve links, and rebuild the navigation homepage.")
    
    # Backwards compatibility: if arguments are passed as old style (e.g. pipeline.py --demo)
    if len(sys.argv) > 1 and sys.argv[1] in ["--demo", "--raw", "--file"]:
        sys.argv.insert(1, "ingest")
        
    args = parser.parse_args()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    orchestrator = LLMWikiOrchestrator(current_dir)
    
    if args.command == "ingest" or args.command is None:
        if args.command is None or not (args.demo or args.raw or args.file):
            if args.command is None:
                parser.print_help()
                print("\nNo command specified. Running default Ingestion Demo...")
            args.demo = True
            
        raw_content = ""
        if args.demo:
            raw_content = "Ingest the Model Context Protocol (MCP) details. It defines Client-Server interface protocols."
            print("Initiating Pipeline Ingestion Demo...")
        elif args.raw:
            raw_content = args.raw
            print(f"Ingesting raw text input (Length: {len(raw_content)} characters)...")
        elif args.file:
            if not os.path.exists(args.file):
                print(f"Error: Ingestion source file not found at '{args.file}'")
                sys.exit(1)
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    raw_content = f.read()
                print(f"Loaded raw content from file '{args.file}' (Length: {len(raw_content)} characters)...")
            except Exception as e:
                print(f"Error reading ingestion file: {e}")
                sys.exit(1)
                
        success = orchestrator.run_pipeline(raw_content)
        sys.exit(0 if success else 1)
        
    elif args.command == "query":
        success = orchestrator.query_wiki(args.query_string)
        sys.exit(0 if success else 1)
        
    elif args.command == "maintain":
        success = orchestrator.maintain_wiki()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

