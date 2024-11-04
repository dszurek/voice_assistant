from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM


class ChatService:
    def __init__(self):
        self.template = """
        You are a helpful artificial intelligence assistant. You respond in a short, concise manner, with responses never longer than 20 words. 
        Do not hallucinate and do not generate any text other than the response. 
        The conversation transcript is as follows:
        {history}
        And here is the user's follow-up: {input}
        Your response:
        """
        self.PROMPT = PromptTemplate(input_variables=["history", "input"], template=self.template)
        self.chain = ConversationChain(
            prompt=self.PROMPT,
            verbose=False,
            memory=ConversationBufferMemory(ai_prefix="Assistant:"),
            llm=OllamaLLM(model="llama3.2")
        )
    
    def get_response(self, text: str) -> str:
        response = self.chain.predict(input=text)
        if response.startswith("Assistant:"):
            response = response[len("Assistant:") :].strip()
        return response
    

        
if __name__ == "__main__":
    chat_service = ChatService()
    while True:
            user_input = input("You: ")
            response = chat_service.get_response(user_input)
            print(f"Assistant: {response}")