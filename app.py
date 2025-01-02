import json
from flask import Flask, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# File to store messages
MESSAGES_FILE = 'messages.json'

# Function to load messages from file
def load_messages():
    try:
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return an empty list if file doesn't exist

# Function to save messages to file
def save_messages(messages):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f)

# Initialize messages
messages = load_messages()

@app.route('/', methods=['GET', 'POST'])
def form():
    success_message = request.args.get('success', '')  # Check for success message in query parameters

    if request.method == 'POST':
        # Collect form data
        name = request.form['name']
        message = request.form['message']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save the message
        new_message = {'name': name, 'message': message, 'time': timestamp}
        messages.insert(0, new_message)
        save_messages(messages)  # Save messages to file

        # Redirect to the form with a success message
        return redirect(url_for('form', success='Message sent successfully!'))

    return f'''
    <form action="/" method="post">
        <input type="text" name="name" maxlength="24" placeholder="Your name" required><br>
        <textarea name="message" maxlength="280" placeholder="Enter your message..." required></textarea><br>
        <button type="submit">Submit</button>
    </form>
    <p>{success_message}</p>
    '''

@app.route('/view/<int:index>')
def view_message(index):
    total_messages = len(messages)

    if total_messages == 0:
        return '<h1>No messages available</h1>'

    # Ensure index is within bounds
    index = max(0, min(index, total_messages - 1))

    msg = messages[index]
    return f'''
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 15px;  /* Padding for the content */
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                width: 100vw;
                background-color: #f5f5f5;
                text-align: center;
                overflow: hidden;  /* Prevent scrollbars */
                box-sizing: border-box;
            }}
            .message {{
                flex: 1;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                font-size: calc(2vh + 2vw);
                overflow-wrap: break-word;
                word-wrap: break-word;
                max-width: 80%;
                max-height: 60%;  /* Ensure the message doesn’t exceed available space */
            }}
            .controls {{
                display: flex;
                justify-content: space-between;
                width: 100%;
                padding: 10px 20px;
                gap: 20px;
            }}
            .info {{
                margin-top: 10px;
                font-size: 14px;
                color: #555;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }}
            .delete {{
                color: red;
                cursor: pointer;
            }}
            .refresh {{
                color: blue;
                text-decoration: underline;
                cursor: pointer;
            }}
            button {{
                font-size: 16px;
                padding: 8px 16px;
                cursor: pointer;
                border: 1px solid #ccc;
                background-color: white;
                border-radius: 5px;
            }}
            button:hover {{
                background-color: #e9e9e9;
            }}
        </style>
    </head>
    <body>
        <div class="controls">
            <a href="/view/{max(0, index - 1)}"><button>Previous</button></a>
            <span>{index + 1} / {total_messages}</span>
            <a href="/view/{min(total_messages - 1, index + 1)}"><button>Next</button></a>
        </div>
        <div class="message">
            {msg['message']}
        </div>
        <div class="controls">
            <div class="info">
                <span><b>{msg['name']}</b> | {msg['time']}</span>
                <a class="refresh" href="/view/{index}">Refresh</a>
            </div>
            <form action="/delete/{index}" method="post" style="display:inline;">
                <button class="delete" type="submit">Delete</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/delete/<int:index>', methods=['POST'])
def delete_message(index):
    try:
        # Remove the specific message
        messages.pop(index)
        save_messages(messages)  # Save updated messages to file
    except IndexError:
        pass  # Ignore if the index is out of range
    return redirect(url_for('view_message', index=max(0, index - 1)))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
