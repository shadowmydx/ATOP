class RewardChain:
    def __init__(self):
        self.chain = list()
        self.reward_function_mapping = dict()
    
    def default_reward_processing(self, solution):
        for each_reward in self.chain:
            reward, should_return = each_reward(solution)
            if should_return:
                return reward
            
    def start_indexing_reward_processing(self, solution, start_index):
        for each_reward in self.chain[start_index: ]:
            reward, should_return = each_reward(solution)
            if should_return:
                return reward
            
    def add_reward_function(self, function, function_key):
        self.chain.append(function)
        self.reward_function_mapping[function_key] = len(self.chain) - 1
