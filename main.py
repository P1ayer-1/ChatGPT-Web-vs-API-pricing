from parse_convo import process_conversations
import tiktoken
from utils import handle_args, diplay_cost_all_time_frames, plot_costs_for_all_time_frames, diplay_cost_for_time_frame







def count_conversation_tokens(encoding, conversations):
    """
    Iterate over the conversations
    determine the total number of tokens sent by the user and chatgpt in the last 30 days
    """
    

    user_tokens = 0
    chatgpt_tokens = 0

    for conversation in conversations:
        for message in conversation['messages']:
            if message['author'] == 'user':
                user_tokens += len(encoding.encode(message['text']))
            elif message['author'] == 'ChatGPT':
                chatgpt_tokens += len(encoding.encode(message['text']))

    return user_tokens, chatgpt_tokens



def calculate_cost(user_tokens, chatgpt_tokens, user_token_price=0.00500, chatgpt_token_price=0.01500):
    """
    Calculate the cost of user and chatgpt tokens in dollars.

    Args:
        user_tokens (int): The number of tokens sent by the user.
        chatgpt_tokens (int): The number of tokens sent by ChatGPT.
        user_token_price (float, optional): The price of 1k user tokens. Defaults to 0.00500.
        chatgpt_token_price (float, optional): The price of 1k ChatGPT tokens. Defaults to 0.01500.

    Returns:
        tuple: A tuple containing the total cost of user tokens, chatgpt tokens, and total cost.
    """
    user_cost = (user_tokens / 1000) * user_token_price
    chatgpt_cost = (chatgpt_tokens / 1000) * chatgpt_token_price

    return user_cost, chatgpt_cost, user_cost + chatgpt_cost



def calculate_month(encoding, conversation_summary, time_frame):
    """ 
    Calculate the cost of user and chatgpt tokens in dollars for a specific month.

    Args:
        encoding (tiktoken.Encoding): The encoding of the model.
        conversation_summary (dict): The conversation summary.
        time_frame (str): The time frame to calculate the cost for.

    Returns:
        tuple: A tuple containing the total cost of user tokens, chatgpt tokens, and total cost.
    """
    user_tokens, chatgpt_tokens = count_conversation_tokens(encoding, conversation_summary[time_frame])
    user_cost, chatgpt_cost, total_cost = calculate_cost(user_tokens, chatgpt_tokens)
    return user_cost, chatgpt_cost, total_cost


def calculate_cost_for_all_time_frames(encoding, conversation_summary):
    """Calculate the cost for all time frames."""
    final_total_cost = 0
    final_user_cost = 0
    final_chatgpt_cost = 0

    cost_data = {}
    for time_frame in conversation_summary.keys():
        print(f"--- {time_frame.upper()} ---")
        user_cost, chatgpt_cost, total_cost = calculate_month(encoding, conversation_summary, time_frame)
        cost_data[time_frame] = (user_cost, chatgpt_cost, total_cost)
        final_total_cost += total_cost
        final_user_cost += user_cost
        final_chatgpt_cost += chatgpt_cost
        print(f"User Tokens Cost:      ${user_cost:.4f}")
        print(f"ChatGPT Tokens Cost:   ${chatgpt_cost:.4f}")
        print(f"Total Tokens Cost:     ${total_cost:.4f}")
        print("-" * 40)

    # Visualize costs for all time frames
    plot_costs_for_all_time_frames(cost_data, conversation_summary.keys())

    return final_total_cost, final_user_cost, final_chatgpt_cost



    


if __name__ == "__main__":

    # Should create save/load mechanism for conversation_summary.
    # right now, we process every time


    args = handle_args()

    output = process_conversations(args)

    conversation_summary = output if args.return_only else output[1]

    if not args.return_only:
        for info in output[0]:
            print(f"Created {info['file']} in directory {info['directory']}")


    encoding = tiktoken.encoding_for_model(args.model_name)


    if args.time_frame == 'all':
        final_total_cost, final_user_cost, final_chatgpt_cost = calculate_cost_for_all_time_frames(encoding, conversation_summary)
        diplay_cost_all_time_frames(final_total_cost, final_user_cost, final_chatgpt_cost, conversation_summary)


    else:
        time_frame = args.time_frame
        user_cost, chatgpt_cost, total_cost = calculate_month(encoding, conversation_summary, time_frame)
        diplay_cost_for_time_frame(
            user_cost, chatgpt_cost, total_cost, time_frame)





    