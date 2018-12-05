import data_generator
import argparse
import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
import networkx as nx

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def run_stable_marrige(data):
    terminated = False
    applied_to = dict()
    unmatched = set()
    for candidate in data.candidates:
        applied_to[candidate] = set()
        unmatched.add(candidate)
    qualified = dict()
    for candidate, qualification in data.qualification.items():
        for course, score in qualification.items():
            if score == 1:
                courses = qualified.get(candidate, set())
                courses.add(course)
                qualified[candidate] = courses
    course_list = list(data.courses)
    current_match = dict()
    for course in data.courses:
        current_match[course] = list()
    while not terminated:
        curr_purpose = dict()
        for candidate in unmatched:
            courses_sorted = sorted(course_list, key = lambda x: data.candidate_preference[candidate][x], reverse = True)
            for course in courses_sorted:
                if course not in applied_to[candidate] and course in qualified[candidate]:
                    applied_to[candidate].add(course)
                    curr_purpose[candidate] = course
                    break
        for candidate, course in curr_purpose.items():
            current_match[course].append(candidate)
        new_match = dict()
        curr_matched_candidates = set()
        for course, candidates in current_match.items():
            new_candidates = sorted(candidates, key = lambda x: data.course_preference[course][x], reverse = True)
            if len(new_candidates) > data.course_capacity[course]:
                new_candidates = new_candidates[0:data.course_capacity[course]]
            new_match[course] = new_candidates
            for c in new_candidates:
                curr_matched_candidates.add(c)
        current_match = new_match.copy()
        unmatched = set()
        for candidate in data.candidates:
            if candidate not in curr_matched_candidates:
                unmatched.add(candidate)
        terminated = True
        for candidate in unmatched:
            if len(applied_to[candidate]) < len(qualified[candidate]):
                terminated = False
    return current_match

def hungarian(data):
    rows = list(data.candidates)
    columns = []
    for course in data.courses:
        for i in range(data.course_capacity[course]):
            columns.append(course + '_' + str(i))
    counter = 0
    while len(columns) < len(rows):
        columns.append('dummy' + str(counter))
        counter += 1
    cost_mx = np.zeros((len(rows), len(columns)))
    not_qualify_penalty = 500000
    dummy_pref = 10
    for i in range(len(rows)):
        for j in range(len(columns)):
            if 'dummy' in columns[j]:
                cost_mx[i][j] = dummy_pref
            else:
                course = columns[j].split('_')[0]
                if data.qualification[rows[i]][course] == 0:
                    cost_mx[i][j] = not_qualify_penalty
                else:
                    cost_mx[i][j] = 2 - data.candidate_preference[rows[i]][course] - data.course_preference[course][rows[i]]
    row_ind, col_ind = linear_sum_assignment(cost_mx)
    total_cost = cost_mx[row_ind, col_ind].sum()
    if total_cost >= not_qualify_penalty:
        print("Error: data is generated badly, try again :)")
        exit(0)
    matching = dict()
    for course in data.courses:
        matching[course] = list()
    for i in range(len(rows)):
        if 'dummy' not in columns[col_ind[i]]:
            candidate = rows[row_ind[i]]
            course = columns[col_ind[i]].split('_')[0]
            matching[course].append(candidate)
    return matching
    

def maximal_matching(data):
    g = nx.Graph()
    courses = [course+"_"+str(i) for course in data.courses\
                for i in range(data.course_capacity[course])]
    for candidate in data.candidates:
        for course in courses:
            if data.qualification[candidate][course.split('_')[0]] == 1:
                sum_of_preference = data.candidate_preference[candidate][course.split('_')[0]] +\
                                    data.course_preference[course.split('_')[0]][candidate]
                g.add_edge(candidate, course, weight=sum_of_preference)
    matching = nx.maximal_matching(g)
    output = dict()
    for assignment in matching:
        assignment = sorted(assignment)
        candidate, course = assignment[0], assignment[1].split('_')[0]
        try:
            output[course].append(candidate)
        except(KeyError):
            output[course] = [candidate]
    return output

def write_to_file(data, matching, output, score, course_satisfication, candidate_satisfication):
    output_file = open(output, 'w')

    output_file.write("candidates preference to courses:\n")
    column_list = list(data.courses)
    column_list.insert(0, 'candidate')
    candidate_preference = pd.DataFrame(columns = column_list)
    for candidate, preference in data.candidate_preference.items():
        new_data = preference.copy()
        for course, qualification_score in data.qualification[candidate].items():
            if qualification_score == 0:
                new_data[course] = "Unqualified"
        new_data['candidate'] = candidate
        candidate_preference = candidate_preference.append(new_data, ignore_index = True)
    output_file.write(candidate_preference.to_string(index=False) + "\n")

    output_file.write("\ncourses capacity and preference to candidates:\n")
    column_list = list(data.candidates)
    column_list.insert(0, 'course')
    column_list.insert(1, 'capacity')
    course_preference = pd.DataFrame(columns = column_list)
    for course, preference in data.course_preference.items():
        new_data = preference.copy()
        for candidate in new_data.keys():
            if data.qualification[candidate][course] == 0:
                new_data[candidate] = "Unqualified"
        new_data['course'] = course
        new_data['capacity'] = data.course_capacity[course]
        course_preference = course_preference.append(new_data, ignore_index = True)
    output_file.write(course_preference.to_string(index=False) + "\n")
    output_file.write("\n")

    output_file.write("Final TA assignment:\n")
    for course, TAs in matching.items():
        new_data = dict()
        people = ""
        if len(TAs) == 1:
            people = TAs[0]
        else:
            people = TAs[0]
            for i in range(1, len(TAs)):
                people += ", " + TAs[i]
        new_data['assigned candidates'] = people
        output_file.write(course + ":," + people + "\n")
    
    output_file.write("\n")
    output_file.write("Score for assignment: {}\n".format(score))
    output_file.write("Percentage of courses get top 3 choice of candidates: {}\n".format(course_satisfication))
    output_file.write("Percentage of candidates get top 3 choice of courses: {}\n".format(candidate_satisfication))

def evaluate_matching(data, matching):
    score = 0
    total_matching = 0
    top_3_course = 0
    top_3_candidate = 0
    for course, candidates in matching.items():
        total_matching += len(candidates)
        candidate_ranking = list(data.candidates)
        candidate_ranking = sorted(candidate_ranking, key=lambda x: data.course_preference[course][x], reverse=True)
        for candidate in candidates:
            score += data.candidate_preference[candidate][course] + data.course_preference[course][candidate]
            course_ranking = list(data.courses)
            course_ranking = sorted(course_ranking, key=lambda x: data.candidate_preference[candidate][x], reverse=True)
            if candidate_ranking.index(candidate) < 3:
                top_3_course += 1
            if course_ranking.index(course) < 3:
                top_3_candidate += 1
    return round(score, 2), round(top_3_course * 100.0/total_matching, 2), round(top_3_candidate * 100.0/total_matching, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_candidate', type=int)
    parser.add_argument('--num_course', type=int)
    parser.add_argument('--output')
    parser.add_argument('--method')
    args = parser.parse_args()


    data = data_generator.generate(args.num_candidate, args.num_course)

    if args.method == 'stable_marrige':
        matching = run_stable_marrige(data)
        score, course_satisfication, candidate_satisfication = evaluate_matching(data, matching)
        write_to_file(data, matching, args.output, score, course_satisfication, candidate_satisfication)
    elif args.method == 'hungarian':
        matching = hungarian(data)
        score, course_satisfication, candidate_satisfication = evaluate_matching(data, matching)
        write_to_file(data, matching, args.output, score, course_satisfication, candidate_satisfication)
    elif args.method == "maximal_matching":
        matching = maximal_matching(data)
        score, course_satisfication, candidate_satisfication = evaluate_matching(data, matching)
        write_to_file(data, matching, args.output, score, course_satisfication, candidate_satisfication)
    else:
        print("haven't implemented yet")

if __name__ == "__main__":
    main()
