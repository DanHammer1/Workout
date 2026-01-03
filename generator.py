import json
from collections import defaultdict
import random
import numpy as np

optimal_workout_time = 1800
skill_factor = 0.4 # 0 - Newborn Baby, 1 - Anime type shit.
sd = 5
weight_adj_factor = 0.03
optimal_exercise_count = 10
fun_numbers = [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 
               50, 60, 75, 100, 120, 150, 180, 210, 
               240, 300, 420, 500, 600, 750, 1000, 1200, 
               1500, 1800]

noise_magnitude = 0.3
min_run_length = 2
max_run_length = 15
workout_intensity_conversion_factor = 3/100 # Intensity of denominator is numerator km extra.

fastest_run_pace = 270 - int(70 * skill_factor)
slowest_run_pace = 300

class Timer:
    def __init__(self, seconds=0, minutes=0, hours=0):
        self.seconds = seconds
        self.minutes = minutes
        self.hours = hours

        self.normalise()

    def normalise(self):
        self.hours += self.seconds // 3600
        self.seconds %= 3600
        
        self.hours += self.minutes // 60
        self.minutes %= 60

        self.minutes += self.seconds // 60
        self.seconds %= 60
    
    def printable(self):
        print_statement = ""
        multiple_non_zero = False

        if self.hours != 0:
            print_statement += f"{self.hours} Hours" + "s" * (self.hours != 1)
            multiple_non_zero = True
        if self.minutes != 0:
            print_statement += ", " * multiple_non_zero + f"{self.minutes} Minute" + "s" * (self.minutes != 1)
            multiple_non_zero = True
        if self.seconds != 0:
            print_statement += ", " * multiple_non_zero + f"{self.seconds} Second" + "s" * (self.seconds != 1)

        return print_statement

    def sum_seconds(self):
        return 3600 * self.hours + 60 * self.minutes + self.seconds

class Exercise:
    def __init__(self, difficulty, category, type="Default", muscles=[], 
                 display="", optimal_reps=1, optimal_rep_time=Timer(), symetrical=True):
        
        self.difficulty = difficulty
        self.category = category
        self.type = type
        self.muscles = muscles
        self.display_name = display
        self.optimal_reps = optimal_reps
        self.optimal_rep_time = optimal_rep_time
        self.symetrical = symetrical

    def copy(self):
        return Exercise(self.difficulty, self.category, self.type, self.muscles, 
            self.display_name, self.optimal_reps, self.optimal_rep_time, self.symetrical)


def generate_weighting_dict(exercises):
    muscle_weights = defaultdict(int)
    exercise_weights = defaultdict(int)
    category_weights = defaultdict(int)

    muscle_list = []
    for exercise in exercises:
        for muscle in exercise.muscles:
            if muscle not in muscle_list:
                muscle_list.append(muscle)
    
    muscle_count = len(muscle_list)
    for muscle in muscle_list:
        muscle_weights[muscle] = 1 / muscle_count

    for exercise in exercises:
        exercise_weights[exercise] = 1 / len(exercises)
        if exercise.category not in category_weights:
            category_weights[exercise.category] = 1
    
    for category in category_weights:
        category_weights[category] = 1 / len(category_weights)
    
    return muscle_weights, exercise_weights, category_weights





def adjust_weighting(weights, list, factor=weight_adj_factor):
    for item in list:
        weight_loss = min(weights[item], factor)
        weights[item] -= weight_loss

        for alt_item in weights.keys():
            if alt_item != item:
                weights[alt_item] += (weight_loss / (len(weights) - 1))





def convert_number(number, num_list):
    num_to_round = 0
    lowest_dist = -1
    for num in num_list:
        dist = num - number
        if abs(dist) < abs(lowest_dist) or dist + lowest_dist == 0 or num_to_round == 0:
            lowest_dist = dist
            num_to_round = num

    return num_to_round




def choose_muscle(muscle_weights):
    l_bound = 0
    u_bound = 0
    r_val = random.random()

    for muscle, weight in muscle_weights.items():
        u_bound += weight
        if l_bound <= r_val <= u_bound:
            return muscle
        l_bound += weight




def choose_category(exercises, category_weights):
    l_bound = 0
    u_bound = 0
    r_val = random.random()

    weight_sum = 0
    processed_categories = []
    
    for exercise in exercises:
        if exercise.category in category_weights.keys() and \
            exercise.category not in processed_categories:

            processed_categories.append(exercise.category)
            weight_sum += category_weights[exercise.category]
    
    if weight_sum != 0:
        weight_ratio = 1 / weight_sum
    else:
        raise AssertionError

    for category in processed_categories:
        u_bound += category_weights[category] * weight_ratio
        if l_bound <= r_val <= u_bound:
            return category

        l_bound += category_weights[category] * weight_ratio





def choose_exercise(exercises, exercise_weights, category_weights):
    l_bound = 0
    u_bound = 0
    r_val = random.random()

    category = choose_category(exercises, category_weights)
    valid_exercises = []

    for exercise in exercises:
        if exercise.category == category:
            valid_exercises.append(exercise)

    weight_sum = 0
    for exercise, weight in exercise_weights.items():
        if exercise in valid_exercises:
            weight_sum += weight
    
    if weight_sum != 0:
        weight_ratio = 1 / weight_sum
    else:
        raise AssertionError

    
    for exercise, weight in exercise_weights.items():
        if exercise in valid_exercises:
            u_bound += weight * weight_ratio
            if l_bound <= r_val <= u_bound:
                return exercise

            l_bound += weight * weight_ratio






def select_exercise(optimal_difficulty, muscle, exercises, 
                    muscle_weights, exercise_weights, category_weights):
    
    valid_exercises = []
    for exercise in exercises:
        if muscle in exercise.muscles:
            valid_exercises.append(exercise)
    
    
    wanted_difficulty = np.random.normal(loc=optimal_difficulty, scale=sd)

    exercise_candidates = []
    for exercise in valid_exercises:
        distance = abs(exercise.difficulty - wanted_difficulty)
        exercise_candidates.append((exercise, distance))

    exercise_candidates = sorted(exercise_candidates, key=lambda x: x[1])

    i = 0    

    while True:
        exercises_to_choose = []
        
        if i < len(exercise_candidates):
            distance = exercise_candidates[i][1]
        else:
            print(i)
            exit()

        for exercise, alt_distance in exercise_candidates[i:]:
            if distance != alt_distance:
                break
            i += 1
            exercises_to_choose.append(exercise)
        try:
            exercise = choose_exercise(exercises_to_choose, exercise_weights, category_weights)
            break
        except Exception as e:
            print(e)
            pass
            
    chosen_exercise = exercise.copy()

    adjust_weighting(exercise_weights, [exercise], 0.025)
    adjust_weighting(muscle_weights, chosen_exercise.muscles)

    if chosen_exercise.category != "Special":
        adjust_weighting(category_weights, [chosen_exercise.category], 1)

    #for exercise, weight in exercise_weights.items():
    #    print(exercise.display_name, weight)

    difficulty_difference = optimal_difficulty - chosen_exercise.difficulty
    std_diff = difficulty_difference / sd

    wanted_rep_time = chosen_exercise.optimal_rep_time
    wanted_rep_count = chosen_exercise.optimal_reps

    noise = random.uniform(-noise_magnitude, noise_magnitude)
    if chosen_exercise.optimal_reps <= 3:
        wanted_rep_time = int((chosen_exercise.optimal_rep_time * 
            max(0.1, (1 + noise + std_diff * 0.1))) ** (1 + std_diff * 0.03))
        wanted_rep_time = convert_number(wanted_rep_time, fun_numbers)
    if chosen_exercise.optimal_reps >= 3:
        wanted_rep_count = int((chosen_exercise.optimal_reps * 
            max(0.1, (1 + noise + std_diff * 0.1))) ** (1 + std_diff * 0.03))
        wanted_rep_count = convert_number(wanted_rep_count, fun_numbers)
    return chosen_exercise, wanted_rep_count, wanted_rep_time





def add_exercise(workout, weighting, e_weighting, exercises, optimal_difficulty, category_weights):
    chosen_muscle = choose_muscle(weighting)
    
    chosen_exercise, reps, rep_time = select_exercise(optimal_difficulty, 
            chosen_muscle, exercises, weighting, e_weighting, category_weights)
    
    chosen_exercise.optimal_reps = reps
    chosen_exercise.optimal_rep_time = Timer(seconds=rep_time)

    workout.append((chosen_exercise))





def add_break(workout, time):
    break_to_add = Exercise(0, None, None, [], "Break", 1, Timer(seconds=time))
    workout.append(break_to_add)





def generate_workout(muscle_weights, exercise_weights, exercise_list, optimal_difficulty, exercise_count, category_weights):
    workout = []
    workout_time = 0

    for i in range(exercise_count):
        add_exercise(workout, muscle_weights, exercise_weights, exercise_list, optimal_difficulty, category_weights)
        
        workout_time += workout[i].optimal_reps * workout[i].optimal_rep_time.sum_seconds() * 1.5 + 60

        if (i + 1) % 5 == 0 and i + 2 < exercise_count and 300 < optimal_workout_time - workout_time:
            add_break(workout, 300)
            workout_time += 300
        if workout_time > optimal_workout_time:
            break
    
    generate_run(workout, optimal_difficulty, exercise_count)
    
    return workout





def print_workout(workout):
    print("Workout Consists Of:\n")
    for exercise in workout:
        if exercise.category == "Run":
            print(f"\nRun {max(min_run_length, exercise.length)}km in {exercise.time.printable()}")
        else:
            if exercise.optimal_reps > 1:
                print(f"{exercise.display_name} x{exercise.optimal_reps}" + 
                    (1 - exercise.symetrical) * " For each limb", 
                    f"({exercise.optimal_rep_time.printable()} each)")
            else:
                print("\n" * (exercise.difficulty == 0) + 
                      f"{exercise.display_name} ({exercise.optimal_rep_time.printable()})", 
                    (1 - exercise.symetrical) * "For each limb" + "\n" * (exercise.difficulty == 0))

    exercise_counts = defaultdict(int)
    for exercise in workout:
        for muscle in exercise.muscles:
            exercise_counts[muscle] += 1

    #print(exercise_counts.items())

    print("\nEnd of Workout!!!\n")





def calculate_intensity(workout, optimal_difficulty):
    intensity_score = 0
    for exercise in workout:
        diff_dist = exercise.difficulty - optimal_difficulty

        intensity_score += diff_dist
    
    return intensity_score




def round_run_distance(run):
    if run.length % 1 >= 0.5:
        run.length = int(run.length) + 1
    else:
        run.length = int(run.length)




def generate_run(workout, optimal_difficulty, exercise_count):
    intensity = calculate_intensity(workout, optimal_difficulty)
    normalised_intensity = intensity * 10 / exercise_count

    default_run_length = (max_run_length - min_run_length) * skill_factor
    optimal_run_length = default_run_length - normalised_intensity * workout_intensity_conversion_factor

    run_difficulty = (optimal_run_length-min_run_length)/(max_run_length-min_run_length)
    run_exercise = Exercise(difficulty=run_difficulty, category="Run", muscles=["Upper Leg"],
                            display="Run", optimal_reps=1, optimal_rep_time=Timer(seconds=0))
    
    pace = random.randint(fastest_run_pace, slowest_run_pace)
    print(Timer(seconds=pace).printable())
    multiplier = (fastest_run_pace - pace) / (fastest_run_pace - slowest_run_pace)
    print(multiplier, fastest_run_pace, slowest_run_pace, pace)
    optimal_run_length -= min_run_length
    optimal_run_length *= multiplier
    optimal_run_length += min_run_length

    run_exercise.length = optimal_run_length

    round_run_distance(run_exercise)

    run_exercise.time = Timer(seconds=(pace * run_exercise.length))
    run_exercise.time.seconds = 0
    
    workout.append(run_exercise)




def extract_json_info(file):
    data = json.load(open(file, "r"))["Data"]
    max_difficulty = data['Max Difficulty']

    exercises = data['Exercises']
    exercise_list = []
    for category in exercises:
        for variation in category['Variations']:
            new_exercise = Exercise(variation['Difficulty'], 
                                    category['Category'], 
                                    variation['Type'], 
                                    variation['Muscles'], 
                                    variation['Display Name'],
                                    variation['Optimal Rep Count'],
                                    variation['Optimal Rep Time'],
                                    variation['Symetrical Limb Targeting'])

            exercise_list.append(new_exercise)

    return exercise_list, max_difficulty




def main():

    exercise_list, max_difficulty = extract_json_info("exercises.json")
    optimal_difficulty = skill_factor * max_difficulty

    muscle_weights, exercise_weights, category_weights = generate_weighting_dict(exercise_list)

    workout = generate_workout(muscle_weights, exercise_weights, exercise_list, 
        optimal_difficulty, optimal_exercise_count, category_weights)
    
    print_workout(workout)




if __name__ == "__main__":
    main()