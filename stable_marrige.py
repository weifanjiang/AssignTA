import data_generator
import argparse

def run_stable_marrige(num_candidate, num_course):
    data = data_generator.generate(num_candidate, num_course)
    terminated = False
    applied_to = dict()
    unmatched = set()
    for candidate in data.candidates:
        applied_to[candidate] = set()
        unmatched.append(candidate)
    course_list = list(data.courses)
    while not terminated:
        curr_purpose = dict()
        for candidate in unmatched:
            courses_sorted = sorted(course_list, key = lambda x: data.candidate_preference[candidate][x], reverse = True)
            for course in courses_sorted:
                if course not in applied_to[candidate]:
                    applied_to[candidate].add(course)
                    curr_purpose[candidate] = course
                    break
            


        terminated = True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_candidate', type=int)
    parser.add_argument('--num_course', type=int)
    args = parser.parse_args()

    run_stable_marrige(args.num_candidate, args.num_course)

main()
