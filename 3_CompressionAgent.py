from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import subprocess
import asyncio
import os

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode()

class CompressionAgent(Agent):
    class CompressFileBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("Compression Agent started.")
            self.compressed_files = set()

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                file_name, algorithm = msg.body.split('|')
                if file_name not in self.compressed_files:
                    print(f"Received compression task: {file_name} with {algorithm}")

                    dir_name = os.path.dirname(file_name)
                    base_name = os.path.splitext(os.path.basename(file_name))[0]

                    if algorithm == 'none':
                        print(f"Skipping compression for {file_name} as per decision.")
                        self.compressed_files.add(file_name)
                        return

                    # Set the correct file extension and compression command based on the algorithm
                    if algorithm == 'gzip':
                        compressed_file = f"{base_name}.gz"
                        compress_command = f"hadoop fs -cat {file_name} | gzip"
                    elif algorithm == 'bzip2':
                        compressed_file = f"{base_name}.bz2"
                        compress_command = f"hadoop fs -cat {file_name} | bzip2"
                    elif algorithm == 'lzo':
                        compressed_file = f"{base_name}.lzo"
                        compress_command = f"hadoop fs -cat {file_name} | lzop"
                    elif algorithm == 'zstd':
                        compressed_file = f"{base_name}.zst"
                        compress_command = f"hadoop fs -cat {file_name} | zstd"
                    elif algorithm == 'snappy':
                        compressed_file = f"{base_name}.snappy"
                        compress_command = f"hadoop fs -cat {file_name} | snzip"
                    else:
                        print(f"Unsupported compression algorithm: {algorithm}")
                        return

                    # Temporary file path
                    temp_file = f"{dir_name}/.temp_{compressed_file}"

                    # Full compression command for HDFS
                    full_command = f"{compress_command} | hadoop fs -put - {temp_file}"
                    stdout, stderr = run_command(full_command)

                    if stderr:
                        print(f"Error during compression: {stderr}")
                    else:
                        # If compression successful, remove the original and rename the compressed file
                        remove_command = f"hadoop fs -rm {file_name}"
                        move_command = f"hadoop fs -mv {temp_file} {dir_name}/{compressed_file}"

                        _, rm_stderr = run_command(remove_command)
                        _, mv_stderr = run_command(move_command)

                        if rm_stderr or mv_stderr:
                            print(f"Error replacing file: {rm_stderr} {mv_stderr}")
                        else:
                            print(f"Compressed and replaced file: {file_name} -> {compressed_file}")

                            # Notify Coordinator Agent
                            response = Message(to="coordinator_agent@anonym.im")
                            response.body = f"Compression of {file_name} completed with {algorithm}"
                            await self.send(response)
                            print(f"Sent completion message to Coordinator Agent.")

                            self.compressed_files.add(file_name)
                else:
                    print(f"File {file_name} already compressed. Skipping.")
            else:
                # No message received, check if we should stop
                if len(self.compressed_files) > 0:
                    print("No new messages. All files compressed. Stopping the agent.")
                    await self.agent.stop()

            await asyncio.sleep(1)  # Add a small delay to prevent busy-waiting

    async def setup(self):
        print("Compression Agent setting up...")
        b = self.CompressFileBehaviour()
        self.add_behaviour(b)

async def main():
    agent = CompressionAgent("compression_agent@anonym.im", "compression_agent")
    await agent.start()
    print("Compression Agent started.")
    
    # Wait for the agent to finish its task
    while agent.is_alive():
        await asyncio.sleep(1)
    
    print("Compression Agent finished.")

if __name__ == "__main__":
    asyncio.run(main())

