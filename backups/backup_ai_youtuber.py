import time
from openai.types.beta import thread
from youtube_transcript_api import YouTubeTranscriptApi

import dontshareconfig as d
from openai import OpenAI
import hashlib
import datetime
import youtube_transcript_api
from datetime import datetime

client = OpenAI(api_key=d.api_key)


# Functions our YouTube AI will use
def save_assistant_id(assistant_id, filename):
    filepath = f'/Users/micahdemarest/Desktop/coding/sniper_bot/ids/{filename}'
    with open(filepath, 'w') as file:
        file.write(assistant_id)


def generate_filename(base, content, extension):
    hash_part = hashlib.md5(content.encode()).hexdigest()[:10]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f'{base}_{hash_part}_{timestamp}.{extension}'


def save_output_to_file(output, base, directory, extension):
    if not output:
        print('No output to save')
        return
    filename = generate_filename(base, output, extension)
    filepath = f'{directory}/{filename}'
    with open(filepath, 'w') as file:
        file.write(output)
    print(f'Output saved to {filepath}')


def extract_assistant_output(messages):
    output = ''
    for message in messages:
        if message.role == 'assistant' and message.content and 'content' in message.content[0]:
            output += message.content[0].text.value + '\n'
    return output.strip()


def create_and_run_assistant(name, instructions, model, content, filename):
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model=model
    )
    print(f'Assistant {name} created...')
    save_assistant_id(assistant.id, filename=f'{filename}.txt')
    thread_response = client.beta.threads.create()  # This creates a new thread and returns a response object
    thread_id = thread_response.id

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=content
    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant.id
    )
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run_status.status in ['completed', 'failed', 'cancelled']:
            print(f'Run completed with status: {run_status.status}')
            break
        else:
            print(f'{name} run still in progress...waiting 5 seconds')
            time.sleep(5)
        print(f'Run for {name} finished, fetching messages...')
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return extract_assistant_output(messages.data)


def create_and_run_data_analysis(trading_idea):
    data_analysis_output = create_and_run_assistant(
        name='Data Analysis',
        instructions='Create a trading strategy based on the given youtube transcript',
        model='gpt-4-1106-preview',
        content=f'Create the trading strategy described here: {trading_idea}. The strategy should be detailed enough for another AI to code a backtest. Output only the step by step instructions for the backtesting ai to code a backtest.',
        filename='data_analysis'
    )
    if data_analysis_output:
        save_output_to_file(data_analysis_output, 'data_analysis', 'output', 'txt')
        return data_analysis_output
    else:
        print(f'No strategy output generated for {trading_idea}')
        return None


def create_and_run_risk_management(trading_idea):
    risk_management_output = create_and_run_assistant(
        name='Risk Management',
        instructions='Create a risk management plan for the given trading idea',
        model='gpt-4-1106-preview',
        content=f'Create a risk management plan for the trading strategy based on {trading_idea}. The plan should include the following: maximum risk per trade, position sizing, and risk-reward ratio.',
        filename='risk_management'
    )
    if risk_management_output:
        save_output_to_file(risk_management_output, 'risk_management', 'output', 'txt')
        return risk_management_output
    else:
        print(f'No risk management output generated for {trading_idea}')
        return None


def create_and_run_backtest(strategy_output, trading_idea):
    if strategy_output:
        backtest_output = create_and_run_assistant(
            name='Backtest Analyst',
            instructions='Code a backtest for the given trading strategy using backtesting.py',
            model='gpt-4-1106-preview',
            content=f'Strategy Output: {strategy_output}. Please use backtesting.py to code a backtest for the trading strategy based on {trading_idea}.',
            filename=f'backtest_{trading_idea}'
        )
        if backtest_output:
            save_output_to_file(backtest_output, 'backtest', 'output', 'txt')
            return backtest_output
        else:
            print(f'No backtest output generated for {trading_idea}')
            return None


def get_youtube_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['en'])
        return ' '.join([t['text'] for t in transcript.fetch()])
    except Exception as e:
        print(f'Error getting transcript for video {video_id}: {e}')
        return None


# trading_ideas_list = ['rsi + vwap', 'ema + bollinger', + 'macd + rsi', 'sma + adx', 'stochastic + atr', 'pivot lines', 'quarter theory', 'ichimoku', 'elliot waves','elliot waves + pivot lines', 'bolinger band contraction + volume', 'grid trading + fibbonacci']

yt_vids = ['https://www.youtube.com/watch?v=GuhUEZglNYE&pp=ygUjZWZmZWN0aXZlIHRyYWRpbmcgc3RyYXRlZ2llcyBjcnlwdG8%3D',
           'https://www.youtube.com/watch?v=T4zKrDvdMuA',
           'https://www.youtube.com/watch?v=jU2YQC7TC0k&t=59s&pp=ygUZdGhlIDEwMEsgdHJhZGluZyBzdHJhdGVneQ%3D%3D',
           'https://www.youtube.com/watch?v=gtTt_7E89TA&pp=ygUjdGhpcyB0cmFkaW5nIHN0cmF0ZWd5IG1hZGUgbWlsbGlvbnM%3D',
           'https://www.youtube.com/watch?v=mJqnG6-7kSs&pp=ygUjdGhpcyB0cmFkaW5nIHN0cmF0ZWd5IG1hZGUgbWlsbGlvbnM%3D',
           'https://www.youtube.com/watch?v=aKeDKLuE9HQ&pp=ygUsc2hlIG1hZGUgbWlsbGlvbnMgdHJhZGluZyB3aXRoIHRoaXMgc3RyYXRlZ3k%3D',
           'https://www.youtube.com/watch?v=EVW7Q0JY5mU&pp=ygU9c2hlIHdlbnQgZnJvbSBwb29yIHRvIHJpY2ggdHJhZGluZyBsaWtlIHRoaXMgdHJhZGluZyBzdHJhdGVneQ%3D%3D']

trading_ideas = []
for url in yt_vids:
    video_id = url.split('=')[1]
    transcript = get_youtube_transcript(video_id)
    if transcript:
        trading_ideas.append(transcript)
    else:
        print(f'No transcript found for video {video_id}')

for idea in trading_ideas:
    print(f'Processing {idea} from YouTube transcript')
    strategy_output = create_and_run_data_analysis(idea)
    create_and_run_backtest(strategy_output, idea)

    '''

    Code compiles successfuly here ... add payment details for ChatGPT Analysis and Backtesting
    --  03/26/2023


                            #TODO: Catch Solana & Base Stream
                    Link: https://www.youtube.com/watch?v=l_zwJ208jpw



    THE BIG PROJECT IDEA:
        - Create a bot that can watch a youtube video and then create a trading strategy based on the video
        - Utilize bot to apply trading strategy ideas to backtesting.py
        - Have ai_assistants algorithmically trade from my Solana wallet (sniping, hodling, etc) 
        - Have ai_assistants algorithmically trade from the Base wallet

    LONG TERM IDEA:
        - Utilize just 2 SOL (~$380) and turn it into $190,000 to $1.9M
        - Utilize volatility of Solana Memes for a 100x return per investment at maximum; 10x at minimum
        - Utilize base funds (est: ~$700) to establish Base project and grow it to $70,000 to $700,000 market cap (conservatively)

    KEY PERFORMANCE INDICATORS:
        - Generate at least $250,000 in one year from Solana Memes and Base project
        - Funnel this $250,000 investment into ISO20022 tokens
        - Apply AlgoTrading to short and long the markets to passively create income during recession and bull markets
        - Package skills into a purchasable Telegram Bot or product for others to apply as well (est worth: $500 per user)
        - Enjoy the free time and passive income generated from the projects, enabling me to own multiple property investments without need for credit
        - Hold a satisfied feeling of accomplishment and financial freedom, job security (by means of skills), and a sellable story for future endeavors
        - Make connections in the Discord ! I want at least ten relationships with 50% of them turning into friends or more. It's a helpful community, and we all have money.


    '''