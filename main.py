import os
import json
import base64
import requests
from openai import OpenAI
from apikey import gpt_api
from IPython.display import display,Markdown
from github_pat import pat
from repo_visualizer import visualize_repo
from repo_visualizer import fetch_file_url

# Define the URL of the repository
repo_url = "https://api.github.com/repos/QwenLM/Qwen2.5-VL/contents"

# Call the function to visualize the repository structure
visualize_repo(repo_url, pat)

file_name=input("Input file name: ") 
fetched_file_urls = fetch_file_url(repo_url, file_name, pat)

fetched_file_urls_index=0
if (len(fetched_file_urls)) > 1:
     print(fetched_file_urls)
     fetched_file_urls_index = input("Input URL index:")
     assert fetched_file_urls_index.replace('.', '', 1).isdigit(), "Error: Input should be a number."
     fetched_file_urls_index = int(fetched_file_urls_index)

headers = {"Authorization": f"Bearer {pat}"}
response = requests.get(fetched_file_urls[fetched_file_urls_index], headers=headers)
name, extension = os.path.splitext(file_name)


folder_path_json = "json"  
os.makedirs(folder_path_json, exist_ok=True)  # creates the folder if it doesn't exist

file_path = os.path.join(folder_path_json, f"{name}.json")

with open(file_path, "w") as json_file:
     json_file.write(json.dumps(response.json(), indent=4))

with open(file_path, "r") as json_file:
    data = json.load(json_file)  # Load JSON as a Python dictionary

decoded_file = base64.b64decode(data["content"]).decode('utf-8')

prompt_template = lambda decoded_file: f"""
You are a professional technical writer and summarization expert specializing in transforming complex documentation into concise, clear, and well-structured summaries. Your goal is to analyze the provided file from a repository and generate a professional summary.

### Guidelines:
1. **Relevance**:  
   - Focus on the **core purpose** of the file.  
   - Highlight key **features**, **functionalities**, and **intended use cases**.  
   - Identify the **target audience** or **users** of the file.

2. **Clarity**:  
   - Use **simple and precise language** to explain the file's purpose and usage.  
   - Avoid overly technical jargon unless necessary for understanding.  

3. **Organization**:  
   - Structure the summary with headings if appropriate (e.g., "Overview", "Key Features", "Usage").  
   - Ensure the output is **well-formatted** and easy to read.  

4. **Formatting**:  
   - Output the summary in **Markdown format**.  

5. **Important**:
   - l.
---

### Input:
- **file **:  
{decoded_file}

---

### Output:  
1. **Summary**:  
   - A **concise and well-structured summary** of the file.  
   - Highlights the file's **purpose**, **features**, and **usage**.  
   - Organized with headings for clarity and readability.

"""
prompt = prompt_template(decoded_file)
from tiktoken import encoding_for_model
import numpy as np

tokens = encoding_for_model('gpt-4o-mini').encode(decoded_file)
print(len(np.array(tokens)))


# setup api client
client = OpenAI(api_key=gpt_api)

# make api call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Expert software engineer summarization for files"},
        {"role": "user", "content": prompt}
    ], 
    temperature = 0.7
)

# extract response
response_string = response.choices[0].message.content

# display(Markdown(response_string))

folder_path_summaries = "summaries"  
os.makedirs(folder_path_summaries, exist_ok=True)  # creates the folder if it doesn't exist

file_path = os.path.join(folder_path_summaries, f"{name}_summary.md")

with open(file_path, "w") as summary_file:
     summary_file.write(response_string)