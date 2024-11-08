from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import asyncio
import json
from datetime import datetime, timedelta

class DecisionAgent(Agent):
    class DecideCompressionBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("Decision Agent started.")
            self.processed_files = set()

        def choose_compression_algorithm(self, metadata):
            file_name = metadata['name']
            file_size = metadata['size']
            last_access = metadata['last_access']
            file_extension = file_name.split('.')[-1].lower()

            # Convert last_access to datetime
            last_access_time = datetime.fromtimestamp(last_access / 1000)
            current_time = datetime.now()

            # Define cold data threshold (not accessed in the last 30 days)
            cold_data_threshold = current_time - timedelta(days=30)

            # Check if it's cold data
            is_cold_data = last_access_time < cold_data_threshold

            if file_size > 1 * 1024 * 1024 * 990:  # Files larger than 1GB
                if is_cold_data:
                    return 'gzip'  # Prioritize size reduction for cold data
                else:
                    return 'bzip2'  # Splittable compression for hot large files
            elif file_size > 100 * 1024 * 1024:  # Files larger than 100MB
                if is_cold_data:
                    return 'gzip'
                else:
                    return 'lzo'  # Good balance of compression and speed for medium-sized hot files
            else:  # Smaller files
                if file_extension in ['txt', 'csv', 'log']:
                    return 'gzip'  # Good for text-based files
                elif file_extension in ['json', 'xml']:
                    return 'zstd'  # Efficient for structured text data
                elif file_extension in ['jpg', 'png', 'gif', 'gz', 'bz2', 'lzo', 'zst', 'snappy']:
                    return 'none'  # Already compressed, skip further compression
                else:
                    return 'snappy'  # Fast compression for small files of unknown type

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    metadata = json.loads(msg.body)
                    file_name = metadata['name']

                    if file_name not in self.processed_files:
                        print(f"Received metadata: {metadata}")

                        chosen_algorithm = self.choose_compression_algorithm(metadata)

                        print(f"Chosen compression algorithm for {file_name}: {chosen_algorithm}")

                        # Send chosen algorithm to Compression Agent
                        response = Message(to="compression_agent@anonym.im")
                        response.body = f"{file_name}|{chosen_algorithm}"
                        await self.send(response)
                        print(f"Sent chosen algorithm to Compression Agent for {file_name}.")

                        self.processed_files.add(file_name)
                    else:
                        print(f"File {file_name} already processed. Skipping.")

                except json.JSONDecodeError:
                    print("Error: Received invalid JSON data")
                except KeyError as e:
                    print(f"Error: Missing key in metadata: {e}")

            else:
                # No message received, check if we should stop
                if len(self.processed_files) > 0:
                    print("No new messages. All files processed. Stopping the agent.")
                    await self.agent.stop()

            await asyncio.sleep(1)  # Add a small delay to prevent busy-waiting

    async def setup(self):
        print("Decision Agent setting up...")
        b = self.DecideCompressionBehaviour()
        self.add_behaviour(b)

async def main():
    agent = DecisionAgent("decision_agent@anonym.im", "decision_agent")
    await agent.start()
    print("Decision Agent started.")
    
    # Wait for the agent to finish its task
    while agent.is_alive():
        await asyncio.sleep(1)
    
    print("Decision Agent finished.")

if __name__ == "__main__":
    asyncio.run(main())

