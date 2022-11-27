# Website 
This is a project about biodiversity. 
This application will help the user to identify different species of incest based on image and sound input. Using a simple and intuitive interface, the user can easily navigate and interact with the website.
##HTML
This website is based on HTML and CSS programming languages. The HTML part is used to create the structure of the website as for the majority of the styling in the pages. CSS is also used as complementary for styling a few elements among the website pages. 
##Project structure
The project files are stored inside a folder with the name flask. Inside the flask folder we stored the flask_01.py file. Also, there are 2 other folders named template and static. Inside the template folder the html files are stored and inside static all the css files are stored. We use this folder structure in order to link flask with our project’s files using the python script.
##Python
To link the HTML files with flask we used python programming language. We created a function for every page using the modules from flaks library.
In each function we link the buttons of the page and the redirect page after the user clicks a particular option. 

## Functions *connection(query, getResult)*, *Encrypt(password)* and *check_password(password, email)*
### *connection(query, getResult)* explained 
Regarding the relation between the flask python file and the database in SQL server, Jason prepared the function *connection* using pyodbc to simplify each line of code where these connections are needed for the queries in SQL. This function takes two parameters: **query** and **getResult**. In the first parameter we put the query that need to be executed in SQL server and the second parameter is put to **True** or **False** based on what kind of result we want. When selecting data and storing these in a variable in the python code, we set this **getResult** variable to **True**. When we only want to insert or update data in the database we set this parameter to **False** because we are not getting any result to use in our code, we only make changes to the database in SQL. 
### *Encrypt(password)* explained
When storing passwords of clients into the database, we had to make sure that these passwords are encrypted for privacy and security purposes. This is done with the help of the function Encrypt. Every time a new account it created or a password is updated, the encrypted version of this password will be saved to the database. [source](https://www.youtube.com/watch?v=CSHx6eCkmv0)
### *check_password(password, email)* explained
When logging in, the script should check whether the combination email and password match. To do this, this function first converts the inserted password to bytes with the *bytes()* function. After this, the encrypted password from the database is selected with the help of the *connection* function from the customer table where **email** is equal to the **inserted email**. This encrypted (hashed) password found in the database will first be converted to bytes, also with *bytes()*. With *bcrypt.checkpw(p, p1)* the **inserted password** and **hashed password** from the database will be decrypted and compared. If the passwords match, this *check_password(password, email)* will return **True**, else **False**. 

## Sign in page
When signing in, python first checks in SQL whether there exists a customer with this email address. Because this value (email) returns a list like this [[email@gm.com]], it is sufficient to check the length of this value. If there is no such email address, this list will be empty. So the length of this list will be 0. In this case there will pop up a message that says 'This email address does not exist'. If this email address exists, the length will be 1 because it would have one list in it which contains a string of the email address like shown above. After checking for *len(check_email)>0*, python checks whether the inserted password and email address match with the help of *check_password(password, email)*. If this returns **True**, a session for this email address is created and the user is redirected to their home page. If the password does **not** match with the email address, there pops up a message that says ‘Inserted wrong password'. Besides signing in, the user can also choose the options 'forgot password' and 'create new account'.

## Index12/userHome page:
In the index page the user finds four buttons on the top left corner and two buttons on top right corner, in order to interact with the application. In the end of the page the user can see the contact details of the institution that this project takes place. 
When users press on log out, the current session is cleared with *session.clear()*


## Contact page:
In this page it is not needed to go through every feedback button to check which one the client chose. In the key **‘rating’** from *request.form* the button that has been clicked after pressing submit will be stored. So setting **feedback_score** to **request.form[‘rating’]** is enough. Before taking any action, it is necessary to check whether there is anyone logged in so we can store the *feedback* with the *id* of this person’s *account*. To check whether there are any active sessions we check *for ‘email’ in session*. If this statement is **True**, the variable **email** is set to the **email of the current session**. This email address is then used to find the **customer id** of the client in the customer table where email equals the email of the currently active email address. In order to find the **account id**, SQL searches for the **id** in the table account where the customer id is equal to the one found before. Finally, a new row is added in the feedback table in SQL and the client will be redirected to the home page of their account with a flash/update message saying 'Thank you, your feedback is successfully submitted.'
When people try to give feedback without being logged in (so in the else statement of *if ‘email’ in session*) they will be redirected to the login page and get a flash/warning message on the screen that says 'You are not logged in. Login or create account to give feedback.'

## Create account page

It is the same for gender as for the feedback buttons. The button selected by the client will be stored in **request.form[‘gender’]**, so it is enough to set the variable **gender** equal to this. First the inserted password and repeated password are being compared, if these are not the same there will pop a message that says that these two do not match. If they do match and the password is encrypted and stored in the variable **encrypted_pw**, python will first check in SQL whether there is already an email address that exists in the database. This is done with select in SQL through the function connection. If there is such email, a list of the row corresponding to this email address will be stored in the variable *email_already_exists*. If there is no such email address in the database, this variable will be empty thus will return False. After checking *if not email_already_exists* this new account will be created in the database. The client’s customer information is stored in the customer table with the help of insert. Customer id is generated automatically. To access the customer id that is just generated, python stores the customer table in a variable(= **get_id**) and accesses the most recent customer id with *get_id[-1][0]*. With [-1] the last added row is accessed and [0] selects the first value which is the id, so the customer id when using it in other tables. This accessed customer id will then be inserted in the table account id to be able to join the customer table with the account table when needed. After successfully creating the account, the client will be redirected to the login page and will see a flash message that tells them their account is created and that they can login. 
In case the inserted email address already exists, the client will be redirected to the login page and will see this message pop up: 'An account with this email address already exists.'

## Forgot page
In case anyone tries to access the forgot page while logged in (for example, by typing /forgot after the link), python will first check whether there is an active session with if ‘email’ in session. If this is the case they will be redirected to their home page and a message will pop up that says they are already logged in. The next elif statement will check whether the inserted email address exists in the database, if it does not the user will see a message that says that the email address does not exist and stay on the forgot page. 
If the email address exists and the two inserted passwords match, the row in the customer table in SQL for this email address will be updated with the new encrypted password. If the two inserted passwords do not match, a message will pop up giving the user this information. 

## Settings page
First python will check if there is not an active session with *if not ‘email’ in session*. In case nobody is logged in, it will return the user to the login page and flash this message: 'You are not logged in yet. Login to access your settings.' After that, it will check whether there is an active session and whether this matches with the inserted current password. In this if statement, python will then check whether the two inserted new passwords match. If they do, the customer table will be updated in SQL with the new encrypted password. The user will be redirected to their homepage and see a message that confirms the update. If their two inserted passwords do not match, the session’s email address and inserted email address do not match or the current password does not match with the email address they will get messages on the same settings page.

## Flash messages in pages
In the html files, for the pages create_account, forgot_password, index12, login and settings, an extra block of code was needed to be able to show the messages in *flash()* used in python. This block of code is only used when the function *flash()*  is called:
```python
{% block content %}
<div class="container">
    {% for message in get_flashed_messages() %}
    <div class="alert alert-warning">
        <button type="button" class="close" data-dismiss="alert">&times;</button>
        {{ message }}
     </div>
     {% endfor %}

     {% block page_content %}{% endblock %}
</div>
{% endblock %}
```
