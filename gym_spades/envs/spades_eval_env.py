from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents import rule_based_0
from gym_spades.envs import SpadesEnv

import pickle
import copy
from datetime import datetime

class SpadesEvaluation(SpadesEnv):

    def __init__(self, agent_to_eval):
        agent_to_eval.bid_random = False
        agent_to_eval.epsilon = 0
        self.agent_to_eval = agent_to_eval

    def load(self, comparison_agents):
        for a in comparison_agents:
            a.bid_random = False

        agent1 = copy.deepcopy(self.agent_to_eval)
        agent2 = copy.deepcopy(self.agent_to_eval)
        a = [agent1, comparison_agents[0], agent2, comparison_agents[1]]
        super().__init__(a)

    def num_wins(self, num_rounds):
        n = 0
        for i in range(num_rounds):
            a = self.agents[0].points_hist[i]
            b = self.agents[1].points_hist[i]
            if a > b:
                n += 1
        return n

    def _eval(self, n=100, rounds_per_game=50):
        for i in range(n):
            self.run(rounds_per_game)
            # index, avg_rewards, points / game, num_wins
            yield (i, self.agents[0].avg_rewards, float(sum(self.agents[0].points_hist)) / (i+1), self.num_wins(rounds_per_game))

    def eval_random(self, n=100, rounds_per_game=50):
        self.load([player(), player()])
        yield from self._eval(n, rounds_per_game)

    def eval_heuristic(self, n=100, rounds_per_game=50):
        self.load([rule_based_0(), rule_based_0()])
        yield from self._eval(n, rounds_per_game)

    def eval(self, n=50, rounds_per_game=50):
        print('total number of runs =', n*rounds_per_game)
        tot_reward_per_game = tot_points_per_game = tot_num_wins = 0
        for i, rpg, ppg, nw in self.eval_random(n, rounds_per_game):
            tot_reward_per_game += rpg
            tot_points_per_game += ppg
            tot_num_wins += nw
        yield (tot_reward_per_game, tot_points_per_game, tot_num_wins, tot_num_wins / (n*rounds_per_game))

        tot_reward_per_game = tot_points_per_game = tot_num_wins = 0
        for i, rpg, ppg, nw in self.eval_heuristic(n, rounds_per_game):
            tot_reward_per_game += rpg
            tot_points_per_game += ppg
            tot_num_wins += nw
        yield (tot_reward_per_game, tot_points_per_game, tot_num_wins, tot_num_wins / (n*rounds_per_game))



if __name__ == "__main__":
    from gym_spades.envs.agents import fa_agent, qfa, rule_based_0

    import sys, os

    if len(sys.argv) != 2:
        print('invalid usage! please provide a folder of models to open for evaluation')
        exit()

    for filename in os.listdir(sys.argv[1]):
        with open(os.path.join(sys.argv[1], filename), 'rb') as f:
            agent = pickle.load(f)
        s = SpadesEvaluation(agent)
        for v in s.eval():
            print(v)