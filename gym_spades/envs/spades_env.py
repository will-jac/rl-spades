from gym_spades.envs.spades import spades, cards, player

import pickle
from datetime import datetime

class SpadesEnv():

    def __init__(self, players):

        self.players = players
        # self.results = [[] for i in range(4)]

    def _episode(self):
        self.game.reset()
        self.game.bid_round()

        for i in range(13):
            self.game.play_round()

        assert self.game.is_game_over()

        self.game.end_game()

        # for p in self.players:
        #     self.results[p.index].append(p.result())

    def _reset(self):
        self.game = spades(self.players)
        for p in self.players:
            p.points_hist = []

    def run(self, n):
        self._reset()
        for i in range(n):
            self._episode()
            #print("game over, resetting")

    def save(self, name=0):
        for i in range(4):
            f = open('training_output/'+ self.players[i].name + '-'+str(i)+'-'+str(name), 'wb')
            pickle.dump(self.players[i], f)
            f.close()
            self.players[i].total_rewards = 0

if __name__=="__main__":
    from gym_spades.envs.agents import rule_based_0, agent
    from gym_spades.envs.agents.fa import fa_agent, qfa, q_lambda, q_nstep_lambda, td_fa

    # eval as we go
    from gym_spades.envs import SpadesEvaluation
    import concurrent.futures
    import sys
    import csv

    def eval_agent(s_eval, agent):
        s_eval.load_agent(agent.create_player())
        return s_eval.eval(10, 10)

    # load in the agents
    # names = ['qfa/qfa0-1', 'qfa/qfa1-1', 'qfa/qfa2-1', 'qfa/qfa3-1']
    # agents = []
    # for n in names:
    #     with open(n, 'rb') as f:
    #         agent = pickle.load(f)
    #         agents.append(agent)

    # I would really love to change these, but it seems the model diverges :(
    epsilon = 0.1
    alpha = 0.1
    gamma = 0.01
    lambda_v = 0.4

    experiments = [
        # playing against other agents
        [
            [qfa(epsilon, alpha, gamma), 1, True],
            [q_lambda(epsilon, alpha, gamma, lambda_v), 1, True],
            [q_nstep_lambda(epsilon, alpha, gamma, lambda_v), 1, True],
            [td_fa(epsilon, alpha, gamma), 1, True]
        ],
        # complete self-play
        [
            [qfa(epsilon, alpha, gamma), 4, True]
        ],
        [
            [q_lambda(epsilon, alpha, gamma, lambda_v), 4, True]
        ],
        [
            [q_nstep_lambda(epsilon, alpha, gamma, lambda_v), 4, True]
        ],
        [
            [td_fa(epsilon, alpha, gamma), 4, True]
        ],
        # playing with heurisitics
        # qfa
        [
            [qfa(epsilon, alpha, gamma), 1, True],
            [agent(), 3, False]
        ],
        [
            [qfa(epsilon, alpha, gamma), 2, True],
            [agent(), 2, False]]
        ],
        [
            [qfa(epsilon, alpha, gamma), 1, True],
            [rule_based_0(), 3, False]
        ],
        [
            [qfa(epsilon, alpha, gamma), 2, True],
            [rule_based_0(), 2, False]
        ],
        # qfa_lambda
        [
            [q_lambda(epsilon, alpha, gamma, lambda_v), 1, True],
            [agent(), 3, False]
        ],
        [
            [q_lambda(epsilon, alpha, gamma, lambda_v), 2, True],
            [agent(), 2, False]
        ],
        [
            [q_lambda(epsilon, alpha, gamma, lambda_v), 1, True],
            [rule_based_0(), 3, False]
        ],
        [
            [q_lambda(epsilon, alpha, gamma, lambda_v), 2, True],
            [rule_based_0(), 2, False]
        ],
        # qfa_nstep_lambda
        [
            [q_nstep_lambda(epsilon, alpha, gamma, lambda_v), 1, True],
            [agent(), 3, False]
        ],
        [
            [q_nstep_lambda(epsilon, alpha, gamma, lambda_v), 2, True],
            [agent(), 2, False]
        ],
        [
            [q_nstep_lambda(epsilon, alpha, gamma, lambda_v), 1, True],
            [rule_based_0(), 3, False]
        ],
        [
            [q_nstep_lambda(epsilon, alpha, gamma, lambda_v), 2, True],
            [rule_based_0(), 2, False]
        ],
        # td_fa
        [
            [td_fa(epsilon, alpha, gamma), 1, True],
            [agent(), 3, False]
        ],
        [
            [td_fa(epsilon, alpha, gamma), 2, True],
            [agent(), 2, False]
        ],
        [
            [td_fa(epsilon, alpha, gamma), 1, True],
            [rule_based_0(), 3, False]
        ],
        [
            [td_fa(epsilon, alpha, gamma), 2, True],
            [rule_based_0(), 2, False]
        ],
    ]

    # 21 total experiments
    exp_num = int(sys.argv[1])

    # q = qfa(epsilon, alpha, gamma)
    # q_lambda = q_lambda(epsilon, alpha, gamma, lambda_v)
    # q_nstep_lambda = q_nstep_lambda(epsilon, alpha, gamma, lambda_v)
    # agents = [q, q_lambda, q_nstep_lambda]
    # agents = [q_lambda]
    # players = [q_lambda.create_player(), rule_based_0(), rule_based_0(), rule_based_0()]
    agents_and_num = experiments[exp_num]
    agents = []
    for a_n in agents_and_num:
        if a_n[2]:
            agents.append(a_n[0])
    players = [ a_n[0].create_player() for a_n in agents_and_num for n in range(a_n[1])]
    print(players)

    s = SpadesEnv(players)

    eval_envs = [SpadesEvaluation()]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        with open(sys.argv[2], 'a+') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['num_games', 'agent', 'convergence', 'rand_rpr', 'rand_ppg', 'rand_nwins', 'rand_winp', 'heur_rpr', 'heur_ppg', 'heur_nwins', 'heur_winp'])
            num_games_played = 0
            num_games_per_round = 10
            for i in range(0, 1000):
                # log scale reporting
                if i % num_games_per_round == 0:
                    num_games_per_round *= 10
                s.run(num_games_per_round)
                s.save(i)

                num_games_played += num_games_per_round
                # evaluate each agent on seperate threads
                future_to_output = {
                    executor.submit(eval_agent, eval_envs[i], agents[i]): agents[i].name for i in range(len(agents))
                }
                for future in concurrent.futures.as_completed(future_to_output):
                    agent_name = future_to_output[future]
                    try:
                        data = future.result()
                    except Exception as exc:
                        print('%r generated an exception: %s' % (agent_name, exc))
                        print(exc)
                    else:
                        writer.writerow([num_games_played, agent_name] + data)



