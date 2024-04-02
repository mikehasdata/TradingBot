import shutil

import fitz  # PyMuPDF
import logging
import time
import hashlib
from datetime import datetime
import fitz  # PyMuPDF for reading PDFs
import dontshareconfig as d
from openai import OpenAI
import os

'''

    Reads PDF files

'''

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(api_key=d.api_key)

pdfs_folder = '/Users/micahdemarest/Desktop/coding/sniper_bot/assistants/pdfs'
read_folder = os.path.join(pdfs_folder, 'read')
if not os.path.exists(read_folder):
    os.makedirs(read_folder)


def chunk_text(text, max_chunk_size, context_window=500):
    """
    Splits the text into chunks with a context window to maintain continuity.
    """
    chunks = []
    start_index = 0
    while start_index < len(text):
        # Ensure we don't cut off in the middle of a word
        end_index = start_index + max_chunk_size
        if end_index < len(text) and text[end_index] not in [' ', '\n', '.', ',']:
            end_index = text.rfind(' ', start_index, end_index) + 1

        # If we've reached the end of the text, or we can include the whole text, then this is our last chunk
        if end_index >= len(text) or len(text) - start_index <= max_chunk_size:
            chunks.append(text[start_index:])
            break
        else:
            # Include the context window for the next chunk
            end_index_with_context = end_index + context_window
            # Ensure we don't exceed the text length
            if end_index_with_context > len(text):
                end_index_with_context = len(text)
            # Find the last complete sentence within the context window
            end_of_context = text.rfind('.', end_index, end_index_with_context) + 1
            if end_of_context == 0:  # No period found, fallback to end_index
                end_of_context = end_index_with_context
            chunks.append(text[start_index:end_of_context])
            # Start the next chunk after the original end index
            start_index = end_index
    return chunks


def process_pdf_file(pdf_path, max_chunk_size=32000):  # Example chunk size, adjust as needed
    text = extract_text_from_pdf(pdf_path)
    if text:
        print(f'Processing trading idea from PDF: {pdf_path}')
        chunks = chunk_text(text, max_chunk_size)
        all_strategy_outputs = []

        for chunk in chunks:
            strategy_output = create_and_run_assistant(
                name='Data Analysis',
                instructions='Create a trading strategy based on the given text',
                model='gpt-4-1106-preview',
                content=f'Create the trading strategy described here: {chunk}',
                short_name='data_analysis'
            )
            if strategy_output:
                all_strategy_outputs.append(strategy_output)
                # Consider saving each chunk's output separately or aggregating them
            else:
                print('No strategy output was generated for a chunk.')
                # Handle the failure as needed (e.g., skip, retry, etc.)

        # Combine all strategy outputs here if needed
        combined_strategy_output = "\n".join(all_strategy_outputs)
        if combined_strategy_output:
            save_output_to_file(combined_strategy_output, 'data_analysis', '/Users/micahdemarest/Desktop/coding/sniper_bot/assistants/output', 'txt')
            # Call backtest function or further process combined_strategy_output as needed
            backtest_code = create_backtest_code(combined_strategy_output)
            if backtest_code:
                save_output_to_file(backtest_code, 'backtest_code',
                                    '/Users/micahdemarest/Desktop/coding/sniper_bot/output', 'py')
                print('Backtest code generated and saved.')
            else:
                print('Failed to generate backtest code.')
        else:
            print('No combined strategy output was generated.')

    else:
        print(f'No text found in PDF {pdf_path}')

    # Move the PDF file to the 'read' folder after processing
    shutil.move(pdf_path, os.path.join(read_folder, os.path.basename(pdf_path)))

# Functions for the PDF-based AI

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
                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                    output += content_block.text.value.strip() + '\n'
    return output.strip()

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

        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status in ['completed', 'failed', 'cancelled']:
                logging.info(f'Run {run.id} completed with status: {run_status.status}')
                break
            else:
                logging.info(f'Run {run.id} still in progress...waiting 5 seconds')
                time.sleep(5)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_output = extract_assistant_output(messages.data)
        return assistant_output

    except Exception as e:
        logging.error(f'Error in create_and_run_assistant for {name}: {e}')
        return None

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ''
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f'Error reading PDF {pdf_path}: {e}')
        return None

def create_backtest_code(strategy_output):

    try:
        instructions = ('Write Python code for a backtest using the library backtesting.py. You do not need to have '
                        'access to backtesting.py locally, simply write the code and I will run it. It should be '
                        'based on this trading'
                        'strategy:')
        backtest_code = create_and_run_assistant(
            name='Backtest Code Generator',
            instructions=instructions,
            model='gpt-4-1106-preview',
            content=f'{instructions} {strategy_output}',
            short_name='backtest'
        )
        return backtest_code
    except Exception as e:
        logging.error(f'Error creating backtest code: {e}')
        return None


for pdf_file in os.listdir(pdfs_folder):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(pdfs_folder, pdf_file)
        process_pdf_file(pdf_path)