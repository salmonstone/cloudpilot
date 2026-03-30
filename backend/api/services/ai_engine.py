from groq import Groq
import os, json

client = Groq(api_key=os.environ['GROQ_API_KEY'])

def analyze_costs(cost_data: dict, idle_resources: list) -> list:
    prompt = f'''
    You are an AWS cost optimization expert.
    Analyze this data and return ONLY a JSON array of recommendations.

    Cost data (last 30 days): {json.dumps(cost_data)}
    Idle resources: {json.dumps(idle_resources)}

    Each recommendation must have:
    - id: unique string like rec-001
    - type: resize | delete | storage_class | rightsizing
    - resource: AWS resource ID
    - current: current config
    - suggested: suggested config
    - reason: explanation with data
    - monthly_saving: estimated dollars saved
    - confidence: 0.0 to 1.0
    - auto_fixable: true or false
    '''
    response = client.chat.completions.create(
        model='llama-3.1-70b-versatile',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.1
    )
    return json.loads(response.choices[0].message.content)
