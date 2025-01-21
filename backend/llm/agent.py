'''
 TODO: Add langgraph memory
 '''
import sys
sys.path.append("..")

from langgraph.checkpoint.memory import MemorySaver # memory saver for keeping the context in the chat
from langchain_openai import AzureChatOpenAI
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, PromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from config_parser import read_config, set_env_variables
from langchain.schema import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langfuse.callback import CallbackHandler
########################################################################
# print("Current working directory:", os.getcwd())
# files = os.listdir(os.getcwd())
# print("Files and directories in the current directory:", files)

# config = RunnableConfig()

# shared_folder_path = os.path.join(os.path.dirname(__file__), '..', '..', '/shared')

# files = os.listdir('..',)
# print("Files and directories in the current directory:", files)
# print()
#######################################################################


memory = MemorySaver()

def get_db():    
    engine = create_engine ('sqlite:///shared/MysFinal_db.db', echo= False, future=True)
    db = SQLDatabase(engine)
    return db

config_path = "shared/config.ini"
config_values = read_config(config_path)

set_env_variables(config_values)
print(config_values)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

langfuse_handler = CallbackHandler(
    public_key=(config_values['LangFuse']['public_key']),
    secret_key=(config_values['LangFuse']['secret_key']),
    host=(config_values['LangFuse']['host'])
) 

llm = AzureChatOpenAI(
    temperature=(config_values['OpenAI']['temperature']),
    api_key=(config_values['OpenAI']['openai_api_key']),
    azure_endpoint=(config_values['OpenAI']['azure_openai_endpoint']),
    azure_deployment=(config_values['OpenAI']['azure_openai_deployment']),
    openai_api_version=(config_values['OpenAI']['azure_openai_api_version']),
    callback_manager=callback_manager, 
)

toolkit = SQLDatabaseToolkit(db=get_db(), llm=llm)
toolkit.get_tools()
#additional_explanation = 'Review the description of the tables and use it to guide how you construct queries based on the provided structure. \n Here is the structure: \nThe database consists of several tables detailing various aspects of employee and organizational information. The employees table contains personal details, contact information, job titles, organizational affiliations, performance scores, and employment history. \nThe mysProjects table links employees to projects, recording project managers, start and end dates, project codes, and names. \nThe orgHierarchy table outlines the organizational hierarchy, specifying employee ranks or positions. Some of the hierarchy levels written in TURKISH. \nThe workHistory table captures employees work experiences, including companies (in TURKISH), job titles (in TURKISH), and departments. \nThe certification table lists employees certifications (in TURKISH) with validity periods, while the comments table holds evaluations and scores given by others. \nThe educations table stores employees academic histories, including schools (in TURKISH), degrees (in TURKISH), and fields of study. \nThe languages table stores employees language proficiency in speaking, reading, and writing. All languages names are written in TURKISH.\n Leaves table records employee leave periods and types. \nThe scores table aggregates employee evaluations across criteria like character, compatibility, efficiency, and technical skills, with detailed breakdowns stored in the scoreDetails table. \nLastly, the softwares table tracks employees software skills, including proficiency, practice, and speed.\n '

additional_explanation = 'Review the description of the tables and use it to guide how you construct queries based on the provided structure. \n Here is the structure: \nThe database consists of several tables detailing various aspects of employee and organizational information. The employees table contains personal details, contact information, job titles, organizational affiliations, performance scores, and employment history. \nThe mysProjects table links employees to projects, recording project managers, start and end dates, project codes, and names. \nThe orgHierarchy table outlines the organizational hierarchy, specifying employee ranks or positions. Some of the hierarchy levels written in TURKISH. \nThe workHistory table contains previous work experiences, including previous companies (in TURKISH), previous job titles (in TURKISH), and previous departments. \nThe certification table lists employees certifications (in TURKISH) with validity periods.\nThe educations table stores employees academic histories, including schools (in TURKISH), degrees (in TURKISH), and fields of study. \nThe languages table stores employees language proficiency in speaking, reading, and writing. All languages names are written in TURKISH.\n Leaves table records employee leave periods and types. \nThe scores table aggregates employee evaluations across criteria like character, compatibility, efficiency, and technical skills, with detailed breakdowns stored in the scoreDetails table. \nLastly, the softwares table tracks employees software skills, including proficiency, practice, and speed.\n '
last_explanation = 'If the output from the database looks like sequence of (1,), modify the SQL query to use COUNT and return how many times (1,) appears. Replace the query with SELECT COUNT(*) FROM <table_name> WHERE <condition>;\n'
prompt_template = ChatPromptTemplate(input_variables=['dialect', 'top_k'], metadata={'lc_hub_owner': 'langchain-ai', 'lc_hub_repo': 'sql-agent-system-prompt', 'lc_hub_commit_hash': '31156d5fe3945188ee172151b086712d22b8c70f8f1c0505f5457594424ed352'}, messages=[SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['dialect', 'top_k'], template=('You are an agent designed to interact with a SQL database.\nGiven an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.\nUnless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.\nYou can order the results by a relevant column to return the most interesting examples in the database.\nNever query for all the columns from a specific table, only ask for the relevant columns given the question.\nYou have access to tools for interacting with the database.\nOnly use the below tools. Only use the information returned by the below tools to construct your final answer.\nYou MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.\n\nDO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.\n\nTo start you should ALWAYS look at the tables in the database to see what you can query.\nDo NOT skip this step.\nThen you should query the schema of the most relevant tables.\n' + additional_explanation + last_explanation)))])
assert len(prompt_template.messages) == 1

system_message = prompt_template.format(dialect="SQLite", top_k=5)
agent_executor = create_react_agent(
    llm, toolkit.get_tools(), checkpointer=memory, state_modifier=system_message)

def ask_openai(user_question):
    answer_chunks = []
    final_answer = None

    enable_tracing = config_values.get('LangFuse', {}).get('enable_tracing', False)
    
    # Initial config dictionary
    config = {
        "recursion_limit": 35,
        "configurable": {
            "thread_id": "1"  
        }
    }
    
    # Add tracing configuration if enabled
    if enable_tracing:
        config["callbacks"] = [langfuse_handler]
    try:
        # Streaming the response
        for chunk in agent_executor.stream(
            {"messages": [("user", user_question)]}, 
            stream_mode="values", 
            config=config
        ):
            answer_chunks.append(chunk)

        # Extracting the final answer
        for chunk in answer_chunks:
            for message in chunk["messages"]:
                if isinstance(message, AIMessage):
                    final_answer = message.content  # content of AIMessage
        
        # Check if we retrieved an answer
        if final_answer is None:
            raise ValueError("No valid response received from AI.")
    
    except ValueError as ve:
        # Handling specific errors like missing or invalid responses
        print(f"ValueError: {ve}")
    
    except Exception as e:
        # Catching general unexpected errors
        print(f"An unexpected error occurred: {e}")
    
    return final_answer
