import uuid
from langchain_core.messages import HumanMessage
from graph import app

def main():
    print("Starting Chatbot Agent with Memory...")
    
    # Generate a unique thread ID for this session
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"Session ID: {thread_id}")
    print("Type 'quit', 'exit', or 'q' to end the session.")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        # Stream the output from the graph
        for output in app.stream(inputs, config=config):
            for key, value in output.items():
                # print(f"Output from node '{key}':")
                # print("---")
                if 'messages' in value:
                    last_msg = value['messages'][-1]
                    # Only print the content if it's from the agent (AI) and has content
                    # or if it's a tool output (though usually we just want the final answer)
                    if key == "agent" and last_msg.content:
                        print(f"Agent: {last_msg.content}")
                # print("\n---\n")

if __name__ == "__main__":
    main()
