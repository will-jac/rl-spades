from gym.envs.registration import register

register(
    id='spades-v0',
    entry_point='gym_spades.envs:SpadesEnv',
)
register(
    id='spades-random-v0',
    entry_point='gym_spades.envs:SpadesRandomEnv',
)
register(
    id='spades-extrahard-v0',
    entry_point='gym_spades.envs:SpadesExtraHardEnv',
)