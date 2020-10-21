from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents import rule_based_0
from gym_spades.envs import SpadesEnv

import pickle
import copy
from datetime import datetime
import numpy as np

import csv

flatten = lambda l: [item for sublist in l for item in sublist]

class SpadesEvaluation(SpadesEnv):

    def __init__(self):
        self.prev_weights = None

    def load_agent(self, agent_to_eval):
        agent_to_eval.bid_random = False
        agent_to_eval.epsilon = 0
        self.agent_to_eval = agent_to_eval

    def _load_comparison(self, comparison_agents):
        for a in comparison_agents:
            a.bid_random = False

        agent1 = copy.deepcopy(self.agent_to_eval)
        agent2 = copy.deepcopy(self.agent_to_eval)
        a = [agent1, comparison_agents[0], agent2, comparison_agents[1]]
        super().__init__(a)

    def num_wins(self, num_rounds):
        n = 0
        for i in range(num_rounds):
            a = self.players[0].points_hist[i]
            b = self.players[1].points_hist[i]
            if a > b:
                n += 1
        return n

    def _eval(self, n=100, rounds_per_game=50):
        for i in range(n):
            self.run(rounds_per_game)
            # index, rewards / round, points / game, num_wins
            yield (i, self.players[0].avg_rewards, sum(self.players[0].points_hist) / n, self.num_wins(rounds_per_game))

    def eval_random(self, n=100, rounds_per_game=50):
        self._load_comparison([player(), player()])

        reward_per_round_sum = points_per_game_sum = num_wins = 0
        for i, rpr, ppg, nw in self._eval(n, rounds_per_game):
            reward_per_round_sum += rpr
            points_per_game_sum += ppg
            num_wins += nw
        return [reward_per_round_sum / n, points_per_game_sum / n, num_wins, num_wins / (n*rounds_per_game)]

    def eval_heuristic(self, n=100, rounds_per_game=50):
        self._load_comparison([rule_based_0(), rule_based_0()])

        reward_per_round_sum = points_per_game_sum = num_wins = 0
        for i, rpr, ppg, nw in self._eval(n, rounds_per_game):
            reward_per_round_sum += rpr
            points_per_game_sum += ppg
            num_wins += nw
        return [reward_per_round_sum / n, points_per_game_sum / n, num_wins, num_wins / (n*rounds_per_game)]

    def eval_convergence(self):
        if self.prev_weights is None:
            self.prev_weights = self.agent_to_eval.parent.weights
            return [np.sum(np.absolute(self.prev_weights))]
        else:
            diff = np.sum(np.absolute(self.agent_to_eval.parent.weights - self.prev_weights))
            self.prev_weights = self.agent_to_eval.parent.weights
            return [diff]

    def eval(self, n=10, rounds_per_game=25):
        # returns list, eg [1, 2, 2, ... ]
        return self.eval_convergence() + self.eval_random(n, rounds_per_game) + self.eval_heuristic(n, rounds_per_game)

    def eval_to_csv(self, csv_writer, row_label, n=10, rounds_per_game=10):
        csv_writer.writerow([row_label] + self.eval(n, rounds_per_game))

if __name__ == "__main__":
    from gym_spades.envs.agents.fa import fa_agent, qfa, q_lambda, q_nstep_lambda #fa_agent, fa_lambda_player, fa_nstep_lambda_player,

    import sys, os
    import concurrent.futures

    if len(sys.argv) < 3:
        print('usage: spades_eval_env.py OUTPUT_CSV_NAME [PATH_TO_AGENT_FOLDER]+')
        exit()

    def eval_agent(path):
        s = SpadesEvaluation()
        #print(os.listdir(path))
        out = []
        file_list = os.listdir(path)
        files = sorted(file_list, key=lambda x:x[-2:])
        for filename in files:
            #print(filename)
            with open(os.path.join(path, filename), 'rb') as f:
                agent = pickle.load(f)
            s.load_agent(agent)
            out.append([filename] + s.eval(10, 10))
        return out

    with concurrent.futures.ThreadPoolExecutor() as executor:
        names = [sys.argv[i] for i in range(2, len(sys.argv))]
        future_to_output = {executor.submit(eval_agent, path): path for path in names}
        for future in concurrent.futures.as_completed(future_to_output):
            agent_name = future_to_output[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (agent_name, exc))
                print(exc)
            else:
                with open(sys.argv[1], 'a+') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['agent', 'convergence', 'rand_rpr', 'rand_ppg', 'rand_nwins', 'rand_winp', 'heur_rpr', 'heur_ppg', 'heur_nwins', 'heur_winp'])
                    for row in data:
                        writer.writerow(row)

                # for filename in os.listdir(sys.argv[i]):
                    # with open(os.path.join(sys.argv[i], filename), 'rb') as f:
                    #     agent = pickle.load(f)
                    # s.load_agent(agent)
                    # s.eval_to_csv(writer, filename)