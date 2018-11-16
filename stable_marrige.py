import data_generator
import argparse

def run_stable_marrige(num_candidate, num_course, output):
    data = data_generator.generate(num_candidate, num_course)
    terminated = False
    applied_to = dict()
    unmatched = set()
    for candidate in data.candidates:
        applied_to[candidate] = set()
        unmatched.add(candidate)
    qualified = dict()
    for c
    course_list = list(data.courses)
    current_match = dict()
    for course in data.courses:
        current_match[course] = list()
    while not terminated:
        curr_purpose = dict()
        for candidate in unmatched:
            courses_sorted = sorted(course_list, key = lambda x: data.candidate_preference[candidate][x], reverse = True)
            for course in courses_sorted:
                if course not in applied_to[candidate]:
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
            if len(applied_to[candidate]) < len(data.courses):
                terminated = False
    # write_to_file(data, current_match, output)

def write_to_file(data, matching, output):
    output_file = open(output, 'w')
    for candidate, preferences in data.candidate_preference.items():
        output_file.write(candidate + ":\n")
        for course, preference in preferences.items():
            output_file.write(' ' + course + '(' + str(preference) + ')')
        output_file.write('\n')
    output_file.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_candidate', type=int)
    parser.add_argument('--num_course', type=int)
    parser.add_argument('--output')
    args = parser.parse_args()

    run_stable_marrige(args.num_candidate, args.num_course, args.output)

main()
