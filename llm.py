# %%
import csv
from dotenv import load_dotenv
import os
import random
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from time import time

# %%
template_with_context = """
You are Bob, a knowledgeable food expert. I will be giving you an Instagram text caption about ingredient substitutions. This text contains the given food, and its substitute. I want you to figure out and output the given food, and the substitute food accurately. The output should be a the given food and the replacement food, with each new pair in a new line.

If there are no obvious food substitutions, output -1, instead of the given food and the replacement food. There maybe multiple substitutions in a caption, so make sure to output all of them.

Some examples of what is expected:
{context}

Now answer as Bob and provide the output for the following caption, which would be the given food and the replacement food, each in a new line.

Caption: {caption}
Bob(Your Answer):
"""



# %%
def set_prompt(context=True):
    template = template_with_context
    return PromptTemplate(template=template, input_variables=["caption", "context"])

# %%
posts = []
with open('./t5_results/eatthisnotthat_2023-09-04_image_text.csv') as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        if(row[2].lower()=='no'):
            continue
        posts.append(row)


# %%
print(len(posts))

# %%
def gen_context(path, num=10):
    annotated_posts = []
    with open(path) as file:
        reader = csv.DictReader(file)
        for row in reader:
            annotated_posts.append(row)
    
    # select random posts
    annotated_posts = random.sample(annotated_posts, num)
    
    # generate context
    context = ''
    for post in annotated_posts:
        context += f'''Caption: {post['Post']}\nBob: {post['Ingredient'], post['Substitute']}\n\n'''
    
    return context

# %%
context = gen_context('./data/output.csv', num=8)

# %%
local_path = "./mistral-7b-instruct-v0.1.Q4_0.gguf"

# %%
# Callbacks support token-wise streaming
callbacks = [StreamingStdOutCallbackHandler()]

# Verbose is required to pass to the callback manager
llm = GPT4All(model=local_path, callbacks=callbacks, verbose=True)

# %%
prompt = set_prompt(context=context)
llm_chain = LLMChain(prompt=prompt, llm=llm)

# %%
context

# %%
with open('./results.csv', 'a') as file:
    writer = csv.DictWriter(file, fieldnames=['pk', 'caption', 'output', 'infer_time'])
    writer.writeheader()
    results = []
    for post in posts[:10]:
        pk = post[0]
        caption = post[1]
        st = time()
        out = llm_chain.run(caption=caption, context=context)
        infer_time = time() - st
        results.append({
            'pk': pk,
            'caption': caption,
            'output': out,
            'infer_time': infer_time
        })
        # write to file
        writer.writerow({
            'pk': pk,
            'caption': caption,
            'output': out,
            'infer_time': infer_time
        })
        print("Inference time: ", infer_time)

# %%
# save results to csv
with open('./results.csv', 'w') as file:
    writer = csv.DictWriter(file, fieldnames=['pk', 'caption', 'output'])
    writer.writeheader()
    for row in results:
        writer.writerow(row)

# %%



