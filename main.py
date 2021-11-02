# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, session, redirect, request, flash, url_for
from db.models import db, Event, Booking, User, Comment, Category
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm
import calendar


# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# create db tables if not already
with app.app_context():
    db.create_all()

# import declared routes
import user


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(500)
def page_not_found(e):
    return render_template("server-error.html")


# helper function, True if user logged in, False otherwise
def authenticated():
    if session.get('logged_in'):
        return True
    return False

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')  # ‘/’ URL is bound with index() function.
def index():
    # fetch all events from database
    events_ = Event.query.order_by(Event.id.desc()).all()

    # fetch categories and pass to view
    categories = Category.query.all()

    # fetch recent 3 comments to display on the landing page
    comments = Comment.query.order_by(Comment.id.desc()).limit(3).all()

    # check if user wants a events of a specific category
    category_id = request.args.get("category")

    # check if user wants to search events
    query = request.args.get("query") or ""

    if category_id:
        events_ = Event.query.filter_by(category_id=category_id).all()

    if query:
        events_ = Event.query.filter(Event.title.like('%' + query + '%')).all()
    # pass events to view
    return render_template('index.html', events=events_, categories=categories, comments=comments, category_id=category_id, query_str=query)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # redirect if user already logged in
    if session.get('logged_in'):
        return redirect("/")

    # Creating Login form object
    form = LoginForm(request.form)
    # verifying that method is post and form is valid
    if request.method == 'POST' and form.validate():
        # checking that user exists or not
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            print("Here")
            # if user exist in database than we will compare our database hashed password
            # and password come from login form
            if check_password_hash(user.password, form.password.data):
                # if password is matched, allow user to access and save email and username inside the session
                flash('You have successfully logged in.', "success")

                session['logged_in'] = True

                session['email'] = user.email

                session['username'] = user.username

                session['user_id'] = user.id
                print(session['username'])
                # After successful login, redirecting to home page
                return redirect('/')

            else:

                # if password is in correct , redirect to login page
                flash('Username or Password Incorrect', "Danger")
                print("Invalid username or password")
                return redirect('/login/')

    # rendering login page
    return render_template('login.html', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    # redirect if user already logged in
    if session.get('logged_in'):
        return redirect("/")

    # Creating RegistrationForm class object
    form = RegisterForm(request.form)

    # Checking that method is post and form is valid or not.
    if request.method == 'POST' and form.validate():

        # if all is fine, generate hashed password
        hashed_password = generate_password_hash(form.password.data, method='sha256')

        # create new user model object
        new_user = User(

            name=form.name.data,

            username=form.username.data,

            email=form.email.data,

            password=hashed_password)

        # saving user object into data base with hashed password
        db.session.add(new_user)

        db.session.commit()

        flash('You have successfully registered', 'success')

        # if registration successful, then redirecting to login Api
        return redirect(url_for('login'))

    else:

        # if method is Get, than render registration form
        return render_template('register.html', form=form)


@app.route('/logout/')
def logout():
    # Removing data from session by setting logged_flag to False.
    session['logged_in'] = False
    session['username'] = None
    session['email'] = None
    # redirecting to home page
    return redirect(url_for('index'))


# upcoming events
@app.route('/events')
def events():
    # fetch all events from database
    events = Event.query.order_by(Event.id.desc()).all()
    return render_template('events.html', events=events)


# my events
@app.route("/my-events")
def my_events():
    # authenticate
    if not session.get("logged_in"):
        return redirect("/login/")

    user_id = session.get("user_id")
    events = Event.query.filter_by(user_id=user_id) \
        .order_by(Event.id.desc()) \
        .all()
    return render_template('my-events.html', events=events)


# for event details and booking an event
@app.route('/book/<event_id>', methods=["POST", "GET"])
def book(event_id):
    # fetch event details
    event = Event.query.filter_by(id=event_id).first()
    comments = Comment.query.filter_by(event_id=event_id).order_by(Comment.id.desc()).all()

    # calculate available tickets
    total_tickets = event.total_tickets
    total_purchased_tickets = Booking.query.with_entities(func.sum(Booking.quantity).label('sum')).filter_by(
        event_id=event_id).first()[0]

    if total_purchased_tickets is None:
        total_purchased_tickets = 0

    available_tickets = total_tickets - total_purchased_tickets

    # check whether current user has already booked this event
    already_booked = False
    if session.get('logged_in'):
        user_id = session.get('user_id')
        already_booked = Booking.query.filter_by(event_id=event_id, user_id=user_id).count() > 0

    # check whether booking form is submitted
    if request.method == "POST":

        # authenticate user
        if not session.get("logged_in"):
            return redirect("/login")

        user_id = session.get('user_id')
        # get form data and put in bookings
        quantity = request.form.get("quantity")

        if int(quantity) <= available_tickets:
            booking = Booking(user_id=user_id, event_id=event_id, quantity=quantity)

            db.session.add(booking)
            db.session.commit()

            return redirect("/my-bookings")

        else:
            flash(f"There are not enough tickets available. Only {available_tickets} tickets left.")
            return redirect(f"/book/{event_id}")
        # take user to success page

    return render_template("book-event.html",
                           event=event, comments=comments,
                           available_tickets=available_tickets,
                           already_booked=already_booked)


#
@app.route('/my-bookings')
def list_bookings():
    # authenticate
    if not session.get("logged_in"):
        return redirect("/login")

    user_id = session.get("user_id")

    # fetch bookings
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.id.desc()).all()

    # pass bookings to view
    return render_template('user-booking-history.html', bookings=bookings)


# create a new event
@app.route('/create-event', methods=["POST", "GET"])
def create_event():
    categories = Category.query.all()

    # check whether form has been submitted
    if request.method == "POST":
        # get submitted data
        user_id = session.get("user_id")
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        banner = request.form.get("banner")
        location = request.form.get("location")
        date_time = datetime.fromisoformat(request.form.get("datetime"))
        total_tickets = request.form.get("total_tickets")
        category = request.form.get("category")
        price = request.form.get("price")

        new_event = Event(user_id=user_id,
                          title=title,
                          description=description,
                          status=status,
                          image_link=banner,
                          location=location,
                          date_time=date_time,
                          total_tickets=total_tickets,
                          category_id=category,
                          price=price

                          )

        # validate submitted data
        # validate inputs
        errors = []
        if not title:
            errors.append("Please provide a title.")
        if not description:
            errors.append("Please provide a description")

        if not status:
            errors.append("Please provide a status")

        if not banner:
            errors.append("Please provide a banner link")

        if not price:
            errors.append("Please provide a price")

        if not location:
            errors.append("Please provide a location")

        if not price:
            errors.append("Please provide a price")

        if not total_tickets:
            errors.append("Please provide a total tickets")

        if len(errors) > 0:
            return render_template("event-creation", event=new_event, errors=errors, categories=categories)

        db.session.add(new_event)
        db.session.commit()
        return redirect("/my-events")

    return render_template('event-creation.html', categories=categories)


# update an event
@app.route('/update-event/<event_id>', methods=["GET", "POST"])
def update_event(event_id):
    # get event and categories from database
    event = Event.query.filter_by(id=event_id).first()
    categories = Category.query.all()

    # authenticate and authorize
    if not authenticated():
        return redirect("/login")

    # get the event
    event = Event.query.filter_by(id=event_id).first()

    # make sure the event is created by current logged in user
    if event.user_id != session.get("user_id"):
        return redirect("/login")

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        banner = request.form.get("banner")
        location = request.form.get("location")
        category = request.form.get("category")
        price = request.form.get("price")

        date_time = datetime.fromisoformat(request.form.get("datetime"))
        total_tickets = request.form.get("total_tickets")

        # validate inputs
        errors = []
        if not title:
            errors.append("Please provide a title.")
        if not description:
            errors.append("Please provide a description")

        if not status:
            errors.append("Please provide a status")

        if not banner:
            errors.append("Please provide a banner link")

        if not price:
            errors.append("Please provide a price")

        if not location:
            errors.append("Please provide a location")

        if not price:
            errors.append("Please provide a price")

        if not total_tickets:
            errors.append("Please provide a total tickets")

        if len(errors) > 0:
            return render_template("event-creation", event=event, errors=errors, categories=categories)

        # update event
        event.title = title
        event.description = description
        event.status = status
        event.image_link = banner
        event.location = location
        event.total_tickets = total_tickets
        event.category_id = category
        event.date_time = date_time
        event.price = price

        db.session.commit()

        return redirect("/my-events")

    return render_template("event-creation.html", event=event, categories=categories)


# post a comment
@app.route('/add-comment/<event_id>', methods=["POST"])
def add_comment(event_id):
    user_id = session.get("user_id")
    comment = request.form.get("comment")

    comment = Comment(event_id=event_id, user_id=user_id, comment=comment)
    db.session.add(comment)
    db.session.commit()

    return redirect("/book/" + event_id)


# delete some event
@app.route('/delete-event/<event_id>')
def delete_event(event_id):
    # authenticate
    if not authenticated():
        return redirect("/login/")

    # authorize
    user_id = session.get("user_id")
    event = Event.query.filter_by(id=event_id).first()

    if event.user_id == user_id:
        # delete event on authorization success
        Event.query.filter_by(id=event_id).delete()
        db.session.commit()

        return redirect("/my-events")

    return redirect("/login/")


@app.template_filter('month_name')
def month_name(month_number):
    return calendar.month_abbr[month_number]

@app.template_filter('str_date')
def str_date(datetime_obj):
    # Thu Oct 28 2021 at 07:00 PM
    # %a %b %-d %Y at %I:%M %p
    return datetime_obj.strftime("%a %b %d %Y at %I:%M %p")




# main driver function
if __name__ == '__main__':
    app.run(debug=True)



