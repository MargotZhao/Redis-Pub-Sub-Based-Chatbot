import redis
import json
import random
from datetime import datetime

class Chatbot:
    def __init__(self, host='redis', port=6379):
        ''' Taks1: set up Docker container'''
        self.client = redis.StrictRedis(host=host, port=port)
        self.pubsub = self.client.pubsub()
        self.username = None
        self.active_channels = [] # EXTRA: show active channels
        self.initialize_data()

    def introduce(self):
        ''' Task 2: Provide an introduction and list of commands'''
        intro = """
        Welcome to Redis Chatbot!
        Available commands:
        - identify <username> <age> <gender> <location>: Set your user profile
        - join <channel>: Join a chat channel
        - leave <channel>: Leave a chat channel
        - send <channel> <message>: Send a message to a channel
        - !help: List of commands
        - !weather <city>: Weather update for a city
        - !fact: Random fun fact
        - !whoami: Your user information
        - quit: Exit the chatbot
        - !channels: Show your active channels
        - !history <channel>: Show message history
        - dm <username> <message>: Send private message

        Start by identifying yourself, then join a channel to chat!
        """
        print(intro)

    def identify(self, username, age, gender, location):
        ''' Taks 3: identify user information: name, age, gender, location '''
        self.username = username
        user_data = {
            'username': username,
            'age': age,
            'gender': gender,
            'location': location
        }
        self.client.hset(f"user:{username}", mapping=user_data)
        self.setup_private_channel()  # EXTRA: Setup private messaging
        print(f"User {username} identified successfully")
        
    def setup_private_channel(self):
        """
        EXTRA: Subscribe to personal channel for receiving private messages
        """
        if self.username:
            private_channel = f"private:{self.username}"
            self.pubsub.subscribe(private_channel)
            print(f"Listening for private messages on {private_channel}")
            
    def send_private_message(self, recipient, message):
        """
        EXTRA: Send private message to a specific user
        """
        if not self.username:
            print("Please identify yourself first")
            return
        
        # Check if recipient exists
        recipient_key = f"user:{recipient}"
        if not self.client.exists(recipient_key):
            print(f"User {recipient} not found")
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] [PRIVATE] {self.username}: {message}"
        
        # Publish to recipient's private channel
        private_channel = f"private:{recipient}"
        self.client.publish(private_channel, full_message)
        print(f"Private message sent to {recipient}")

    def join_channel(self, channel):
        ''' Task 4: join a channel '''
        self.pubsub.subscribe(channel) 
        if channel not in self.active_channels: # EXTRA: track active channels
            self.active_channels.append(channel)
        print(f"Joined channel: {channel}")

    def leave_channel(self, channel):
        ''' Task 4: leave a channel '''
        self.pubsub.unsubscribe(channel)
        if channel in self.active_channels: # EXTRA: track active channels
            self.active_channels.remove(channel)
        print(f"Left channel: {channel}")

    def send_message(self, channel, message):
        ''' Task 4: send message to a channel '''
        if not self.username:
            print("Please identify yourself first")
            return
        
        # EXTRA: add timestamp to messages
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {self.username}: {message}"
        self.client.publish(channel, full_message)
        
        # EXTRA: Store message history
        self.client.lpush(f"history:{channel}", full_message)
        self.client.ltrim(f"history:{channel}", 0, 49)
        print(f"Message sent to {channel}")

    def read_message(self):
        ''' Taks 4:: read messages from a channel '''
        # EXTRA: add timestamp to messages and highlight private messages
        message = self.pubsub.get_message()
        if message and message['type'] == 'message':
            channel = message['channel'].decode('utf-8')
            data = message['data'].decode('utf-8')
            
            # Highlight private messages differently
            if channel.startswith('private:'):
                print(f"\n*** PRIVATE MESSAGE ***")
                print(f"{data}")
                print("*" * 40 + "\n")
            else:
                print(f"[{channel}] {data}")
            
    def initialize_data(self):
        ''' Taks 5: initialize data of weather and fun facts '''
        weather_data = {
            'newyork': 'New York: 72°F, Partly Cloudy',
            'boston': 'Boston: 65°F, Sunny',
            'chicago': 'Chicago: 58°F, Rainy',
            'losangeles': 'Los Angeles: 80°F, Sunny',
            'miami': 'Miami: 85°F, Humid',
            'seattle': 'Seattle: 55°F, Overcast',
            'denver': 'Denver: 68°F, Clear',
            'austin': 'Austin: 78°F, Hot and Sunny'
        }
        
        for city, weather in weather_data.items():
            self.client.set(f"weather:{city}", weather)
        
        facts = [
            "Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs that was still edible.",
            "Octopuses have three hearts and blue blood.",
            "A group of flamingos is called a 'flamboyance'.",
            "Bananas are berries, but strawberries aren't.",
            "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion.",
            "A day on Venus is longer than a year on Venus.",
            "Dolphins have names for each other.",
            "The shortest war in history lasted 38 minutes.",
            "A cloud can weigh more than a million pounds.",
            "There are more stars in the universe than grains of sand on Earth."
        ]
        
        # Store facts in Redis list
        self.client.delete('facts')  
        for fact in facts:
            self.client.rpush('facts', fact)
            
    def show_channels(self):
        """
        EXTRA: New command to show active channels
        """
        if self.active_channels:
            print("You are subscribed to:")
            for channel in self.active_channels:
                print(f"  - {channel}")
        else:
            print("You are not subscribed to any channels")
            
    def show_history(self, channel, count=10):
        """
        EXTRA: Show message history for a channel
        """
        messages = self.client.lrange(f"history:{channel}", 0, count - 1)
        
        if messages:
            print(f"\n--- Last {len(messages)} messages in {channel} ---")
            for msg in reversed(messages): 
                print(msg.decode('utf-8'))
            print("---" + "-" * 40 + "\n")
        else:
            print(f"No message history for {channel}")

    def get_weather(self, city):
        ''' Task 5: get weather data for a city '''
        city_lower = city.lower()
        weather = self.client.get(f"weather:{city_lower}")
        
        if weather:
            print(weather.decode('utf-8'))
        else:
            print(f"Weather data not available for {city}")

    def get_fact(self):
        ''' Task 5: get a random fun fact '''
        fact = self.client.randomkey()
        fact_count = self.client.llen('facts')
        
        if fact_count > 0:
            random_index = random.randint(0, fact_count - 1)
            fact = self.client.lindex('facts', random_index)
            print(f"Fun Fact: {fact.decode('utf-8')}")
        else:
            print("No facts available")

if __name__ == "__main__":
    ''' Task 2: initialize chatbox'''
    bot = Chatbot()
    bot.introduce()
    
    while True:
        # Taks4: Check for incoming messages from subscribed channels
        bot.read_message()
        
        user_input = input("> ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        # Task3: uer identification
        elif user_input.startswith('identify '):
            parts = user_input.split()
            if len(parts) >= 5:
                username = parts[1]
                age = parts[2]
                gender = parts[3]
                location = ' '.join(parts[4:])
                bot.identify(username, age, gender, location)
            else:
                print("Usage: identify <username> <age> <gender> <location>")
        
        # Task 4: join channel
        elif user_input.startswith('join '):
            parts = user_input.split()
            if len(parts) >= 2:
                channel = parts[1]
                bot.join_channel(channel)
            else:
                print("Usage: join <channel>")
                
        elif user_input == '!channels':
            bot.show_channels()
        
        # Task 4: leave channel
        elif user_input.startswith('leave '):
            parts = user_input.split()
            if len(parts) >= 2:
                channel = parts[1]
                bot.leave_channel(channel)
            else:
                print("Usage: leave <channel>")
        
        # Task 4: send message to a channel
        elif user_input.startswith('send '):
            parts = user_input.split(maxsplit=2)
            if len(parts) >= 3:
                channel = parts[1]
                message = parts[2]
                bot.send_message(channel, message)
            else:
                print("Usage: send <channel> <message>")
        
        # Task 5: show user information
        elif user_input == '!whoami':
            if bot.username:
                user_data = bot.client.hgetall(f"user:{bot.username}")
                if user_data:
                    info = {key.decode('utf-8'): value.decode('utf-8') for key, value in user_data.items()}
                    print(f"Username: {info['username']}, Age: {info['age']}, Gender: {info['gender']}, Location: {info['location']}")
                else:
                    print("User information not found")
            else:
                print("Please identify yourself first")
        
        # Task 5: weather
        elif user_input.startswith('!weather '):
            parts = user_input.split(maxsplit=1)
            if len(parts) >= 2:
                city = parts[1]
                bot.get_weather(city)
            else:
                print("Usage: !weather <city>")
         
         # Task 5: fun facts       
        elif user_input == '!fact':
            bot.get_fact()
        
        # Taks 5: !help        
        elif user_input == '!help':
            bot.introduce()
            
        elif user_input.startswith('!history '):
            parts = user_input.split()
            if len(parts) >= 2:
                channel = parts[1]
                bot.show_history(channel)
            else:
                print("Usage: !history <channel>")
                
        elif user_input.startswith('dm '):
            parts = user_input.split(maxsplit=2)
            if len(parts) >= 3:
                recipient = parts[1]
                message = parts[2]
                bot.send_private_message(recipient, message)
            else:
                print("Usage: dm <username> <message>")
        
        else:
            print("Unknown command")
            
