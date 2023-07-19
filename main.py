from flask import Flask, jsonify, request
import random
from utils_aspireboy001 import *
import json
import cv2
import numpy as np
import datetime
import pyttsx3
import pygame
import speech_recognition as sr
import random

app = Flask(__name__)

class MMSE_Tests:
    @staticmethod
    def process_clock_image():
        time = request.form.get('time')
        uploaded_file = request.files['image']

        total_score = 0.0
        circle_score = 0.0
        digits_score = 0.0
        lines_score = 0.0
        time_match_score = 0.0

        file_array = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_array, cv2.IMREAD_COLOR)
        processed_image = preprocess_image(image)

        number_lists = []
        circle_info = detect_circle(processed_image)
        if circle_info is not None:
            center, radius, circularity = circle_info
            circle_score = circularity

            lines_in_circle = detect_lines_in_circle(image, center)
            if lines_in_circle is not None:
                lines_score = min(1, len(lines_in_circle) * 0.5)
            else:
                lines_score = 0

            numbers = determine_numbers(lines_in_circle)
            number_lists = list(numbers.keys())

        numbers = extract_handwritten_numbers(processed_image)
        digits_score = (min(12, len(numbers))) / 10

        possible_timings = generate_timings(number_lists)

        match = 0
        if len(possible_timings) > 0:
            for i, timing in enumerate(possible_timings):
                pair_num = i + 1
                temp = str(timing[0]) + ":" + str(timing[1])
                match = max(match, calculate_score(time, temp))

        time_match_score = match
        total_score = circle_score + digits_score + lines_score + time_match_score

        response = {
            'total_score': total_score,
            'circle_score': circle_score,
            'digits_score': digits_score,
            'lines_score': lines_score,
            'time_match_score': time_match_score
        }

        json_response = json.dumps(response)

        return json_response, 200, {'Content-Type': 'application/json'}

    @staticmethod
    def generate_random_words():
        data = request.get_json()
        num_words = data['num_words']

        meaningful_words = ['apple', 'cherry', 'banana', 'cat', 'dog', 'elephant', 'flower', 'guitar', 'house',
                            'island', 'jungle']

        random_words = random.sample(meaningful_words, num_words)

        return jsonify({'random_words': random_words})


    @staticmethod
    def get_random_animals():
        animals = [
            {'name': 'elephant', 'image': 'elephant.jpg'},
            {'name': 'lion', 'image': 'lion.jpg'},
            {'name': 'cat', 'image': 'cat.jpg'},
            {'name': 'dog', 'image': 'dog.jpg'},
            {'name': 'tiger', 'image': 'tiger.jpg'},
            {'name': 'horse', 'image': 'horse.jpg'},
        ]

        data = request.get_json()
        num_animals = data['num_animals']

        random_animals = random.sample(animals, num_animals)

        response = []
        for animal in random_animals:
            animal_data = {
                'name': animal['name'],
                'image': f'https://mmse-test-api.onrender.com/static/img/{animal["image"]}'
            }
            response.append(animal_data)

        return jsonify({'animals': response})

    @staticmethod
    def process_animal_guess():
        guesses = request.get_json()  
        correct_guesses = 0

        for guess in guesses:
            actual_animal = guess['actual_animal']
            guessed_animal = guess['guessed_animal']

            if actual_animal.lower() == guessed_animal.lower():
                correct_guesses += 1

        return jsonify({'score': correct_guesses})

    @staticmethod
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

        score = min(5, score)

        return jsonify({'score': score})

    # newly added are below 

    @staticmethod
    def process_orientation_test():
        data = request.get_json()
        score = 0
        user_name = data['name']
        month = data['month']
        day = data['day']
        year = data['year']
        
        month = month.lower()

        current_time = datetime.datetime.now()
        current_month = current_time.strftime("%B").lower()
        current_day = current_time.strftime("%d")
        current_year = current_time.strftime("%Y")

        if current_month == month:
            score+=1 
        if current_day == day:
            score+=1 
        if current_year == year:
            score+=1 

        return jsonify({'score': score})

    @staticmethod
    def process_two_lists():
        data = request.get_json()
        actual_words = data['actual_words']
        user_words = data['user_words']

        actual_answers = list(set([word.lower() for word in actual_words]))
        user_answers = list(set([word.lower() for word in user_words]))

        score = 0
        for i in range(0,len(user_answers)):
            if i >= len(actual_answers):
                break
            if user_answers[i] == actual_answers[i]:
                score += 1

        return jsonify({'score': score})

    @staticmethod
    def no_ifs_ands_buts():
        data = request.get_json()
        phrase = data['phrase']
        score = 0 
        if phrase.lower() == "no ifs ands or buts":
            score += 1
        return jsonify({'score': score})


    # VPA TEST BELOW 
    @staticmethod
    def vpa_play():
        word_pairs = [
            {'first_word': 'apple', 'second_word': 'fruit'},
            {'first_word': 'car', 'second_word': 'vehicle'},
            {'first_word': 'dog', 'second_word': 'animal'},
            {'first_word': 'sun', 'second_word': 'star'},
            {'first_word': 'book', 'second_word': 'read'},
            {'first_word': 'tree', 'second_word': 'plant'},
            {'first_word': 'pen', 'second_word': 'write'},
        ]   
        
        engine = pyttsx3.init()
        pygame.init()
        def create_audio_file(text):
            audio_file = 'output.wav'

            engine.save_to_file(text, audio_file)
            engine.runAndWait()

            return audio_file

        pairs_text = ''
        for pair in word_pairs:
            first_word = pair['first_word']
            second_word = pair['second_word']
            pairs_text += f"{first_word} - {second_word}. "

        text = f"Let's test your knowledge! Listen to each word and provide the corresponding word as the answer. Pairs are: {pairs_text}"
        audio_file_path = create_audio_file(text)
        
        if audio_file_path:
            return jsonify({'audio_file_path': f'https://mmse-test-api.onrender.com/{audio_file_path}'})
        else:
            return jsonify({'message': 'Failed to retrieve audio file path.'})


    @staticmethod
    def get_vpa_text_question():
        word_pairs = [
            {'first_word': 'apple', 'second_word': 'fruit'},
            {'first_word': 'car', 'second_word': 'vehicle'},
            {'first_word': 'dog', 'second_word': 'animal'},
            {'first_word': 'sun', 'second_word': 'star'},
            {'first_word': 'book', 'second_word': 'read'},
            {'first_word': 'tree', 'second_word': 'plant'},
            {'first_word': 'pen', 'second_word': 'write'},
        ]  
        data = request.get_json()
        selected_pairs = random.sample(word_pairs, data['num_questions'])
        return jsonify({'selected_pairs': selected_pairs})

    @staticmethod
    def vpa_test():
        data = request.get_json()
        user_responses = [response.lower() for response in data['user_responses']]
        filtered_responses = [pair['second_word'].lower() for pair in data['original_responses']]

        score = 0 

        for i in range(0,len(user_responses)) :
            if i >= len(filtered_responses) :
                break
            if filtered_responses[i] == user_responses[i]:
                score+=1 

        return jsonify({'score':score})


app.add_url_rule('/process_clock_image', view_func=MMSE_Tests.process_clock_image, methods=['POST'])
app.add_url_rule('/random-words', view_func=MMSE_Tests.generate_random_words, methods=['POST'])
app.add_url_rule('/random-animals', view_func=MMSE_Tests.get_random_animals, methods=['POST'])
app.add_url_rule('/animal-guess', view_func=MMSE_Tests.process_animal_guess, methods=['POST'])
app.add_url_rule('/subtraction-test', view_func=MMSE_Tests.process_subtraction_test, methods=['POST'])
app.add_url_rule('/orientation_test', view_func=MMSE_Tests.process_orientation_test, methods=['POST'])
app.add_url_rule('/score-of-two-list', view_func=MMSE_Tests.process_two_lists, methods=['POST'])
app.add_url_rule('/no-ifs-ands-buts', view_func=MMSE_Tests.no_ifs_ands_buts, methods=['POST'])

app.add_url_rule('/get-vpa-audio', view_func=MMSE_Tests.vpa_play, methods=['POST'])
app.add_url_rule('/get-vpa-text-question', view_func=MMSE_Tests.get_vpa_text_question, methods=['POST'])
app.add_url_rule('/vpa_test', view_func=MMSE_Tests.vpa_test, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True,port = 80)
