import random
from faker import Faker
from datetime import datetime, timedelta

from data_dev.config import data_generator_config


class DataGenerator:
    """
    A class to generate synthetic data for patients, facilities, and visits.

    Attributes:
        fake (Faker): An instance of the Faker library used to generate fake data.
        num_patients (int): The number of patients to generate, sourced from generator_config.num_patients.
        start_date (str): The start date for the data generation period, sourced from generator_config.start_date.
        end_date (str): The end date for the data generation period, sourced from generator_config.end_date.
        date_format (str): The format of the date strings, sourced from generator_config.date_format.
        visits_per_day (Tuple[int, int]): The range (min, max) of visits per day, sourced from generator_config.visits_per_day.
        facility_types (List[str]): A list of facility types, sourced from generator_config.facility_types.
        patients (List[dict] or None): A list of generated patient data, initialized as None.
        facilities (List[dict] or None): A list of generated facility data, initialized as None.
        visits (List[dict] or None): A list of generated visit data, initialized as None.
    """

    def __init__(self):
        """
        Initializes the DataGenerator class with configuration values and sets up Faker.
        """
        self.fake = Faker()
        self.num_patients = data_generator_config.num_patients
        self.start_date = data_generator_config.start_date
        self.end_date = data_generator_config.end_date
        self.date_format = data_generator_config.date_format
        self.visits_per_day = data_generator_config.visits_per_day
        self.facility_types = data_generator_config.facility_types

        self.patients = None
        self.facilities = None
        self.visits = None

    def generate_patients(self):
        """
        Generates a list of synthetic patient data.

        Returns:
            List[dict]: A list of dictionaries, each representing a patient with attributes:
                - first_name (str): The first name of the patient.
                - last_name (str): The last name of the patient.
                - date_of_birth (str): The date of birth of the patient in the configured date format.
                - address (str): The address of the patient.
        """
        patients = []
        for i in range(0, self.num_patients):
            patients.append({
                "patient_id": i + 1,
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "date_of_birth": self.fake.date_of_birth(minimum_age=18, maximum_age=100).strftime(self.date_format),
                "address": self.fake.address()
            })
        return patients

    def generate_facilities(self):
        """
        Generates a list of synthetic facility data.

        Returns:
            List[dict]: A list of dictionaries, each representing a facility with attributes:
                - facility_name (str): The name of the facility.
                - facility_type (str): The type of the facility (e.g., "Hospital", "Clinic").
                - address (str): The address of the facility.
                - city (str): The city where the facility is located.
                - state (str): The state where the facility is located.
        """
        city = self.fake.city()
        state = self.fake.state()
        facilities = []
        for i in range(0, len(self.facility_types)):
            facilities.append({
                "facility_id": i + 1,
                "facility_name": self.fake.company(),
                "facility_type": self.facility_types[i],
                "address": self.fake.address(),
                "city": city,
                "state": state
            })
        return facilities

    def generate_visits(self):
        """
        Generates a list of synthetic visit data.

        Returns:
            List[dict]: A list of dictionaries, each representing a visit with attributes:
                - patient_id (int): The ID of the patient (randomly assigned).
                - facility_id (int): The ID of the facility (randomly assigned).
                - time_id (str): The date of the visit in the configured date format.
                - visit_reason (str): The reason for the visit (e.g., "Routine Checkup", "Emergency").
                - treatment_cost (float): The cost of the treatment (randomly generated).
                - duration_minutes (int): The duration of the visit in minutes (randomly generated).
        """
        visits = []
        date_list = [(datetime.strptime(self.end_date, self.date_format) - timedelta(days=i)) for i in
                     range((datetime.strptime(self.end_date, self.date_format)
                            - datetime.strptime(self.start_date, self.date_format)).days + 1)]
        for date in date_list:
            num_visits_per_day = random.randint(self.visits_per_day[0], self.visits_per_day[1])
            for _ in range(num_visits_per_day):
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                visit_timestamp = datetime(
                    year=date.year,
                    month=date.month,
                    day=date.day,
                    hour=random_hour,
                    minute=random_minute,
                    second=random_second
                )
                visits.append({
                    "patient_id": random.randint(1, self.num_patients),
                    "facility_id": random.randint(1, len(self.facility_types)),
                    "visit_timestamp": visit_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "treatment_cost": round(random.uniform(50, 5000), 2),
                    "duration_minutes": random.randint(15, 60)
                })
        return visits

    def generate_data(self):
        """
        Generates synthetic data for patients, facilities, and visits, and stores them in the class attributes.
        """
        self.patients = self.generate_patients()
        self.facilities = self.generate_facilities()
        self.visits = self.generate_visits()

    def get_visits(self):
        """
        Retrieves the generated visit data.

        Returns:
            List[dict]: A list of visit data dictionaries.
        """
        return self.visits

    def get_facilities(self):
        """
        Retrieves the generated facility data.

        Returns:
            List[dict]: A list of facility data dictionaries.
        """
        return self.facilities

    def get_patients(self):
        """
        Retrieves the generated patient data.

        Returns:
            List[dict]: A list of patient data dictionaries.
        """
        return self.patients
