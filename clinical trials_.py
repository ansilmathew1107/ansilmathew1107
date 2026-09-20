import requests
import csv
from collections import defaultdict

def fetch_all_trials():
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "fields": "nct_id,has_results",
        "size": 1000
    }
    all_trials = []
    offset = 0
    while True:
        params["offset"] = offset
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            studies = data.get("studies", [])
            if not studies:
                break
            all_trials.extend(studies)
            offset += 1000
        except requests.exceptions.RequestException as e:
            print("Error fetching trial data:", e)
            break
    return all_trials

def fetch_participant_data(trial_id):
    url = f"https://clinicaltrials.gov/api/v2/studies/{trial_id}/participants"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("participants", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching participants for trial {trial_id}:", e)
        return []

def calculate_distribution(participant_data, key):
    distribution = defaultdict(int)
    total_count = 0

    for participant in participant_data:
        value = participant.get(key, "Unknown")
        distribution[value] += 1
        total_count += 1

    percentages = {k: (v / total_count) * 100 for k, v in distribution.items()}
    return percentages

def save_to_csv(filename, total_trials=None, trials_with_results=None, race_percentages=None, age_percentages=None, gender_percentages=None):
    age_groups = ["1-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100", "100+"]
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Total Trials and Trials with Results
        if total_trials is not None and trials_with_results is not None:
            writer.writerow(["Total Trials", total_trials])
            writer.writerow(["Trials with Results", trials_with_results])
        else:
            writer.writerow(["Total Trials", "Error fetching data"])
            writer.writerow(["Trials with Results", "Error fetching data"])

        # Empty buffer rows
        writer.writerow([])  
        writer.writerow([])  
        writer.writerow([])  

        # Race distribution
        writer.writerow(["Race", "Percentage"])
        if race_percentages is not None:
            for race, percentage in race_percentages.items():
                writer.writerow([race, f"{percentage:.2f}%"])
        else:
            writer.writerow(["Error fetching race data"])

        # Empty buffer rows
        writer.writerow([])  
        writer.writerow([])  
        writer.writerow([])  

        # Age distribution
        writer.writerow(["Age", "Percentage"])
        if age_percentages is not None:
            for age_group in age_groups:
                percentage = age_percentages.get(age_group, 0)
                writer.writerow([age_group, f"{percentage:.2f}%"])
        else:
            writer.writerow(["Error fetching age data"])

        # Empty buffer rows
        writer.writerow([])  
        writer.writerow([])  
        writer.writerow([])  

        # Gender distribution
        writer.writerow(["Gender", "Percentage"])
        if gender_percentages is not None:
            for gender, percentage in gender_percentages.items():
                writer.writerow([gender, f"{percentage:.2f}%"])
        else:
            writer.writerow(["Error fetching gender data"])

if __name__ == "__main__":
    try:
        all_trials = fetch_all_trials()
        if all_trials:
            total_trials = len(all_trials)
            trials_with_results = sum(1 for trial in all_trials if trial.get("has_results", False))
        else:
            total_trials = None
            trials_with_results = None
    except Exception as e:
        total_trials = None
        trials_with_results = None
        print(f"Error fetching total trials or trials with results: {e}")

    participant_data = []
    try:
        if all_trials:
            for trial in all_trials:
                if trial.get("has_results", False):
                    participants = fetch_participant_data(trial.get("nct_id", ""))
                    participant_data.extend(participants)
    except Exception as e:
        print(f"Error fetching participant data: {e}")

    try:
        race_percentages = calculate_distribution(participant_data, "race")
    except Exception as e:
        race_percentages = None
        print(f"Error calculating race distribution: {e}")

    try:
        age_percentages = calculate_distribution(participant_data, "age")
    except Exception as e:
        age_percentages = None
        print(f"Error calculating age distribution: {e}")

    try:
        gender_percentages = calculate_distribution(participant_data, "sex")
    except Exception as e:
        gender_percentages = None
        print(f"Error calculating gender distribution: {e}")

    save_to_csv("clinical_trials_statistics.csv", total_trials, trials_with_results, race_percentages, age_percentages, gender_percentages)
