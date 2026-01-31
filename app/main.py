import sys
from agent import agent

def main():
    print("Chat with the robot agent. Type 'exit' to quit.")
    messages = None
    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "q"}:
            break

        try:
            result = agent.run_sync(user_input, message_history=messages)
            print(result.output)
            messages = result.all_messages()
        except Exception as e:
            print(f"Error: {e}")

    print("Goodbye!")

if __name__ == "__main__":
    main()