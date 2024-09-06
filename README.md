# Fitness Friends Challenge

Welcome to the **Fitness Friends Challenge**, our intuitive and dynamic web application designed to help users monitor and achieve their health and fitness goals, create challenges with a group of friends and have e healthy competition along the way. Built with Django (initially forked from https://github.com/iferco/django-health-tracker), this responsive application offers a seamless experience for tracking daily fitness activities, dietary habits (to be reitroduced later), and weight progress.

## Features

- **Activity Log**:  Log and track various physical activities with details such as duration, intensity, calories burned, and Training Stress Score (TSS).
- **Dietary Tracker**: Monitor daily food and water intake, including comprehensive nutritional information (this feature is currently commented out but can be enabled as needed).
- **Weight Tracker**: Record and visualize weight changes over time with dynamic charts.
- **Fitness Goals**: Set, monitor, and achieve fitness goals, whether it's weight loss, muscle gain, or maintaining a healthy lifestyle.
- **Challenges and Leaderboards**:  Create and participate in group challenges, view leaderboard rankings, and track progress towards challenge goals.
- **Responsive Design**: Access the tracker easily on any device, perfect for updates and checks on the go.
- **User Authentication**: Secure user registration and login, ensuring data privacy and security.

## Technologies

- **Backend**: Python and Django for robust and scalable application structure.
- **Frontend**: HTML, CSS, and JavaScript for a user-friendly interface.
- **Data Visualization**: Chart.js for rendering interactive and informative graphs.
- **Database**: SQLite for development, with easy scalability to PostgreSQL or other databases for production.

## Getting Started

1. **Clone the Repository**:

``` git clone git@github.com:aguirreSL/fitnessFriendsChallenge.git``` 

```or```

``` git clone https://github.com/aguirreSL/fitnessFriendsChallenge.git``` 

2. **Navigate to the project directory**:
```
cd fitnessFriendsChallenge
```

3. **Set Up a Virtual Environment**:
``` 
python -m venv env
source env/bin/activate # On Windows use env\Scripts\activate
``` 

4. **Install Dependencies**:
``` 
pip install -r requirements.txt

``` 

5. **Initialize the Database**:
``` 
python manage.py makemigrations
python manage.py migrate
``` 

6. **Create a superuser (optional but recommended for admin access)**:
```
python manage.py createsuperuser
```

7. **Run the Server**:
``` 
python manage.py runserver
``` 

