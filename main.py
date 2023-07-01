from flask import Flask, jsonify, request
import random
from utils import *
import json
import cv2
import numpy as np

app = Flask(__name__)

# Hand-Drawn-clock 
@app.route('/process_clock_image', methods=['POST'])
def process_clock_image():
    
    time = request.form.get('time')
    uploaded_file  = request.files['image']

    score = 0.0 

    #step1 
    file_array = np.frombuffer(uploaded_file.read(), np.uint8)
    # Decode the numpy array into an image
    image = cv2.imdecode(file_array, cv2.IMREAD_COLOR)
    processed_image = preprocess_image(image)

    #step2
    circle_info = detect_circle(processed_image)
    if circle_info is not None:
        center, radius, circularity = circle_info
        score += circularity
    else:
        # Set default values
        height, width = processed_image.shape[:2]
        center = (width // 2, height // 2)
        radius = height // 2
        circularity = 0
    print("score after circle:",score)
    #step3
    numbers = extract_handwritten_numbers(processed_image)
    score += (min(12,len(numbers)))/10 

    print("score after digits:",score)

    #step4
    lines_in_circle = detect_lines_in_circle(processed_image, center, radius)
    score += min(2,len(lines_in_circle)*0.5 )
    print("score after lines:",score)

    #step5
    numbers = determine_numbers(lines_in_circle)
    number_lists = list(numbers.keys())  # Convert dictionary keys to a list
    #step6
    possible_timings = generate_timings(number_lists)
    print(possible_timings)
    match = 0 
    if len(possible_timings) > 0:
        for i, timing in enumerate(possible_timings):
            pair_num = i + 1
            temp = str(timing[0]) + ":" + str(timing[1]) 
            match = max(match,calculate_score(time,temp))
    
    score += match 
    print("score after match:",score)

    response = {'score': score}

    json_response = json.dumps(response)

    return json_response, 200, {'Content-Type': 'application/json'} 



# Verbal Recall Test
@app.route('/random-words', methods=['POST'])
def generate_random_words():
    data = request.get_json()
    num_words = data['num_words']

    meaningful_words = ['apple', 'cherry' ,'banana', 'cat', 'dog', 'elephant', 'flower', 'guitar', 'house', 'island', 'jungle']

    random_words = random.sample(meaningful_words, num_words)

    return jsonify({'random_words': random_words})


@app.route('/calculate-score', methods=['POST'])
def calculate_score_of_two_lists():
    data = request.get_json()
    actual_words = data['actual_words']
    user_words = data['user_words']

    actual_answers = list(set(actual_words))
    user_answers = list(set(user_words))

    score = 0
    for answer in actual_words:
        if answer in user_words:
            score += 1

    return jsonify({'score': score})




# Animal Naming Test 
@app.route('/random-animals', methods=['POST'])
def get_random_animals():
    animals = [
        {'name': 'Elephant', 'image': 'elephant.jpg'},
        {'name': 'Lion', 'image': 'lion.jpg'},
    ]

    data = request.get_json()
    num_animals = data['num_animals']

    random_animals = random.sample(animals, num_animals)

    response = []
    for animal in random_animals:
        animal_data = {
            'name': animal['name'],
            'image': f'static/img/{animal["image"]}'
        }
        response.append(animal_data)

    return jsonify({'animals': response})


@app.route('/animal-guess', methods=['POST'])
def process_animal_guess():
    data = request.get_json()
    user_guess = data['guessed_animal']
    actual = data['actual_animal']
    score = 0 
    if actual.lower() == user_guess.lower():
        score += 1 
    
    return jsonify({'score': score})



# Substraction Test :
@app.route('/subtraction-test', methods=['POST'])
def process_subtraction_test():
    data = request.get_json()
    starting_number = data['starting_number']
    difference = data['difference']
    user_answer = data['user_answers']

    score = 0
    previous = starting_number

    for num in user_answer:
        expected = previous - difference
        if num == expected:
            score += 1
        previous = num

    score = min(5,score)

    return jsonify({'score': score})




if __name__ == '__main__':
    app.run(debug=True)