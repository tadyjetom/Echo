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
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 14pt;
                color: black;
                background-color: white;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .form-container {{
                width: 90%;
                max-width: 400px;
                display: flex;
                flex-direction: column;
                gap: 1rem;
                padding: 1.5rem;
                border: 1px solid #ccc;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                background-color: white;
            }}
            .form-container input,
            .form-container textarea {{
                font-family: Arial, sans-serif;
                font-size: 14pt;
                padding: 0.75rem;
                border: 1px solid #ccc;
                border-radius: 5px;
                width: 100%;
                box-sizing: border-box;
            }}
            .form-container button {{
                font-family: Arial, sans-serif;
                font-size: 14pt;
                padding: 0.75rem;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                cursor: pointer;
            }}
            .form-container button:hover {{
                background-color: #0056b3;
            }}
            .success-message {{
                color: green;
                font-size: 12pt;
                margin-top: 10px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="form-container">
            <form action="/" method="post">
                <input type="text" name="name" maxlength="24" placeholder="Your name" required>
                <textarea name="message" maxlength="280" placeholder="Enter your message..." required></textarea>
                <button type="submit">Submit</button>
            </form>
            <p class="success-message">{success_message}</p>
        </div>
    </body>
    </html>
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
                padding: 15px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f5f5f5;
                text-align: center;
            }}
            .message-container {{
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 10px;
                max-width: 600px;
                background-color: white;
                text-align: left;
            }}
            .controls {{
                margin-top: 10px;
                display: flex;
                justify-content: space-between;
                width: 100%;
                max-width: 600px;
            }}
            button {{
                font-size: 14pt;
                padding: 10px 20px;
                border: 1px solid #ccc;
                background-color: white;
                border-radius: 5px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #e9e9e9;
            }}
        </style>
    </head>
    <body>
        <div class="message-container">
            <p><b>{msg['name']}</b> | {msg['time']}</p>
            <p>{msg['message']}</p>
        </div>
        <div class="controls">
            <a href="/view/{max(0, index - 1)}"><button>Previous</button></a>
            <a href="/view/{min(total_messages - 1, index + 1)}"><button>Next</button></a>
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
