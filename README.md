# A Multi-Agents System Solution For Intelligent File Compression in Hadoop

This project leverages a Multi-Agent System (MAS) to dynamically optimize file compression in Hadoop Distributed File System (HDFS). Autonomous agents work collaboratively to analyze, decide and apply the most efficient compression methods based on real-time data characteristics, enhancing both storage efficiency and data processing speeds.

## Overview
The goal of this project is to implement a multi-agent system within a Hadoop environment to intelligently manage file compression tasks. By using specialized agents that communicate and coordinate, the MAS dynamically optimizes storage utilization and processing efficiency. 
Key features include:
- Real-time file analysis and decision-making
- Compression algorithm selection based on file characteristics
- Coordinated task execution and error handling among agents

## Architecture
The system architecture consists of four specialized agents, each with a distinct role to improve storage efficiency and reduce computational overhead:

1. **Data Analysis Agent**: Gathers metadata from HDFS (e.g., file size, type, access frequency) to guide compression choices.
2. **Decision Agent**: Uses metadata to choose an optimal compression algorithm (e.g., Gzip, Bzip2), balancing speed, storage, and compatibility with MapReduce.
3. **Compression Agent**: Compresses files based on instructions, replaces original files, and skips already-compressed files for efficiency.
4. **Coordinator Agent**: Oversees and synchronizes agent activities, manages errors, and logs workflow status. 

This agent-based structure allows for parallel, scalable, and adaptable file compression within the Hadoop ecosystem.

## Communication Protocols
The agents communicate asynchronously via the Extensible Messaging and Presence Protocol (XMPP), supported by the Converse.js client interface:

- **Message Format**: Each agent exchanges structured XML stanzas for clear, organized communication.
- **Converse.js Integration**: Each agent uses a unique XMPP ID to log in and send messages via a lightweight web interface.
- **Workflow**: The Coordinator Agent initializes the process, monitors agent status, and manages task assignments based on real-time conditions, ensuring efficient collaboration across all agents.

## Technology Requirements
The following software and packages are required to set up and run this project:

- **Hadoop**: Distributed storage and processing (HDFS, YARN)
- **Python 3.x**: Core language for agent development
- **SPADE (Smart Python Agent Development Environment)**: Multi-agent system framework
- **Anaconda**: For managing Python environments
- **XMPP (via Converse.js)**: Communication protocol for agent interactions

## Setup and Installation

### Step 1: Starting Hadoop Components
before starting working on this project make sure that Hadoop is properly installed on your machine I prefer to use an Ubuntu VM to avoid unnecessary problems. (stay tuned for my Hadoop guide where I'll discuss Hadoop's proper installation and some implementation use cases)
```bash
#login to your Hadoop environment
fatima@ubuntu:~$ su hdoop
```
Before initializing the agents, start the Hadoop Distributed File System (HDFS) and YARN for resource management:
```bash
# Start HDFS
hdoop@ubuntu:~$ start_hdfs.sh

# Start YARN
hdoop@ubuntu:~$ start_yarn.sh
```
### Step 2: Create Conda Environment and Install Dependencies
Set up a Python environment using Conda and install SPADE for agent development:
```bash
# Create Conda environment
$ conda create -n mas_prj python=3.7

# Activate environment
$ conda activate mas_env

# Install required libraries
$ pip install spade
```
### Step 3: Agents's server creation
Make sure to create an ID and a password for each agent using the XMPP server of your choice (converse.js/Openfire/eJabberd...) and that they are online and connected to each others, this is the most crucial step to ensure agents's communication 
### Step 4: Set Up Agents
Each agent script can be created and edited using a text editor, such as nano:
```bash
# Create Data Analysis Agent script
$ nano data_analysis_agent.py

# Create Decision Agent script
$ nano decision_agent.py

# Create Compression Agent script
$ nano compression_agent.py

# Create Coordinator Agent script
$ nano coordinator_agent.py
```
### Step 5: Start Each Agent simultaneously 
Run each agent individually in separate terminal windows:
```bash
# Start Data Analysis Agent
$ python3 data_analysis_agent.py

# Start Decision Agent
$ python3 decision_agent.py

# Start Compression Agent
$ python3 compression_agent.py

# Start Coordinator Agent
$ python3 coordinator_agent.py
```
## Results
The MAS was tested with large and small files in HDFS, showing:

- 80% storage reduction for large files using Bzip2, optimizing space and maintaining splittability for MapReduce.
- 60% storage reduction for smaller files with Gzip, balancing speed with storage efficiency.

The MAS proved effective in streamlining Hadoop storage management, with efficient communication and error handling ensuring a reliable file compression process.

## Conclusion
This project showcases a powerful Multi-Agent System that brings intelligence and efficiency to file compression in Hadoop, significantly optimizing storage and processing performance. By automating compression decisions through coordinated agents, the MAS adapts dynamically to varying data needs, reducing storage costs and enhancing data accessibility.

For a detailed breakdown of the project’s architecture, communication protocols, testing, and future directions, please refer to the full article below:



