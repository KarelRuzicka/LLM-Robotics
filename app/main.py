import agent


def main():    
    """
    Main chat loop to interact with the robot agent.
    """
    
    print("Chat with the robot agent. Type 'exit' to quit.")
    messages = None
    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt): # Handle Ctrl+C or EOF
            print()
            break

        if not user_input: # Ignore empty input
            continue
        if user_input.lower() in {"exit", "quit", "q"}: # Exit commands
            break

        try:
            result = agent.agent.run_sync(user_input, message_history=messages) # Run agent with the user input and the conversation history
            print(result.output) # Print the agent's response
            messages = result.all_messages() # Keep the conversation history
        except Exception as e:
            print(f"Error: {e}")

    print("Goodbye!")

if __name__ == "__main__":
    main()