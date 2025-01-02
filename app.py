import json
from flask import Flask, request, redirect, url_for, flash, get_flashed_messages
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

# File to store messages
MESSAGES_FILE = "messages.json"


# Function to load messages from file
def load_messages():
    try:
        with open(MESSAGES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return an empty list if file doesn't exist


# Function to save messages to file
def save_messages(messages):
    # Pretty print JSON for easier readability
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=4)


# Initialize messages
messages = load_messages()


@app.route("/", methods=["GET", "POST"])
def form():
    # Get any flashed messages
    success_message = get_flashed_messages()

    if request.method == "POST":
        # Collect form data
        name = request.form["name"]
        message = request.form["message"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save the message
        new_message = {"name": name, "message": message, "time": timestamp}
        messages.insert(0, new_message)
        save_messages(messages)  # Save messages to file

        # Persist success message
        flash("Message sent successfully!")
        return redirect(url_for("form"))  # Redirect to clear POST request

    # HTML with character limit feedback only for the message field
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
                background-color: white;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                box-sizing: border-box;
            }}
            h1 {{
                font-size: 33px;
                font-weight: 400;
                margin-bottom: 24px;
            }}
            form {{
                width: 100%;
                max-width: 500px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin-bottom: 16px;
            }}
            input, textarea {{
                font-family: Arial, sans-serif;
                font-size: 14px;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 5px;
                width: 100%;
                box-sizing: border-box;
            }}
            button {{
                font-family: Arial, sans-serif;
                font-size: 14px;
                padding: 12px;
                border: none;
                border-radius: 5px;
                background-color: black;
                color: white;
                cursor: pointer;
                width: 100%;
                margin-top: 16px;
            }}
            button:hover {{
                background-color: #333;
            }}
            .success-message {{
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: black;
                margin-top: 16px;
                text-align: center;
            }}
            .success-message a {{
                color: blue;
                text-decoration: underline;
                cursor: pointer;
            }}
            .char-count {{
                font-size: 12px;
                color: gray;
                margin-top: -10px;
                text-align: right;
            }}
        </style>
        <script>
            function updateCharCount(field, countField, maxLength) {{
                const remaining = maxLength - field.value.length;
                document.getElementById(countField).textContent = remaining + " characters remaining";
            }}
        </script>
    </head>
    <body>
        <h1>Echo-o-o-o-o</h1>
        <form action="/" method="post">
            <input 
                type="text" 
                name="name" 
                maxlength="24" 
                placeholder="Your name" 
                required
            >
            
            <textarea 
                name="message" 
                maxlength="280" 
                placeholder="Enter your message..." 
                required 
                oninput="updateCharCount(this, 'message-count', 280)"
            ></textarea>
            <p class="char-count" id="message-count">280 characters remaining</p>
            
            <button type="submit">Send</button>
        </form>
        {'<p class="success-message">' + success_message[0] + ' <a href="/">Close</a></p>' if success_message else ''}
    </body>
    </html>
    """


@app.route("/view/<int:index>")
def view_message(index):
    total_messages = len(messages)

    if total_messages == 0:
        return """
        <html>
        <body style="text-align: center; font-family: Arial;">
        <div class="message">No messages available<br>
        <a href="/">Go back to the form</a></div>
        </body>
        </html>
        """

    # Ensure index is within bounds
    index = max(0, min(index, total_messages - 1))

    msg = messages[index]
    return f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            width: 100vw;
            overflow: hidden; /* Prevent scrollbars */
            font-family: Arial, sans-serif;
            font-size: 14px;
        }}
        .message {{
            font-size: 5vw; /* Adjust font size relative to viewport width */
            text-align: center;
            margin: 0;
            word-wrap: break-word;
            white-space: normal;
            flex: 1; /* Allow it to grow and take up most of the space */
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .info, .controls, form {{
            margin: 10px 0;
        }}
        .controls a, .delete-btn {{
            font-size: 14px;
            padding: 10px;
            margin: 5px;
            text-decoration: none;
        }}
        .info {{
            font-size: 14px;
            text-align: center;
        }}
        p {{
            margin: 0;
        }}
        .delete-btn {{
            background-color: red;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
            padding: 8px 16px;
        }}
    </style>
</head>
<body>
    <p>{index + 1} / {total_messages}</p>
    <p class="message">{msg['message']}</p>
    <div class="info">
        <span><b>{msg['name']}</b><br>{msg['time']}<br>
        <a href="/view/{index}">Refresh</a></span>
    </div>
    <div class="controls">
        <a href="/view/{max(0, index - 1)}">Previous</a>
        <a href="/view/{min(total_messages - 1, index + 1)}">Next</a>
    </div>
    <form action="/delete/{index}" method="post">
        <button type="submit" class="delete-btn">Delete</button>
    </form>
</body>

    </html>
    """


@app.route("/delete/<int:index>", methods=["POST"])
def delete_message(index):
    try:
        # Remove the specific message
        messages.pop(index)
        save_messages(messages)  # Save updated messages to file
    except IndexError:
        pass  # Ignore if the index is out of range
    return redirect(url_for("view_message", index=max(0, index - 1)))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
