"""
main.py
Single entrypoint to launch the Lex Detective web application.
Usage:
  python main.py [--port 8000] [--host 127.0.0.1]
"""

import sys
import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Start Lex Detective Web Application")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code change")

    args = parser.parse_args()

    print("=" * 80)
    print("  LEX DETECTIVE: Autonomous Legal Conflict & Loophole Engine")
    print("  First-Order Predicate Logic Theorem Proving & Resolution Refutation")
    print(f"  Starting web interface on: http://{args.host}:{args.port}")
    print("=" * 80)

    uvicorn.run("api:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
