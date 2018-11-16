import random
import argparse

class trial_data:
    def __init__(self):
        self.candidates = set()
        self.courses = set()
        self.candidate_preference = dict()
        self.course_preference = dict()
        self.qualification = dict()
        self.course_capacity = dict()

def generate(num_candidate, num_course):
    data = trial_data()
    for i in range(num_candidate):
        data.candidates.add('candidate' + str(i))
        data.candidate_preference['candidate' + str(i)] = dict()
    for i in range(num_course):
        data.courses.add('course' + str(i))
        data.course_preference['course' + str(i)] = dict()
        data.course_capacity['course' + str(i)] = random.choice([1, 2, 3, 4, 5])
    for candidate in data.candidates:
        for course in data.courses:
            data.candidate_preference[candidate][course] = round(random.uniform(0, 1), 1)
            data.course_preference[course][candidate] = round(random.uniform(0, 1), 1)
    for candidate in data.candidates:
        data.qualification[candidate] = dict()
        for course in data.courses:
            data.qualification[candidate][course] = random.choice([0, 1])
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_candidate', type=int)
    parser.add_argument('--num_course', type=int)
    args = parser.parse_args()

    trial_data = generate(args.num_candidate, args.num_course)
