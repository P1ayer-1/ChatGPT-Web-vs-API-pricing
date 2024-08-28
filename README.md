# ChatGPT-Web-vs-API-pricing
I used this to determine the cost differential between my ChatGPT Plus subscription and the ChatGPT API.

I discovered I could save over $20 monthly by switching to the API.
The tax on the monthly ChatGPT Plus bill would cover an entire month of API usage for me.

Not sure if I'll ever clean this README up. I couldn't find a repo with this exact purpose, so I wanted to share.


### Usage:
1. [Export your conversation](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data)
2. Extract `conversations.json` to your preferred directory (ex. ./data). It is found in the chatlog export zip file (check your email)
3. Clone this repo with submodules `git clone https://github.com/P1ayer-1/ChatGPT-Web-vs-API-pricing.git`
4. Install requirements `pip install -r requirements.txt`
5. Run `main.py` and pass relevant args. Use `python main.py -h` to explain args

#### Example:
```
python main.py ./data/conversations.json gpt-4o all --return_only
```