import pickle

def load(f_name):
    f = open(f_name, "rb")
    a = pickle.load(f)
    print(a.weights)
    print(a.avg_rewards)
    print(a.team_bid, a.bid_amount)
    print(a.rewards)
    print(a.prev_features)
    return(a)


if __name__=="__main__":
    import sys
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            load(str(sys.argv[i]))
    else:
        print("error! please provide file names")
