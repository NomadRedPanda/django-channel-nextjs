import json, os
from openai import OpenAI
from decouple import config

def get_client(llm_model):
    config_path = os.path.join(os.path.dirname(__file__), 'llm_config.json')    
    with open(config_path, 'r') as file:
        llm_config = json.load(file)

    select_config = [config for config in llm_config if llm_model in config.get("model", [])]
    select_config = select_config[0]
    # print(select_config)

    client = OpenAI(
        base_url=select_config['base_url'], 
        api_key=config(select_config['api_key'])
        )
    return client

def get_completion(client, 
                   llm_model, 
                   user_prompt="Say You forgot to give user prompt", 
                   system_prompt=None,
                   temperature=1
                   ):
    completion = client.chat.completions.create(
                                    model=llm_model,
                                    messages=[
                                        {"role": "system","content": system_prompt},
                                        {"role": "user","content": user_prompt}]
                                        ,
                                        temperature=temperature)
    return completion.choices[0].message.content