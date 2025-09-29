# Redis-Pub-Sub-Based-Chatbot
# Redis Pub/Sub Chatbot

A simple chatbot application built with Redis Pub/Sub for real-time messaging between multiple users. This project demonstrates the use of Redis as a message broker and database for storing user information and application data.

## Features

- User identification and profile storage in Redis
- Real-time messaging using Redis Pub/Sub
- Channel-based communication (join/leave channels)
- Special commands: weather updates, fun facts, user information
- Multiple concurrent users support
- Message timestamps
- Active channel tracking
- Message history per channel
- Private/direct messaging between users

## Technologies Used

- Python 3.x
- Redis 7.x
- Docker & Docker Compose
- redis-py library

## Project Structure

```
.
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Python client container configuration
├── mp1_template.py        # Main chatbot application
└── README.md              # This file
```

## Setup Instructions

### Prerequisites

- Docker installed on your system
- Docker Compose installed

### Installation Steps

1. Clone this repository:
```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

2. Start the containers using Docker Compose:
```bash
docker-compose up -d
```

3. Verify containers are running:
```bash
docker ps
```

You should see two containers:
- `python_client_container`
- `redis_container`

## Usage Instructions

### Starting the Chatbot

Run the chatbot in the Python client container:
```bash
docker exec -it python_client_container python mp1_template.py
```
<img width="1171" height="488" alt="image" src="https://github.com/user-attachments/assets/061dc1c7-c776-4cd4-b5e8-98f1feb4a0c6" />


### Available Commands
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
        - !online: List online users

#### User Management
- `identify <username> <age> <gender> <location>` - Register your user profile
  - Example: `identify alice 25 female newyork`

<img width="544" height="74" alt="image" src="https://github.com/user-attachments/assets/874fb4ed-aac0-4570-85e7-50274c060cff" />

#### Channel Operations
- `join <channel>` - Join a chat channel
  - Example: `join general`
- `leave <channel>` - Leave a chat channel
  - Example: `leave general`
- `send <channel> <message>` - Send a message to a channel
  - Example: `send general Hello everyone!`

<img width="472" height="198" alt="image" src="https://github.com/user-attachments/assets/f1811709-100a-4f5c-800c-bbfe7c444d26" />

#### Special Commands
- `!help` - Display available commands
- `!weather <city>` - Get weather information for a city
  - Example: `!weather boston`
- `!fact` - Get a random fun fact
- `!whoami` - Display your user information
- `!channels` - Show all channels you're subscribed to 
- `!history <channel>` - Display last 10 messages from a channel 
  - Example: `!history general`
- `dm <username> <message>` - Send a private message to another user 
  - Example: `dm bob Hey there!`
- `quit` - Exit the chatbot

### Testing Multiple Users

To test the Pub/Sub functionality with multiple users:

**Terminal 1:**
```bash
docker exec -it python_client_container python mp1_template.py
> identify alice 30 female newyork
> join general
> send general Hello from Alice!
```

**Terminal 2:**
```bash
docker exec -it python_client_container python mp1_template.py
> identify bob 25 male boston
> join general
```

Bob will see Alice's messages in the `general` channel.

<img width="451" height="34" alt="image" src="https://github.com/user-attachments/assets/670aa600-7dad-462e-a2fd-08f3ce0ee4fa" />

## Redis Monitoring

You can monitor Redis commands in real-time using the Redis CLI:

1. Access Redis CLI:
```bash
docker exec -it redis_container redis-cli
```

2. Start monitoring:
```redis
MONITOR
```

3. In another terminal, run chatbot commands and observe the Redis operations in real-time.

### Sample Monitor Output

<img width="1798" height="619" alt="image" src="https://github.com/user-attachments/assets/4e977a26-704f-4fbd-951e-a9357222e61e" />


## Development Process

### Task 1: Docker Setup
- Created `docker-compose.yml` with two services: Redis and Python client
- Configured networking between containers
- Set up volume for Redis data persistence

### Task 2: Chatbot Initialization
- Implemented `introduce()` method to display welcome message and available commands
- Designed user-friendly command interface

### Task 3: User Identification
- Implemented user registration system
- Used Redis Hash to store user information with key format `user:{username}`
- Stored username, age, gender, and location

### Task 4: Channels (Pub/Sub)
- Implemented `join_channel()` using Redis SUBSCRIBE
- Implemented `leave_channel()` using Redis UNSUBSCRIBE
- Implemented `send_message()` using Redis PUBLISH
- Implemented `read_message()` to receive messages from subscribed channels
- Tested multi-user communication successfully

### Task 5: Special Commands
- `!help`: Displays command list
- `!weather <city>`: Retrieves mock weather data from Redis (stored as key-value pairs)
- `!fact`: Retrieves random fun fact from Redis list
- `!whoami`: Retrieves and displays user information from Redis hash

### Extra Features 

#### 1. Message Timestamps 
- Added timestamps to all messages using Python's datetime module
- Format: `[HH:MM:SS] username: message`
- Helps users track when messages were sent

#### 2. Active Channel Tracking
- Tracks all channels user has joined in `self.active_channels` list
- `!channels` command displays all subscribed channels
- Updates list when joining or leaving channels

#### 3. Message History
- Stores last 50 messages for each channel in Redis list
- Key format: `history:{channel}`
- `!history <channel>` command displays last 10 messages
- Uses Redis `LPUSH` to add messages and `LTRIM` to maintain limit

#### 4. Private Messaging 
- Implemented direct messaging between users
- Each user automatically subscribes to private channel: `private:{username}`
- `dm <username> <message>` sends private message to specific user
- Verifies recipient exists before sending
- Private messages highlighted differently in output
- Includes timestamp and [PRIVATE] tag
  
### Challenges and Solutions

**Challenge 1**: Managing asynchronous message reception while waiting for user input
- **Solution**: Called `read_message()` at the beginning of each loop iteration to check for new messages

**Challenge 2**: Handling byte strings returned by Redis
- **Solution**: Used `.decode('utf-8')` to convert bytes to strings

**Challenge 3**: Testing Pub/Sub with multiple users
- **Solution**: Opened multiple terminal sessions running the same chatbot

## Redis Data Structures Used

1. **Hash** - User information storage
   - Key: `user:{username}`
   - Fields: username, age, gender, location

2. **String** - Weather data storage
   - Key: `weather:{city}`
   - Value: Weather information string

3. **List** - Fun facts storage
   - Key: `facts`
   - Values: Individual fun facts

4. **Pub/Sub** - Real-time messaging
   - Channels: User-defined channel names

## Future Enhancements

- Direct messaging between users
- Persistent message history
- User authentication
- Multiple channel subscriptions
- Message timestamps
- Online user list per channel

## GenAI Usage Disclosure

[If you used any GenAI tools like ChatGPT or Claude, describe:
- Used Claude to help structure the code, understand Redis commands, and create a README by what I've done.
- Created Docker containers by myself.
- All implementation and debugging was done independently, including testing chatbox functions in Docker terminal.
- Modified GenAI suggestions to simplify the code and match project requirements.
- GenAI helped to generate some fun facts and user, weather examples.

## Author

Margot Zhao
zhaosiyang95@gmail.com
9/29/2025

## License

This project was created for educational purposes as part of DS5760 NoSQL course.
