from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.form
    name = data.get('name')
    gender = int(data.get('gender'))
    personal = int(data.get('personal_gender'))
   
    class_names = [] #list of names (strings)
    class_sizes = []
    class_availability = []

    for key, value in data.items():
        if key.startswith('class-name-'):
            class_names.append(value)
        elif key.startswith('class-size-'):
            class_sizes.append(int(value))
        elif key.startswith('class-availability-'):
            class_availability.append(int(value))

    df_baby_names = pd.read_csv("babyNamesUSYOB-full.csv")

    class_look_up = {
    1: [2003, 2004],
    2: [2002, 2003],
    3: [2001, 2002],
    4: [2000, 2001],
    5: [2002, 2003, 2004],
    6: [2000, 2001, 2002],
    7: [2000, 2001, 2002, 2003, 2004]
    }

    probabilities_per_class = []
    for i in range(len(class_names)):

        #determine the probability a baby with your name was born in particular years (male, female, or both)
        years_to_be_considered = class_look_up[class_availability[i]]
        df_babies_filtered_year = df_baby_names[df_baby_names["YearOfBirth"].isin(years_to_be_considered)]
        total_babies = []
        total_babies.append(df_babies_filtered_year[df_babies_filtered_year["Sex"] == "M"]["Number"].sum())
        total_babies.append(df_babies_filtered_year[df_babies_filtered_year["Sex"] == "F"]["Number"].sum())

        if personal == 1:
            total_babies[0] = total_babies[0] - 1
        else:
            total_babies[1] = total_babies[1] - 1

        df_babies_filtered_name = df_baby_names[(df_baby_names["Name"] == name) & (df_baby_names["YearOfBirth"].isin(years_to_be_considered))]
        babies_with_name = []
       
        if gender == 1:
            babies_with_name.append(df_babies_filtered_name[df_babies_filtered_name["Sex"] == "M"]["Number"].sum())
            babies_with_name.append(0)
            if personal == 1 and babies_with_name[0] > 0:
                babies_with_name[0] = babies_with_name[0] - 1
        elif gender == 2:
            babies_with_name.append(0)
            babies_with_name.append(df_babies_filtered_name[df_babies_filtered_name["Sex"] == "F"]["Number"].sum())
            if personal == 2 and babies_with_name[1] > 0:
                babies_with_name[1] - babies_with_name[1] - 1
        else:
            babies_with_name.append(df_babies_filtered_name[df_babies_filtered_name["Sex"] == "M"]["Number"].sum())
            babies_with_name.append(df_babies_filtered_name[df_babies_filtered_name["Sex"] == "F"]["Number"].sum())
            if personal == 1 and babies_with_name[0] > 0:
                babies_with_name[0] = babies_with_name[0] - 1
            elif personal == 2 and babies_with_name[1] > 0:
                babies_with_name[1] = babies_with_name[1] - 1


        probability_of_name = []
        if total_babies[0] != 0:
            probability_of_name.append(np.nan_to_num(float(babies_with_name[0] / total_babies[0])))
        else:
            probability_of_name.append(0)
        
        if total_babies[1] != 0:
            probability_of_name.append(np.nan_to_num(float(babies_with_name[1] / total_babies[1])))
        else:
            probability_of_name.append(0)


        #determine gender distribution based off of class answer
        current_class = class_names[i].lower()
        subject_percentages = [.480, .520]
        if current_class.startswith('cs'):
            subject_percentages = [.662, .338]
        elif current_class.startswith('humbio'):
            subject_percentages = [.173, .827]
        elif current_class.startswith('engr'):
            subject_percentages = [.522, .478]   
        elif current_class.startswith('econ'):
            subject_percentages = [.537, .463]
        elif current_class.startswith('symsys') or current_class.startswith('phil') or current_class.startswith('psych'):
            subject_percentages = [.448, .557]
        elif current_class.startswith('sts'):
            subject_percentages = [.349, .651]
        elif current_class.startswith('bio'):
            subject_percentages = [.443, .557]
        elif current_class.startswith('polisci'):
            subject_percentages = [.492, .508]
        elif current_class.startswith('math'):
            subject_percentages = [.759, .241]


        expected_students_gender = []
        expected_students_gender.append(round(subject_percentages[0] * class_sizes[i]))
        expected_students_gender.append(round(subject_percentages[1] * class_sizes[i]))

        probability_not_males = 1 - probability_of_name[0]
        probability_not_females = 1 - probability_of_name[1]
        
        probability_of_class = 1 - ((probability_not_males ** expected_students_gender[0]) * (probability_not_females ** expected_students_gender[1]))
        probabilities_per_class.append(probability_of_class)

    probabilities_of_not = []
    for i in range(len(probabilities_per_class)):
        probabilities_of_not.append(1 - probabilities_per_class[i])

    probability_across_classes = 1 - np.prod(probabilities_of_not)

    probability_not = round((probability_across_classes) * 100, 4)

    response = {
        'probability': probability_not
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run()
