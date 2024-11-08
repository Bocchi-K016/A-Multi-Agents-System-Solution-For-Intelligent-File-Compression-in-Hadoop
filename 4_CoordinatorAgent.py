from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import asyncio
import json
import re

class CoordinatorAgent(Agent):
    class CoordinateBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("Coordinator Agent started.")
            self.tasks = {}
            self.agents = {
                "data_analysis": "data_analysis_agent@anonym.im",
                "decision": "decision_agent@anonym.im",
                "compression": "compression_agent@anonym.im"
            }

        async def run(self):
            msg = await self.receive(timeout=10)  # Wait for messages with a timeout
            if msg:
                try:
                    # Attempt to parse JSON
                    content = json.loads(msg.body)
                    sender = msg.sender.split("/")[0]  # Get the agent JID without resource

                    if content['type'] == 'task_complete':
                        await self.handle_task_completion(content)
                    elif content['type'] == 'error':
                        await self.handle_error(content)
                    elif content['type'] == 'new_task':
                        await self.assign_task(content)
                    elif content['type'] == 'agent_status':
                        await self.handle_agent_status(content, sender)
                except json.JSONDecodeError:
                    # Handle message not in JSON format (e.g., messages from compression agent)
                    print(f"Received non-JSON message: {msg.body}")
                    self.handle_compression_message(msg.body)
                except KeyError as e:
                    print(f"Received message with missing key: {e}")

            # Check for task timeouts
            await self.check_task_timeouts()

            # Stop agent if all tasks are complete
            if self.tasks and all(task['status'] == 'complete' for task in self.tasks.values()):
                print("All tasks completed. Stopping Coordinator Agent.")
                await self.agent.stop()

        def handle_compression_message(self, message_body):
            # Define pattern to match the compression result messages
            pattern = r"Compression of (.+) completed with (.+)"
            match = re.match(pattern, message_body)

            if match:
                file_path = match.group(1)
                algorithm = match.group(2)
                print(f"Compression of {file_path} completed with {algorithm}.")
                # Further processing logic can be added here
            else:
                print("Message format not recognized. No behaviour matched for message.")

        async def assign_task(self, content):
            task_id = content['task_id']
            task_type = content['task_type']
            file_name = content['file_name']
            self.tasks[task_id] = {
                'type': task_type,
                'file': file_name,
                'status': 'assigned',
                'assigned_to': self.agents[task_type],
                'timestamp': asyncio.get_event_loop().time()
            }
            msg = Message(to=self.agents[task_type])
            msg.body = json.dumps({
                'task_id': task_id,
                'file_name': file_name,
                'action': task_type
            })
            await self.send(msg)
            print(f"Assigned task {task_id} ({task_type}) for file {file_name} to {self.agents[task_type]}")

        async def handle_task_completion(self, content):
            task_id = content['task_id']
            if task_id in self.tasks:
                self.tasks[task_id]['status'] = 'complete'
                print(f"Task {task_id} completed: {content['result']}")
            else:
                print(f"Received completion for unknown task: {task_id}")

        async def handle_error(self, content):
            task_id = content['task_id']
            if task_id in self.tasks:
                self.tasks[task_id]['status'] = 'error'
                print(f"Error in task {task_id}: {content['error_message']}")
            else:
                print(f"Received error for unknown task: {task_id}")

        async def handle_agent_status(self, content, sender):
            status = content.get('status')
            if status == 'start':
                print(f"Agent {sender} started working.")
            elif status == 'finish':
                print(f"Agent {sender} finished its work.")

        async def check_task_timeouts(self):
            current_time = asyncio.get_event_loop().time()
            for task_id, task in self.tasks.items():
                if task['status'] == 'assigned' and current_time - task['timestamp'] > 300:  # 5 minutes timeout
                    print(f"Task {task_id} timed out. Reassigning...")
                    await self.assign_task({
                        'task_id': task_id,
                        'task_type': task['type'],
                        'file_name': task['file']
                    })

    async def setup(self):
        print("Coordinator Agent setting up...")
        template = Template()
        template.set_metadata("performative", "inform")
        b = self.CoordinateBehaviour()
        self.add_behaviour(b, template)

async def main():
    agent = CoordinatorAgent("coordinator_agent@anonym.im", "coordinator_agent")
    await agent.start()
    print("Coordinator Agent started.")

    # Wait for the agent to finish its task
    while agent.is_alive():
        await asyncio.sleep(1)
    print("Coordinator Agent finished.")

if __name__ == "__main__":
    asyncio.run(main())

