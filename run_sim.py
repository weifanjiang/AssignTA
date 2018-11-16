import stable_marrige

num_candidate = [50, 100, 500, 800, 1000]
num_course = [5, 10, 20, 25, 30]

for i in range(5):
    print('Doing trial ' + str(i + 1) + "...")
    output = "result/stable_marrige/trial" + str(i + 1) + ".txt"
    done = False
    while not done:
        try:
            stable_marrige.run_stable_marrige(num_candidate[i], num_course[i], output)
            done = True
        except:
            done = False

