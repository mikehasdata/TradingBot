import logging
import re
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

'''
    Watches YouTube Videos
'''

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
        # Adjust your instructions here to clarify what you expect from the AI.
        instructions = (
            "Please write a Python script for a backtest, "
            "which includes a mock data set and simple buy/sell logic based on the strategy output provided. "
            "The script does not need to use backtesting.py or any actual historical data files. "
            "Assume the data is already loaded into a DataFrame 'df' with columns 'Open', 'High', 'Low', 'Close', and 'Volume'."
        )

        # Make sure your content does not mention backtesting.py if you do not want the AI to use it.
        content = f'''
# ... [other parts of the content]

# Generating mock data
date_range = pd.date_range(start="2020-01-01", end="2020-12-31", freq='D')
np.random.seed(42)
prices = np.random.lognormal(mean=0, sigma=0.1, size=len(date_range))
volume = np.random.randint(100, 1000, size=len(date_range))

df = pd.DataFrame({{
    'Open': prices,
    'High': prices * np.random.uniform(1, 1.1, size=len(date_range)),
    'Low': prices * np.random.uniform(0.9, 1, size=len(date_range)),
    'Close': prices,
    'Volume': volume
}}, index=date_range)

# ... [rest of the content]
'''

        backtest_output = create_and_run_assistant(
            name='Backtest Analyst',
            instructions=instructions,
            model='gpt-4-1106-preview',
            content=content,
            short_name=f'backtest_{trading_idea}'
        )
        if backtest_output:
            save_output_to_file(backtest_output, 'backtest', '/Users/micahdemarest/Desktop/coding/sniper_bot/output',
                                'py')
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


def get_youtube_video_id(url):
    # This function assumes that the URL is a valid YouTube link
    if 'youtube.com/watch' in url:
        # Extracts the video ID from standard YouTube URLs
        match = re.search(r"v=([^&]+)", url)
        if match:
            return match.group(1)
    elif 'youtu.be' in url:
        # Extracts the video ID from shortened YouTube URLs
        match = re.search(r"youtu\.be/([^?]+)", url)
        if match:
            return match.group(1)

    # If neither format matches, return None
    return None


def interactive_youtube_input():
    trading_ideas = []
    while True:
        url = input("Enter YouTube video URL (or type 'done' to finish): ")
        if url.lower() == 'done':
            break
        video_id = get_youtube_video_id(url)
        if video_id:
            transcript = get_youtube_transcript(video_id)
            if transcript:
                trading_ideas.append(transcript)
                print(f'Transcript added for video ID: {video_id}')
            else:
                print(f'No transcript found for video {video_id}')
        else:
            print('Invalid YouTube URL.')
    return trading_ideas


def main():
    trading_ideas = interactive_youtube_input()
    print(f'Collected {len(trading_ideas)} trading ideas.')

    for i, idea in enumerate(trading_ideas, start=1):
        print(f'Processing trading idea {i}/{len(trading_ideas)} from YouTube transcript.')
        strategy_output = create_and_run_data_analysis(idea)
        if strategy_output:
            print(f'Strategy output for idea {i} generated, proceeding to create backtest.')
            backtest_output = create_and_run_backtest(strategy_output, idea)
            if backtest_output:
                print(f'Backtest created for idea {i}.')
            else:
                print(f'Failed to generate backtest for idea {i}.')
        else:
            print(f'Failed to generate strategy output for idea {i}.')


# Only run the main function if this script is executed directly
if __name__ == "__main__":
    main()

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
