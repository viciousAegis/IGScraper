from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import csv
from tqdm import tqdm
import datasets
import pandas as pd
import torch
import time
import os

def get_image_text_data(f):
    posts = []
    with open(f, 'r') as f:
        reader = csv.reader(f)
        # drop header
        headers = next(reader)
        data = list(reader)
        
        required_keys = ['image_path', 'text']
        
        # append required keys to posts
        for d in tqdm(data):
            post = {}
            for key in required_keys:
                if key == 'image_path':
                    f_key = 'pk'
                else:
                    f_key = 'caption_text'
                post[f_key] = d[headers.index(key)]
            posts.append(post)
    return posts

def get_data(f):
    # if f contains 'image_text' in path, then use get_image_text_data()
    if 'image_text' in f:
        return get_image_text_data(f)
    posts = []
    with open(f, 'r') as f:
        reader = csv.reader(f)
        # drop header
        headers = next(reader)
        data = list(reader)
        
        required_keys = ['pk', 'caption_text']
        
        # append required keys to posts
        for d in tqdm(data):
            post = {}
            for key in required_keys:
                post[key] = d[headers.index(key)]
            posts.append(post)
    
    return posts

def get_dataset(posts):
    dataset = datasets.Dataset.from_pandas(pd.DataFrame(posts))
    return dataset

def preprocess_text(row):
    text = row['caption_text']
    # remove all words starting with #
    text = ' '.join([word for word in text.split() if not word.startswith('#')])
    # remove all words starting with @
    text = ' '.join([word for word in text.split() if not word.startswith('@')])
    # remove all words starting with http
    text = ' '.join([word for word in text.split() if not word.startswith('http')])
    
    # clean text to remove non-ascii characters
    text = text.encode("ascii", "ignore").decode()
    
    row['caption_text'] = text
    return row

def load_model(MODEL_NAME):
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    return model, tokenizer

def get_device():
    if torch.backends.mps.is_available():
        print ("MPS device found.")
        device = torch.device("mps")
    else:
        print ("MPS device not found.")
        device = torch.device("cpu")
    return device

def postprocess_text(answer):
    # remove pad and s tags
    answer = answer.replace('<pad>', '')
    answer = answer.replace('</s>', '')
    answer = answer.strip()
    return answer

def infer(dataset, PROMPT, model, tokenizer, device):
    outputs = []
    for i in tqdm(range(len(dataset))):
        inputs = tokenizer(
            PROMPT + dataset[i]['caption_text'],
            return_tensors='pt',
            max_length=512,
            truncation=True,
            padding='max_length',
            add_special_tokens=True
        ).to(device)
        
        input_ids = inputs['input_ids']
        start_time = time.time()
        output = model.generate(input_ids, max_new_tokens=20)
        inference_time = time.time() - start_time
        outputs.append({
            'pk': dataset[i]['pk'],
            'caption_text': dataset[i]['caption_text'],
            'output': postprocess_text(tokenizer.decode(output[0])),
            'inference_time': inference_time,
        })
    # calculate % of yes 
    yes_count = 0
    for output in outputs:
        if output['output'] == 'yes':
            yes_count += 1
    print(f"Percentage of posts left: {yes_count/len(outputs)}")
    print(f"Number of posts left: {yes_count}")
    
    return outputs, len(dataset), yes_count

def save_outputs(outputs, file_path):
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['pk', 'caption_text', 'output', 'inference_time'])
        for output in outputs:
            writer.writerow([output['pk'], output['caption_text'], output['output'], output['inference_time']])

def run(file_path, model, tokenizer, device):
    posts = get_data(file_path)
    dataset = get_dataset(posts).map(preprocess_text)

    print(dataset)
    
    PROMPT = "Does the following text contain information about food, cooking or anything related? Answer yes or no: "
    
    outputs, i_count, f_count = infer(dataset, PROMPT, model, tokenizer, device)
    
    result_path = file_path.split('/')[2:]
    result_path = "_".join(result_path)
    
    save_outputs(outputs, f'./t5_results/{result_path}')
    
    return i_count, f_count

if __name__ == '__main__':
    
    initial_post_count = 0
    final_post_count = 0

    
    MODEL_NAME = 'google/flan-t5-base'
    device = get_device()
    print("Loading model...")
    model, tokenizer = load_model(MODEL_NAME)
    model.to(device)
    print("Model loaded.")
    file_paths = []
    # get all csvs in post directory
    for root, dirs, files in os.walk('./posts'):
        for file in files:
            if file.endswith('.csv'):
                file_paths.append(os.path.join(root, file))
    print(file_paths)
    
    for path in file_paths:
        print(">>",path)
        i_count, f_count = run(path, model, tokenizer, device)
        print("--------------------")
        initial_post_count += i_count
        final_post_count += f_count

    print(f"Initial post count: {initial_post_count}")
    print(f"Final post count: {final_post_count}")
    
    print(f'Percentage of posts left: {final_post_count/initial_post_count}')