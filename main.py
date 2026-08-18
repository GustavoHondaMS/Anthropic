from dotenv import load_dotenv
from anthropic import Anthropic
import os
from time import sleep
from decorators import timer, log
from context_manager import SafeContext
from anthropic.types import Message
import json
from text_editor import TextEditorTool
from anthropic.types import ToolParam
from datetime import datetime, timedelta
from langchain_aws import ChatBedrockConverse

load_dotenv(dotenv_path=".env.secrets")

class Colors:
        AZUL = "\033[94m"      # Azul
        VERDE = "\033[92m" # Verde
        AMARELO = "\033[93m" # Amarelo
        VERMELHO = "\033[91m" # Vermelho
        BRANCO = "\033[97m" # Branco
        
        RESET = "\033[0m"

# us.anthropic.claude-sonnet-4-20250514-v1:0
# us.anthropic.claude-haiku-4-5-20251001-v1:0
# us.anthropic.claude-fable-5
# us.anthropic.claude-sonnet-4-6
# us.anthropic.claude-opus-4-6-v1
# us.anthropic.claude-opus-5
# us.anthropic.claude-opus-4-8
# us.anthropic.claude-opus-4-7
# us.anthropic.claude-sonnet-4-5-20250929-v1:0
# us.anthropic.claude-sonnet-5
# us.anthropic.claude-opus-4-1-20250805-v1:0
# us.anthropic.claude-opus-4-5-20251101-v1:0
# us.anthropic.claude-3-haiku-20240307-v1:0:48k
# us.anthropic.claude-3-haiku-20240307-v1:0:200k
# us.anthropic.claude-3-haiku-20240307-v1:0

class Agent():
    
    def __init__(self, model="us.anthropic.claude-haiku-4-5-20251001-v1:0", system_message="Você é um assistente útil e prestativo."):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = self._build_model(model)
        self.system_message = system_message
        self.history = []
        self.colors = {
            "user": Colors.AZUL,
            "assistant": Colors.VERDE,
            "system": Colors.AMARELO,
            "reset": Colors.RESET
        }
        self.web_search_tool = {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5,
            "allowed_domains": ["nih.gov"],
        }
        self.text_editor_schema = {
            "type": "text_editor_20250728",
            "name": "str_replace_based_edit_tool",
        }
        self.current_datetime_schema = ToolParam(
            {
                "name": "get_current_datetime",
                "description": "Returns the current date and time formatted according to the specified format string. This tool provides the current system time formatted as a string. Use this tool when you need to know the current date and time, such as for timestamping records, calculating time differences, or displaying the current time to users. The default format returns the date and time in ISO-like format (YYYY-MM-DD HH:MM:SS).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "date_format": {
                            "type": "string",
                            "description": "A string specifying the format of the returned datetime. Uses Python's strftime format codes. For example, '%Y-%m-%d' returns just the date in YYYY-MM-DD format, '%H:%M:%S' returns just the time in HH:MM:SS format, '%B %d, %Y' returns a date like 'May 07, 2025'. The default is '%Y-%m-%d %H:%M:%S' which returns a complete timestamp like '2025-05-07 14:32:15'.",
                            "default": "%Y-%m-%d %H:%M:%S",
                        }
                    },
                    "required": [],
                },
            }
        )
        self.text_editor_tool = TextEditorTool()

    def _build_model(self, modelo = "openai.gpt-oss-20b-1:0" , t = 0)-> ChatBedrockConverse:
        """Constrói e retorna um modelo LLM configurado.

        Atualmente usa um mock para testes e desenvolvimento. Em produção,
        a implementação pode carregar variáveis de ambiente e criar um cliente
        ChatBedrockConverse com credenciais AWS.

        Args:
            modelo: Identificador do modelo a ser usado.
            t: Temperatura de sampling para geração do modelo.

        Returns:
            Objeto de modelo LLM configurado.
        """
        load_dotenv()  
        ACESS_KEY = os.getenv("ACESS_KEY")
        SECRET_KEY = os.getenv("SECRET_KEY")
        llm = ChatBedrockConverse(model = modelo,
        region_name = 'us-east-1',
        aws_access_key_id= ACESS_KEY,
        aws_secret_access_key= SECRET_KEY,
        temperature = t)
        # llm = llm_mock_model
    
        return llm

    ### History Management Methods ###
    def _add_user_message(self, message):
        user_message = {
                "role": "user",
                "content": message.content if isinstance(message, Message) else message,
            }
        self.history.append(user_message)
        
    def _add_assistant_message(self, message):
        user_message = {
                        "role": "user",
                        "content": message.content if isinstance(message, Message) else message,
                    }
        self.history.append(user_message)
    
    
    ### Style Methods ###
    def _print_question(self, question):
        print(f"{self.colors['user']}User:{self.colors['reset']} {question}")

    def _print_answer(self, answer):
        print(f"{self.colors['assistant']}Assistant:{self.colors['reset']} {answer}")

    def _print_history(self):
        print(f"\n{self.colors['system']}Histórico de mensagens:{self.colors['reset']}")
        for msg in self.history:
            color = self.colors.get(msg["role"], self.colors["reset"])
            print(f"{color}{msg['role'].capitalize()}:{self.colors['reset']} {msg['content']}")
        print("\n")
                
    def _output_response(self, response):
        self._print_answer(response)

    def _input_question(self):
        return input(f"{self.colors['user']}User:{self.colors['reset']} ")
    
    def _text_from_message(self,message):
        return "\n".join([block.text for block in message.content if block.type == "text"])
    
    ### Command Handling Methods ###
    def _handle_command(self, command):
        match command:
            case "exit" | "quit" | "sair" | "fechar" | "encerrar" | "q":
                print(f"{self.colors['system']}Encerrando a conversa.{self.colors['reset']}")
                exit()
            case "history":
                self._print_history()
            case _:
                print(f"{self.colors['system']}Comando desconhecido: {command}{self.colors['reset']}")
    
    def _is_command(self, question):
        if question[:1] == "/":
            command = question[1:].strip()
            return command
        else:
            return None
    
    ### Tool Use
    
    def current_datetime_tool(date_format="%Y-%m-%d %H:%M:%S"):
        if not date_format:
            raise ValueError("date_format cannot be empty")
        return datetime.now().strftime(date_format)

    def _run_tool(self, tool_name, tool_input):
        if tool_name == "str_replace_editor":
            command = tool_input["command"]
            if command == "view":
                return self.text_editor_tool.view(
                    tool_input["path"], tool_input.get("view_range")
                )
            elif command == "str_replace":
                return self.text_editor_tool.str_replace(
                    tool_input["path"], tool_input["old_str"], tool_input["new_str"]
                )
            elif command == "create":
                return self.text_editor_tool.create(tool_input["path"], tool_input["file_text"])
            elif command == "insert":
                return self.text_editor_tool.insert(
                    tool_input["path"],
                    tool_input["insert_line"],
                    tool_input["new_str"],
                )
            elif command == "undo_edit":
                return self.text_editor_tool.undo_edit(tool_input["path"])
            else:
                raise Exception(f"Unknown text editor command: {command}")
        else:
            raise Exception(f"Unknown tool name: {tool_name}")


    def _run_tools(self,message):
        tool_requests = [block for block in message.content if block.type == "tool_use"]
        tool_result_blocks = []

        for tool_request in tool_requests:
            try:
                tool_output = self._run_tool(tool_request.name, tool_request.input)
                tool_result_block = {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,
                    "content": json.dumps(tool_output),
                    "is_error": False,
                }
            except Exception as e:
                tool_result_block = {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,
                    "content": f"Error: {e}",
                    "is_error": True,
                }

            tool_result_blocks.append(tool_result_block)

        return tool_result_blocks

    ### Conversation Methods ###
    def _anthropic_ask(self, tools=None, system=None, temperature=0, stop_sequences=["```"]):
            params = {
                    "model": self.model,
                    "max_tokens": 1000,
                    "messages": [self.history],
                    "temperature": temperature,
                    "stop_sequences": stop_sequences,
                }
            
            if tools:
                params["tools"] = tools
            
                if system:
                    params["system"] = system
            
            message = self.client.messages.create(**params)
            answer = message.content[0].text
            # answer = "Desculpe, não consigo responder no momento."
            # return answer 

    def _ask(self, tools=None, system=None, temperature=0, stop_sequences=["```"]):
        if stop_sequences is None:
            stop_sequences = ["```"]
            
        kwargs = {
            "temperature": temperature,
        }
        
        if tools:
            kwargs["tools"] = tools
        if system:
            kwargs["system"] = system
        
        message = self.model.invoke(self.history,stop=stop_sequences,**kwargs)
        return message
    

    def chat(self, question):
        while True:
            self._add_user_message(question)
            answer = self._ask(question, tools=[self.text_editor_schema, self.web_search_schema])
            self._add_assistant_message(answer)
            print(self._text_from_message(answer))
            if answer.stop_reason != "tool_use":
                break
                
            tool_results = self.run_tools(answer)
            self._add_user_message(tool_results)
        
        return answer

    def start_conversation(self):
        while True:
            user_input = self._input_question()
            command = self._is_command(user_input)
            if command:
                self._handle_command(command)
            else:
                response = self.chat(user_input)
                self._output_response(response)

class Conversation:
    def __init__(self, agent):
        self.agent = agent
        self.history = []

    def mock_conversation(self):
        questions = [
            "Sou um estudante, tudo bem?",
            "Eu sou um estudante?",
            "Qual é a capital da França?",
            "Quem descobriu o Brasil?",
            "Qual é a fórmula da água?",
            "Qual é a velocidade da luz?",
            "Quem escreveu 'Dom Casmurro'?",
            "Qual é a distância entre a Terra e a Lua?"]
        for question in questions:
            response = self.agent.chat(question)
            print(f"Pergunta: {question}")
            print(f"Resposta: {response}\n")

class StreamingAgent(Agent):
    def __init__(self, model="claude-sonnet-4-0", system_message="Você é um assistente útil e prestativo."):
        super().__init__(model, system_message)
        self.stream_delay = 0.02  
    
    @timer
    @log
    def _output_response(self, stream, user_input):
        print(f"{self.colors['assistant']}Assistant:{self.colors['reset']} ",end="",flush=True)
        for char in stream(user_input):
            print(char, end="", flush=True)
            sleep(self.stream_delay)
    
    
    def _ask(self, question):
        # with self.client.messages.create_stream(
        #     model=self.model,
        #     max_tokens=1000,
        #     messages=self.history,
        #     stream=True
        # ) as stream:
        #     yield from stream.text_stream
            
        chunks = [
            "Hello ",
            "there! ",
            "This ",
            "is ",
            "a ",
            "streaming ",
            "response."
        ]

        for chunk in chunks:
            yield chunk     

    def chat(self, question):
        self._add_user_message(question)
        answer = ""
        for chunk in self._ask(question):
            answer += chunk
            yield from chunk
        yield "\n"
        self._add_assistant_message(answer)
        
    def start_conversation(self):
        while True:
            user_input = self._input_question()
            command = self._is_command(user_input)
            if command:
                self._handle_command(command)
            else:
                self._output_response(self.chat, user_input)

def main():
    # agent = StreamingAgent()
    # agent.start_conversation()
    agent = Agent()
    agent._add_user_message("2+2?")
    answer = agent._ask()
    print(answer)
    print(agent.model)
    
if __name__ == "__main__":
    main()