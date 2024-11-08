from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import pyhdfs
import asyncio
import json
import os

# HDFS Configuration
HDFS_HOST = 'localhost'
HDFS_PORT = '9870'
HDFS_USER = 'hdoop'

class DataAnalysisAgent(Agent):
    class ReadFilesBehaviour(OneShotBehaviour):
        async def run(self):
            print("Data Analysis Agent started.")
            fs = pyhdfs.HdfsClient(hosts=f"{HDFS_HOST}:{HDFS_PORT}", user_name=HDFS_USER)
            try:
                # List files in HDFS
                files = fs.listdir('/user/hdoop/test_files')  # Use absolute path to your test directory
                print(f"Files found in HDFS: {files}")

                for file in files:
                    file_path = f'/user/hdoop/test_files/{file}'  # Construct absolute path
                    metadata = {
                        'name': file_path,
                        'size': fs.get_file_status(file_path).length,
                        'last_access': fs.get_file_status(file_path).accessTime,
                        'extension': os.path.splitext(file)[1].lower()  # Add file extension
                    }
                    print(f"Metadata for file {file_path}: {metadata}")

                    msg = Message(to="decision_agent@anonym.im")
                    msg.body = json.dumps(metadata)  # Convert dictionary to JSON string
                    msg.set_metadata("performative", "inform")
                    msg.set_metadata("purpose", "metadata")
                    await self.send(msg)
                    print(f"Sent metadata to Decision Agent: {metadata}")
                    await asyncio.sleep(1)  # Short delay between messages

                print("All file metadata sent. Stopping the agent.")
                await self.agent.stop()

            except pyhdfs.HdfsException as e:
                print(f"HDFS Exception: {e}")
                await self.agent.stop()

    async def setup(self):
        print("Data Analysis Agent setting up...")
        b = self.ReadFilesBehaviour()
        self.add_behaviour(b)

async def main():
    agent = DataAnalysisAgent("data_analysis_agent@anonym.im", "data_analysis_agent")
    await agent.start()
    
    # Wait for the agent to finish its task
    while agent.is_alive():
        await asyncio.sleep(1)
    
    print("Data Analysis Agent finished.")

if __name__ == "__main__":
    asyncio.run(main())
