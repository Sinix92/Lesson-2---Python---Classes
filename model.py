import json


class Agent:

    def __init__(self, **agent_attributes):
        for attr_name, attr_value in agent_attributes.items():
            setattr(self, attr_name, attr_value)


def main():
    with open('agents-100k.json') as f:
        list_of_agents = json.load(f)
        for my_agent_attributes in list_of_agents:
            agent = Agent(**my_agent_attributes)
            print(agent.agreeableness)


main()