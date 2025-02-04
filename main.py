from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord Emoji Downloader</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white font-sans">
    <div class="flex justify-center items-center h-screen">
        <div class="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
            <h1 class="text-3xl font-bold text-center mb-6">Discord Emoji Downloader</h1>
            
            <p class="text-center text-yellow-400 mb-4">Follow the steps below to retrieve your Discord Token:</p>
            
            <div class="bg-gray-700 p-4 rounded-lg mb-4">
                <h2 class="text-xl font-semibold mb-2">How to Retrieve Your Discord Token:</h2>
                <ol class="list-decimal ml-5 text-sm">
                    <li>Open Discord in your web browser and log in.</li>
                    <li>Press <code>Ctrl + Shift + I</code> (Windows) or <code>Cmd + Option + I</code> (Mac) to open Developer Tools.</li>
                    <li>Go to the "Application" tab in Developer Tools.</li>
                    <li>In the left sidebar, under "Storage", select <code>Local Storage</code>.</li>
                    <li>Click on <code>https://discord.com</code>.</li>
                    <li>Look for the key named <code>token</code> and copy its value.</li>
                    <li>Paste the token into the field below to proceed.</li>
                </ol>
            </div>

            <!-- New Button to Get the Extension -->
            <a href="https://chromewebstore.google.com/detail/discord-get-user-token/accgjfooejbpdchkfpngkjjdekkcbnfd" target="_blank">
                <button class="w-full p-3 bg-green-600 rounded text-white font-bold hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-600 mt-4">
                    Get the Discord Token Extension
                </button>
            </a>

            <form id="downloadForm" class="space-y-4 mt-6">
                <div>
                    <label for="serverId" class="block text-sm font-medium">Server ID</label>
                    <input type="text" id="serverId" class="w-full p-3 mt-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-600" placeholder="Enter Server ID" required>
                </div>
                <div>
                    <label for="userToken" class="block text-sm font-medium">Your Token</label>
                    <input type="text" id="userToken" class="w-full p-3 mt-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-600" placeholder="Enter your Discord Token" required>
                </div>
                <button type="submit" class="w-full p-3 bg-blue-600 rounded text-white font-bold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 mt-4">Download Emojis</button>
            </form>
            
            <div id="loading" class="mt-4 text-center text-yellow-300 hidden">Downloading...</div>
            <div id="status" class="mt-4 text-center text-green-500 hidden">Emojis downloaded successfully!</div>
            <div id="error" class="mt-4 text-center text-red-500 hidden">Error occurred. Please check your details.</div>
        </div>
    </div>

    <script>
        // Handle form submission
        document.getElementById("downloadForm").addEventListener("submit", async function(event) {
            event.preventDefault();
            
            const serverId = document.getElementById("serverId").value;
            const userToken = document.getElementById("userToken").value;
            
            document.getElementById("loading").classList.remove("hidden");
            document.getElementById("status").classList.add("hidden");
            document.getElementById("error").classList.add("hidden");

            try {
                const response = await fetch("/download-emojis", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ serverId, userToken })
                });

                const result = await response.json();
                
                if (result.success) {
                    document.getElementById("loading").classList.add("hidden");
                    document.getElementById("status").classList.remove("hidden");
                } else {
                    document.getElementById("loading").classList.add("hidden");
                    document.getElementById("error").classList.remove("hidden");
                }
            } catch (error) {
                document.getElementById("loading").classList.add("hidden");
                document.getElementById("error").classList.remove("hidden");
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_code)

@app.route('/download-emojis', methods=['POST'])
def download_emojis():
    data = request.get_json()
    server_id = data.get('serverId')
    user_token = data.get('userToken')
    
    url = f"https://discord.com/api/v10/guilds/{server_id}"
    headers = {
        "Authorization": user_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        guild_data = response.json()
        emojis = guild_data.get("emojis", [])

        if not os.path.exists('emojis'):
            os.makedirs('emojis')

        for emoji in emojis:
            emoji_id = emoji['id']
            emoji_name = emoji['name']
            animated = emoji['animated']
            extension = 'gif' if animated else 'png'
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{extension}"

            emoji_response = requests.get(emoji_url)

            if emoji_response.status_code == 200:
                with open(f'emojis/{emoji_name}.{extension}', 'wb') as f:
                    f.write(emoji_response.content)
            else:
                return jsonify({"success": False})

        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

if __name__ == "__main__":
    app.run(debug=True)
