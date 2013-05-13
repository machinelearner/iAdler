def nb_train():
    begin = open("./data/domain_difficulty/beginner.txt","r")
    inter = open("./data/domain_difficulty/intermediate.txt","r")
    advanced = open("./data/domain_difficulty/advanced.txt","r")
    training_set = {"beginner":begin.readlines(),"intermediate":inter.readlines(),"advanced":advanced.readlines()}
    from learning_engine.models import NBClassifier
    nbc = NBClassifier(training_set)
    nbc.train()

nb_train()
