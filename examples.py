#!/usr/bin/env python3
"""
Example usage of the Straico Python client.

This file demonstrates various ways to use the Straico API client.
"""

import os
from straico import StraicoClient


def main():
    """Run example queries."""
    
    # Get API key from environment
    api_key = os.environ.get("STRAICO_API_KEY")
    if not api_key:
        print("Please set STRAICO_API_KEY environment variable")
        return
    
    # Initialize client
    client = StraicoClient(api_key=api_key)
    
    print("=" * 60)
    print("Straico Python Client - Usage Examples")
    print("=" * 60)
    
    # Example 1: Simple query with smart selector
    print("\n1. Simple query with smart selector (balance pricing):")
    print("-" * 60)
    response = client.chat("What is the capital of France?", pricing_method="balance")
    if response.get("success"):
        data = response["data"]
        choices = data["completion"]["choices"]
        print(f"Response: {choices[0]['message']['content']}")
        print(f"Price: {data['price']['total']} coins")
    
    # Example 2: Quality-focused query
    print("\n2. Quality-focused query:")
    print("-" * 60)
    response = client.chat(
        "Explain quantum entanglement in simple terms",
        pricing_method="quality"
    )
    if response.get("success"):
        data = response["data"]
        choices = data["completion"]["choices"]
        content = choices[0]['message']['content']
        print(f"Response: {content[:200]}...")
        print(f"Model: {data['completion']['model']}")
    
    # Example 3: Budget-conscious query
    print("\n3. Budget query:")
    print("-" * 60)
    response = client.chat(
        "What is 2+2?",
        pricing_method="budget"
    )
    if response.get("success"):
        data = response["data"]
        choices = data["completion"]["choices"]
        print(f"Response: {choices[0]['message']['content']}")
        print(f"Price: {data['price']['total']} coins (budget mode)")
    
    # Example 4: Specific model
    print("\n4. Query with specific model:")
    print("-" * 60)
    response = client.chat(
        "Tell me a short joke",
        model="openai/gpt-4o-mini"
    )
    if response.get("success"):
        data = response["data"]
        choices = data["completion"]["choices"]
        print(f"Response: {choices[0]['message']['content']}")
        print(f"Model: {data['completion']['model']}")
    
    # Example 5: Multiple models (v1 API)
    print("\n5. Query multiple models simultaneously:")
    print("-" * 60)
    response = client.chat(
        "What is AI?",
        models=["openai/gpt-4o-mini", "anthropic/claude-3-5-haiku-20241022"]
    )
    if response.get("success"):
        data = response["data"]
        completions = data["completions"]
        print(f"Queried {len(completions)} models:")
        for model_id, model_data in completions.items():
            choices = model_data["completion"]["choices"]
            content = choices[0]['message']['content']
            print(f"\n  {model_id}:")
            print(f"  {content[:100]}...")
    
    # Example 6: Smart selector with quantity
    print("\n6. Smart selector with quantity (2 models):")
    print("-" * 60)
    response = client.chat(
        "Compare different perspectives on renewable energy",
        pricing_method="balance",
        quantity=2
    )
    if response.get("success"):
        data = response["data"]
        completions = data.get("completions", {})
        if completions:
            print(f"Selected {len(completions)} models:")
            for idx, (model_id, model_data) in enumerate(completions.items(), 1):
                print(f"\n  Model {idx}: {model_id}")
            print(f"\nTotal Price: {data['overall_price']['total']} coins")
            
            # Show justification if available
            if "model_selector_justification" in data:
                print(f"\nJustification: {data['model_selector_justification'][:150]}...")
    
    # Example 7: List available models
    print("\n7. List available models:")
    print("-" * 60)
    models_response = client.get_models()
    if models_response.get("success"):
        chat_models = models_response["data"]["chat"]
        print(f"Found {len(chat_models)} chat models\n")
        
        # Show first 5 models
        for model in chat_models[:5]:
            print(f"  • {model['name']}")
            print(f"    ID: {model['model']}")
            print(f"    Cost: {model['pricing']['coins']} coins per 100 words\n")
        
        print(f"  ... and {len(chat_models) - 5} more models")
    
    # Example 8: Error handling with model suggestions
    print("\n8. Error handling (invalid model name):")
    print("-" * 60)
    response = client.chat(
        "Hello",
        model="gpt4"  # Invalid model name
    )
    if not response.get("success") and response.get("model_not_found"):
        print(f"Error: {response['error']}")
        suggestions = response.get("suggestions", [])
        if suggestions:
            print("\nDid you mean:")
            for model in suggestions[:3]:
                print(f"  • {model['name']} ({model['model']})")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
