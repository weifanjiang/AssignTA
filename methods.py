import data_generator
import argparse
import pandas as pd
import numpy as np
import scipy

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
        for candidate in data.candidates:
            if candidate not in curr_matched_candidates:
                unmatched.add(candidate)
        terminated = True
        for candidate in unmatched:
            if len(applied_to[candidate]) < len(qualified[candidate]):
                terminated = False
    return matching

def hungarian(data):
    rows = list(data.candidates)
    columns = []
    for course in data.courses()

def write_to_file(data, matching, output):
    output_file = open(output + "", 'w')

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
        output_file.write(course + ": " + people + "\n")

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
        write_to_file(data, matching, args.output)
    elif args.method == 'hungarian':
        matching = hungarian(data)
        write_to_file(data, matching, args.output)
    else:
        print("haven't implemented yet")

if __name__ == "__main__":
    main()
