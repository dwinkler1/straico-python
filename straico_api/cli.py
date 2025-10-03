"""
Straico CLI - Command-line interface for Straico API.
"""

import argparse
import os
import sys
from typing import Dict

from .client import StraicoClient


def get_api_key() -> str:
    """
    Get API key from environment variable or user input.

    Returns:
        API key string
    """
    api_key = os.environ.get("STRAICO_API_KEY")

    if not api_key:
        api_key = input("Enter your Straico API key: ").strip()

        if not api_key:
            print("Error: API key is required", file=sys.stderr)
            sys.exit(1)

    return api_key


def format_response(response: Dict, response_only: bool = False) -> str:
    """
    Format the API response for display.

    Args:
        response: API response dictionary

    Returns:
        Formatted string for display
    """
    if not response.get("success", False):
        error = response.get("error", "Unknown error")

        # Check if it's a model not found error with suggestions
        if response.get("model_not_found"):
            requested_model = response.get("requested_model", "unknown")
            suggestions = response.get("suggestions", [])

            output = f"❌ Error: {error}\n\n"

            if suggestions:
                output += "💡 Did you mean one of these models?\n\n"
                for i, model in enumerate(suggestions, 1):
                    model_id = model.get("model", "N/A")
                    model_name = model.get("name", "Unknown")
                    pricing = model.get("pricing", {})
                    coins = pricing.get("coins", "N/A")

                    output += f"{i}. {model_name}\n"
                    output += f"   ID: {model_id}\n"
                    output += f"   Cost: {coins} coins per 100 words\n\n"

                output += '💬 Use: --model "MODEL_ID" to select a specific model\n'
                output += f'   Example: --model "{suggestions[0].get("model", "")}"'
            else:
                output += "💡 Use --list-models to see all available models"

            return output

        return f"❌ Error: {error}"

    data = response.get("data", {})

    # Check if this is a v1 response with multiple completions
    completions = data.get("completions", {})

    if completions and isinstance(completions, dict):
        # v1 format with multiple models
        output = ""
        total_price = 0
        total_words = 0

        for idx, (model_id, model_response) in enumerate(completions.items(), 1):
            completion_data = model_response.get("completion", {})

            if not completion_data:
                continue

            # Get the model name
            model_name = completion_data.get("model", model_id)

            # Get the actual message content and annotations from choices
            choices = completion_data.get("choices", [])
            completion_text = "No response"
            annotations = []

            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                completion_text = message.get("content", "No response")
                annotations = message.get("annotations", [])

            # Add separator between models
            if idx > 1:
                output += "\n" + "=" * 60 + "\n"

            output += f"\n🤖 Model {idx}: {model_name}\n"
            output += f"\n{completion_text}\n"

            # Format annotations if present
            if annotations:
                output += "\n" + "─" * 60 + "\n"
                output += "📚 Sources:\n\n"

                for ann_idx, annotation in enumerate(annotations, 1):
                    annotation_type = annotation.get("type", "unknown")

                    if annotation_type == "url_citation":
                        url_citation = annotation.get("url_citation", {})
                        url = url_citation.get("url", "N/A")
                        output += f"[{ann_idx}] {url}\n"
                    else:
                        output += f"[{ann_idx}] {annotation_type}: {annotation}\n"

        # Add total pricing at the end
        overall_price = data.get("overall_price", {})
        overall_words = data.get("overall_words", {})
        total_price = overall_price.get("total", "N/A")
        total_words = overall_words.get("total", "N/A")

        # Get model selector justification if available
        justification = data.get("model_selector_justification", "")
        if not response_only:
            output += "\n" + "=" * 60 + "\n"
            output += f"💰 Total Price: {total_price} coins | Total Words: {total_words}\n"

            if justification:
                output += f"\n📋 Model Selection Justification:\n{justification}\n"

        return output

    # Single model response (v0 or v1 with single model)
    completion_data = data.get("completion", {})

    if completion_data:
        # Get the model name
        model_name = completion_data.get("model", "Unknown")

        # Get the actual message content and annotations from choices
        choices = completion_data.get("choices", [])
        completion_text = "No response"
        annotations = []

        if choices and len(choices) > 0:
            message = choices[0].get("message", {})
            completion_text = message.get("content", "No response")
            annotations = message.get("annotations", [])

        # Get pricing and word information
        price_data = data.get("price", {})
        words_data = data.get("words", {})

        total_price = price_data.get("total", "N/A")
        total_words = words_data.get("total", "N/A")

        # Get model selector justification if available
        justification = data.get("model_selector_justification", "")

        output = f"\n🤖 Model: {model_name}\n"
        output += f"💰 Price: {total_price} coins | Words: {total_words}\n"
        if justification:
            output += (
                f"📋 Justification: {justification[:500]}...\n"
                if len(justification) > 500
                else f"📋 Justification: {justification}\n"
            )
        output += f"\n{completion_text}\n"

        # Format annotations if present
        if annotations:
            output += "\n" + "─" * 60 + "\n"
            output += "📚 Sources:\n\n"

            for idx, annotation in enumerate(annotations, 1):
                annotation_type = annotation.get("type", "unknown")

                if annotation_type == "url_citation":
                    url_citation = annotation.get("url_citation", {})
                    url = url_citation.get("url", "N/A")
                    output += f"[{idx}] {url}\n"
                else:
                    # Handle other annotation types if needed in the future
                    output += f"[{idx}] {annotation_type}: {annotation}\n"

        return output

    return "❌ No completion found in response"


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Straico CLI - Chat with AI using smart LLM selection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use smart LLM selector with default pricing (balance)
  %(prog)s "What is the capital of France?"
  
  # Use quality pricing method for best results
  %(prog)s --pricing quality "Explain quantum computing"
  
  # Use budget pricing for cost-effective responses
  %(prog)s --pricing budget "What is 2+2?"
  
  # Specify a specific model (bypasses smart selector)
  %(prog)s --model "openai/gpt-4o" "Tell me a joke"
  
  # Query multiple models simultaneously (v1 API)
  %(prog)s --models "openai/gpt-4o-mini" "anthropic/claude-3-5-haiku-20241022" "What is AI?"
  
  # Use smart selector to pick multiple models (v1 API)
  %(prog)s --pricing budget --quantity 2 "Compare different perspectives"
  
  # Interactive mode with balance pricing
  %(prog)s --interactive --pricing balance
  
  # Set API key via environment variable
  export STRAICO_API_KEY="your-api-key-here"
  %(prog)s "Your prompt here"
        """,
    )

    parser.add_argument("prompt", nargs="?", help="The prompt/question to send to the AI")

    parser.add_argument(
        "-p",
        "--pricing",
        choices=["quality", "balance", "budget"],
        default="balance",
        help="Pricing method: balance (default), quality, or budget",
    )

    parser.add_argument(
        "-m", "--model", help="Specific model to use (overrides smart LLM selector)"
    )

    parser.add_argument(
        "--models",
        nargs="+",
        help="Multiple models to query simultaneously (v1 API only)",
    )

    parser.add_argument(
        "-q",
        "--quantity",
        type=int,
        help="Number of models to select with smart LLM selector (1-4, v1 API only, requires --pricing)",
    )

    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")

    parser.add_argument(
        "-l",
        "--list-models",
        action="store_true",
        help="List available models and exit",
    )

    parser.add_argument("--api-key", help="Straico API key (can also use STRAICO_API_KEY env var)")

    parser.add_argument("--no-animation", action="store_true", help="Hide loading animation")

    parser.add_argument(
        "--response-only",
        action="store_true",
        help="Provide only response text without additional info (price, justification, etc.)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show verbose output including request details",
    )

    args = parser.parse_args()

    # Validate quantity parameter
    if args.quantity is not None and (args.quantity < 1 or args.quantity > 4):
        print(
            f"❌ Error: Number of models must be between 1 and 4 (got {args.quantity})",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.no_animation:
        show_animation = False
    else:
        show_animation = True

    if args.response_only:
        response_only = True
    else:
        response_only = False

    # Get API key
    api_key = args.api_key or get_api_key()
    client = StraicoClient(api_key)

    # List models if requested
    if args.list_models:
        print("Fetching available models from Straico...")
        models_response = client.get_models()

        if models_response.get("success"):
            chat_models = models_response.get("data", {}).get("chat", [])
            print(f"\n✅ Found {len(chat_models)} chat models:\n")

            for model in chat_models:
                name = model.get("name", model.get("model", "Unknown"))
                model_id = model.get("model", "N/A")
                pricing = model.get("pricing", {})
                coins = pricing.get("coins", "N/A")

                print(f"  • {name}")
                print(f"    ID: {model_id}")
                print(f"    Cost: {coins} coins per 100 words")
                print()
        else:
            error = models_response.get("error", "Unknown error")
            print(f"❌ Error fetching models: {error}")

        return

    # Interactive mode
    if args.interactive:
        print("🤖 Straico CLI - Interactive Mode")

        if args.model:
            print(f"Model: {args.model}")
        else:
            print("Smart LLM Selector: Enabled")
            print(f"Pricing Method: {args.pricing}")

        print("Type 'exit' or 'quit' to end the session\n")

        while True:
            try:
                prompt = input("You: ").strip()

                if prompt.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break

                if not prompt:
                    continue

                # Send to API
                if args.verbose:
                    if args.models:
                        print(f"\n[Querying multiple models: {', '.join(args.models)}]")
                    elif args.model:
                        print(f"\n[Using model: {args.model}]")
                    else:
                        print(f"\n[Sending request with pricing: {args.pricing}]")

                response = client.chat(
                    prompt,
                    pricing_method=args.pricing,
                    model=args.model,
                    models=args.models,
                    quantity=args.quantity,
                    show_animation=show_animation,
                )
                formatted = format_response(response, response_only)
                print(formatted)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}", file=sys.stderr)

    # Single prompt mode
    elif args.prompt:
        if args.verbose:
            if args.models:
                print(f"[Querying multiple models: {', '.join(args.models)}]")
            elif args.model:
                print(f"[Using model: {args.model}]")
            else:
                print(f"[Using smart LLM selector with pricing: {args.pricing}]")

        response = client.chat(
            args.prompt,
            pricing_method=args.pricing,
            model=args.model,
            models=args.models,
            quantity=args.quantity,
            show_animation=show_animation,
        )
        formatted = format_response(response, response_only)
        print(formatted)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
