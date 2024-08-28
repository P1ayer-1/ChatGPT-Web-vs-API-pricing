import json
from pathlib import Path
import argparse
import matplotlib.pyplot as plt

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def handle_args():
    """
    Main function to parse arguments and process the conversations.
    """
    parser = argparse.ArgumentParser(
        description="Process conversation data from a JSON file."
    )
    parser.add_argument(
        "input_file", type=Path, help="Path to the input conversations JSON file."
    )

    parser.add_argument(
        "model_name",
        type=str,
        help="Name of the model used for token calculations.",
    )

    parser.add_argument(
        "time_frame",
        type=str,
        help="""Time frame to calculate tokens for. Format: $YYYY_MM  eg. `2024_08` or `all` for all conversations.
        If a specific date/month is given, it will only calculate the tokens for conversations that took place in that time frame.""",
    )

    parser.add_argument(
        "--output_dir",
        type=Path,
        help="Directory to save the output files.",
        required=False
    )

    parser.add_argument(
        "--return_only",
        action="store_true",
        help="Return only the created directories and files.",
        required=False
    )

 

    args = parser.parse_args()

    if not args.input_file.exists():
        print(f"Error: The input file '{args.input_file}' does not exist.")
        return
    
    return args




def diplay_cost_all_time_frames(final_total_cost, final_user_cost, final_chatgpt_cost, conversation_summary):
    """Display the cost summary for all time frames."""
    print("\n===== Overall Cost Summary =====\n")
    print(f"Overall User Tokens Cost:      ${final_user_cost:.4f}")
    print(f"Overall ChatGPT Tokens Cost:   ${final_chatgpt_cost:.4f}")
    print(f"Overall Total Tokens Cost:     ${final_total_cost:.4f}")
    print("=" * 40)


    # Visualize overall cost summary
    plot_overall_cost_summary(final_user_cost, final_chatgpt_cost)


def diplay_cost_for_time_frame(user_cost, chatgpt_cost, total_cost, time_frame):
    """
    Display the cost summary for a specific time frame.

    Args:
        encoding (tiktoken.Encoding): The encoding of the model.
        conversation_summary (dict): The conversation summary.
        time_frame (str): The time frame to calculate the cost for.
    """
    print(f"\n===== Cost Calculation for {time_frame.upper()} =====\n")
    print(f"User Tokens Cost:      ${user_cost:.4f}")
    print(f"ChatGPT Tokens Cost:   ${chatgpt_cost:.4f}")
    print(f"Total Tokens Cost:     ${total_cost:.4f}")
    print("-" * 40)

    # Visualize costs for a specific time frame
    plot_cost_for_time_frame(user_cost, chatgpt_cost, total_cost, time_frame)


def plot_cost_for_time_frame(user_cost, chatgpt_cost, total_cost, time_frame):
    labels = ['User Cost', 'ChatGPT Cost', 'Total Cost']
    costs = [user_cost, chatgpt_cost, total_cost]
    
    plt.figure(figsize=(8, 5))
    plt.bar(labels, costs, color=['blue', 'green', 'red'])
    
    plt.ylabel('Cost ($)')
    plt.title(f'Cost Breakdown for {time_frame.upper()}')
    plt.tight_layout()
    plt.show()



def plot_overall_cost_summary(final_user_cost, final_chatgpt_cost):
    labels = ['User Cost', 'ChatGPT Cost']
    costs = [final_user_cost, final_chatgpt_cost]
    colors = ['blue', 'green']

    plt.figure(figsize=(8, 8))
    plt.pie(costs, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    
    plt.title('Overall Cost Summary')
    plt.tight_layout()
    plt.show()


def plot_costs_for_all_time_frames(cost_data, time_frames):

    # reverse time frame ordering
    time_frames = list(time_frames)[::-1]

    user_costs = [cost_data[tf][0] for tf in time_frames]
    chatgpt_costs = [cost_data[tf][1] for tf in time_frames]
    total_costs = [cost_data[tf][2] for tf in time_frames]
    
    bar_width = 0.25
    index = range(len(time_frames))
    
    plt.figure(figsize=(10, 6))
    plt.bar(index, user_costs, bar_width, label='User Cost', color='blue')
    plt.bar([i + bar_width for i in index], chatgpt_costs, bar_width, label='ChatGPT Cost', color='green')
    plt.bar([i + 2 * bar_width for i in index], total_costs, bar_width, label='Total Cost', color='red')
    
    plt.xlabel('Time Frame')
    plt.ylabel('Cost ($)')
    plt.title('Cost Breakdown by Time Frame')
    plt.xticks([i + bar_width for i in index], time_frames)
    plt.legend()
    plt.tight_layout()
    plt.show()