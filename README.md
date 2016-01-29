#### Labour Today API####
  
This is a Python Django application that serves as the API for the Labour Today database, containing information on workers, contractors and jobs.
  The main structure are as follows: <br> <br>
  **urls.py** - Defines the URI routes for each resource in the REST API <br>
  **models.py** - The schema for the database expressed as models from Django's ORM <br>
  **views.py** - Receives and processes the requests and returns a response to the client. URIs from urls.py map to classes and functions in views.py <br>
  **serializers.py** - Handles conversion between formats when receiving and returning data as well as checking the validity of request data.
