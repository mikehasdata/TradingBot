import logging
import time
from openai.types.beta import thread
from youtube_transcript_api import YouTubeTranscriptApi

import dontshareconfig as d
from openai import OpenAI
import hashlib
import datetime
import youtube_transcript_api
from datetime import datetime
from openai import OpenAIError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(api_key=d.api_key)


# Functions our YouTube AI will use
def save_assistant_id(assistant_id, filename):
    filepath = f'/Users/micahdemarest/Desktop/coding/sniper_bot/ids/{filename}'
    with open(filepath, 'w') as file:
        file.write(assistant_id)


def generate_filename(base, content, extension):
    MAX_LENGTH = 50
    limited_content = (content[:MAX_LENGTH] + '..') if len(content) > MAX_LENGTH else content
    hash_part = hashlib.md5(limited_content.encode()).hexdigest()[:10]
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
        if message.role == 'assistant':
            for content_block in message.content:
                # Assuming each content_block is a TextContentBlock with a 'text' attribute that has a 'value' attribute
                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                    output += content_block.text.value.strip() + '\n'
    return output.strip()


def create_and_run_data_analysis(trading_idea):
    short_name = 'data_analysis'
    try:
        data_analysis_output = create_and_run_assistant(
            name='Data Analysis',
            instructions='Create a trading strategy based on the given youtube transcript',
            model='gpt-4-1106-preview',
            content=f'Create the trading strategy described here: {trading_idea}',
            short_name=short_name
        )
        if data_analysis_output:
            save_output_to_file(data_analysis_output, short_name,
                                '/Users/micahdemarest/Desktop/coding/sniper_bot/assistants/output', 'txt')
            return data_analysis_output
        else:
            print(f"No strategy output generated for {trading_idea}")
            return None
    except Exception as e:
        print(f"Error during data analysis: {e}")
        return None


def create_and_run_assistant(name, instructions, model, content, short_name):
    try:
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=[{"type": "code_interpreter"}],
            model=model
        )
        logging.info(f'Assistant {name} created with ID {assistant.id}')

        thread_response = client.beta.threads.create()
        thread_id = thread_response.id
        logging.info(f'Thread created with ID {thread_id}')

        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role='user',
            content=content
        )
        logging.info(f'Message sent to thread ID {thread_id}: {content}')

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant.id
        )
        logging.info(f'Run initiated for {name} with ID {run.id}')

        # Polling for run completion
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status in ['completed', 'failed', 'cancelled']:
                logging.info(f'Run {run.id} completed with status: {run_status.status}')
                break
            else:
                logging.info(f'Run {run.id} for {name} still in progress...waiting 5 seconds')
                time.sleep(5)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_output = extract_assistant_output(messages.data)
        return assistant_output

    except Exception as e:
        logging.error(f'Error in create_and_run_assistant for {name}: {e}')
        return None

    print(f'Run for {name} finished, fetching messages...')
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    assistant_output = extract_assistant_output(messages.data)

    return assistant_output


def create_and_run_backtest(strategy_output, trading_idea):
    if strategy_output:
        backtest_output = create_and_run_assistant(
            name='Backtest Analyst',
            instructions='Code a backtest for the given trading strategy using backtesting.py',
            model='gpt-4-1106-preview',
            content=f'Strategy Output: {strategy_output}. Please use backtesting.py to code a backtest for the trading strategy based on {trading_idea}.',
            short_name=f'backtest_{trading_idea}'
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
    if strategy_output:
        create_and_run_backtest(strategy_output, idea)
    else:
        print(f'No output was generated for the idea: {idea}')

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