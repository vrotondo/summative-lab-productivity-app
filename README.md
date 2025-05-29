# summative-lab-productivity-app

Summative Lab: Full Auth Flask Backend- Productivity App
In this lab, you’ll build a secure Flask API backend from scratch. You’ll implement authentication using either JWT or session-based methods and create a single resource that is owned by a user, such as a Notes app, a Workout log, or a Mood tracker.

The frontend will be provided (in two versions: JWT and Session), and includes a complete authentication flow. You will not build any frontend code, but your backend must support future integration with the provided frontend for all resource endpoints.

Scenario

Your company’s frontend team is building a productivity tool for users to track personal data. You’re the backend engineer responsible for implementing:

Full authentication
A user-owned resource (e.g., notes, journal entries, workouts, expenses, tasks)
CRUD endpoints and pagination
Secure access controls so users cannot view or edit each other’s data
The frontend team has completed user registration and login, but they're waiting on your API before implementing the main feature screens.

By completing this lab, you will:

Design a secure RESTful Flask API using either JWT or session-based authentication.
Build the designed Flask API from scratch.
Implement full CRUD operations for a user-specific resource.
Restrict access to ensure users can only view or manipulate their own records.
Integrate pagination into resource index routes.
Follow best practices for project structure, documentation, and database seeding.
Tools and Resources
Python 3.8.13+
Text Editor or IDE (e.g., VS Code)
Git + GitHub
Pipenv: The following Python packages (for your Pipfile):
flask = "2.2.2"
flask-sqlalchemy = "3.0.3"
Werkzeug = "2.2.2"
marshmallow = "3.20.1"
faker = "15.3.2"
flask-migrate = "4.0.0"
flask-restful = "0.3.9"
importlib-metadata = "6.0.0"
importlib-resources = "5.10.0"
pytest = "7.2.0"
flask-bcrypt = "1.0.1"
(Optional, only if using JWT) flask-jwt-extended
GitHub Repo: Summative Lab with Client AppsLinks to an external site.
You can fork and clone this and add your Flask API directly to the repo, or you can just download one of the folders to test your authentication routes. Be sure to choose the correct sessions or JWT client based on which auth method you choose to implement.
Instructions
Task 1: Define the Problem
You must build a secure API that supports:

User authentication using either JWT or sessions
A resource of your choosing (e.g., journal entries, workouts, expenses) that belongs to a user
All CRUD actions (Create, Read, Update, Delete) for the chosen resource
Pagination on the resource index endpoint
Route protection so users can only access their own data.
This app will be similar to a workout tracking or notes app you may have on your phone. Other users should not be able to see, update, create, or delete my notes (or whichever resource you choose) and vice versa.
Task 2: Determine the Design
Choose your auth method: Either session or JWT (use one of the frontend templates provided).

Models
User model: Implement registration, login, and secure password handling.

Chosen resource model: Should include at least id, 2+ other fields (like title and content), and a foreign key to user_id.

CRUD Endpoints
GET /<resource> – paginated
POST /<resource>
PATCH /<resource>/<id>
DELETE /<resource>/<id>
Auth
Full Authentication and Authorization endpoints should be built out.
Passwords should be protected and securely hashed in the database.
Only authenticated users can access resource endpoints.
Users cannot access or modify other users' records.
Task 3: Develop the Code
You must:

Scaffold your project structure (app.py, models.py, seed.py, etc.).
Create and apply database migrations with Flask-Migrate.
Build RESTful routes using Flask-RESTful or Flask views.
Use Flask-Bcrypt for password hashing.
Use sessions or JWT for auth endpoints.
Optionally, you can develop the frontend further by adding components and pages for your resources, but you will only be graded on your backend Flask API.

Task 4: Test, Debug, and Refine Application
Test your application auth flow using Postman and/or the given frontend repo, depending on whether you choose JWT or sessions.

Ensure that routes return appropriate HTTP status codes and error messages
Confirm that unauthorized users cannot access data
Optionally, you could build a test suite for automated testing, but testing is not a graded portion of this lab.

Task 5: Document and Maintain
Step 1: Add Necessary Comments, Remove Unnecessary comments

Include explanatory comments and/or docstrings on any unclear code.
Remove unnecessary, outdated, or unclear code comments.
Step 2: Create README with Required Information

Create a README.md with:
Project title
Project Description
Installation instructions (i.e. pipenv install, migrating and seeding the database, etc)
Run instructions (i.e. flask run or python app.py)
List with descriptions of all endpoints the API has
Step 3: Final Commit and Push Git History

Ensure all code is pushed to GitHub and on the main branch.
  Important 

Before you submit your solution, you need to save your progress with git.

Add your changes to the staging area by executing git add .
Create a commit by executing git commit -m "Your commit message"
Push your commits to GitHub by executing git push origin main or git push origin master , depending on the name of your branch (use git branch to check on which branch you are).
Submission and Grading Criteria
Review the rubric below as a guide for how this lab will be graded.
Complete your assignment using your preferred IDE.
When you are ready, push your final script to a public GitHub. Your public GitHub repository should include:
Full flask application, with all necessary files and code.
A functioning seed.py file to create example data for all models.
A README.md with the following:
Project title
Project Description
Installation instructions (i.e. pipenv install, migrating and seeding the database, etc)
Run instructions (i.e. flask run)
List with descriptions of all endpoints the API has
Pipfile with dependencie
Test files, if applicable
To submit your assignment, click on Start Assignment then share the link to your GitHub repo below. 
