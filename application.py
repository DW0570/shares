from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from time import gmtime, strftime
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import and_, or_, not_
from helpers import apology, login_required, lookup, usd
from flask_sqlalchemy import SQLAlchemy
# Configure application
app = Flask(__name__)
#export postgres://qcsgsjppdtlzir:4c726872a180d217f5babd320fb748d98590dc6789080a1f3f0bd5a12ff0de25@ec2-3-89-0-52.compute-1.amazonaws.com:5432/d2q0teadlv8g8e

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Session(app)
db = SQLAlchemy(app)
engine = create_engine(os.getenv("DATABASE_URL"))
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

#if not os.getenv("API_KEY"):
    #raise RuntimeError("API_KEY not set")

db.init_app(app)


class Userr(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    cash = db.Column(db.Float, nullable=False)
    def __init__(self, username, hash, cash):
        self.username = username
        self.hash = hash
        self.cash = cash

#symbol, price, shares, total
class Summm(db.Model):
    __tablename__ = "summs"
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    symbol = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    def __init__(self, userId, symbol, price, shares, total):
        self.userId = userId
        self.symbol = symbol
        self.price = price
        self.shares = shares
        self.total = total

#userId, symbol, shares, price, time
class Portfolioo(db.Model):
    __tablename__ = "portfolios"
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    symbol = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    def __init__(self, userId, symbol, price, shares, time):
        self.userId = userId
        self.symbol = symbol
        self.price = price
        self.shares = shares
        self.time = time

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        name = request.form.get("username")
        pwd = request.form.get("password")
        # Ensure username and password was submitted
        if not name or not pwd:
            return apology("must provide username and password", 403)
            #return apology("用户名或秘密不能为空", 403)
        # Query database for username
        count = Userr.query.filter_by(username=name).count()
        row = Userr.query.filter_by(username=name).first()
        #row = Userr.query.filter_by(hash=generate_password_hash(pwd)).first()
        #rows = db.execute("SELECT * FROM users WHERE username = :username",
                          #username=request.form.get("username"))

        # Ensure username exists and password is correct
        if count != 1 or not row:
            return apology("invalid username and/or password", 403)
            #return apology("用户名或秘密错误", 403)
        if not check_password_hash(row.hash, pwd):
            return apology("invalid username and/or password", 403)
            #return apology("用户名或秘密错误", 403)
        # Remember which user has logged in
        user_idd = session["user_id"] = row.id
        # Redirect user to home page
        #return redirect('/')
        return redirect(url_for('index'))
        #return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/pwd", methods=["GET", "POST"])
@login_required
def pwd():
    # user try to change the password
    if request.method=="POST":
        # user must provide the old and new password as well as to confirm the new password
        pwd_0 = request.form.get("old_pwd")
        pwd = request.form.get("password")
        conf = request.form.get("confirmation")
        if not pwd_0 or not pwd or not conf:
            return apology("provide old and new password and confirm new password" ,403)
            #return apology("请重新设置秘密" ,403)
        user = Userr.query.get(session.get("user_id"))

        # compare password
        #for row in rows:
            #hashh = row["hash"]
        if not check_password_hash(user.hash, pwd_0):
            return apology("incorrect password" ,403)
            #return apology("秘密错误" ,403)
        # confirm password
        elif pwd != conf:
            return apology("passwords don't match" ,403)
            #return apology("请再次确认" ,403)
        # everything is ready then update the password
        #db.execute("UPDATE users SET hash = :hah", hah=generate_password_hash(pwd))
        #user = Userr.query.all()
        #for user in users:
        user.hash = generate_password_hash(pwd)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template("pwd.html")


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    # user try to add some additional cash
    if request.method == "POST":
        cash = int(request.form.get("cash"))
        if not cash or cash < 0:
            return apology("please provide a positive number!" ,403)
            #return apology("请输入自然数!" ,403)
        #db.execute("UPDATE users SET cash = cash + :ca WHERE id = :id", ca=cash, id=session.get("user_id"))
        user = Userr.query.get(session.get("user_id"))
        user.cash = user.cash + cash
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template("add_cash.html")


# implement a route that could alow user to change their password and add some additional cash
@app.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    if request.method == "POST":
        setting = request.form.get("setting")
        if not setting:
            return apology("chose what you want to set please!" ,403)
            #return apology("请先选择设置!" ,403)
        # switch which way the user want to take either "password" or "cash" and send them the right route to continue the setting
        elif setting == "password":
            return redirect(url_for('pwd'))
        elif setting == "cash":
            return redirect(url_for('add_cash'))
    else:
        return render_template("setting.html")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # select cash and transaction of detail that we want to show to users
    amount = 0
    total = 0
    user = Userr.query.get(session.get("user_id"))
    #user = Userr.query.get(12)
    cash = user.cash
    rows = Summm.query.filter_by(userId=user.id).all()
    #cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session.get("user_id"))
    #rows = db.execute("SELECT symbol, price, shares, total FROM summ WHERE userId = :id", id=session.get("user_id"))
    portfolios = Portfolioo.query.all()
    if len(rows) == 0 and len(portfolios) == 0:
        cash = 10000
        amount = cash + total
        return render_template("index.html", rows=rows, cash=cash, total=amount, usd=usd)
    elif len(rows) > 0 :
        for row in rows:
            # change the price to current price
            row.price = lookup(row.symbol)["price"]
            row.total = row.price * row.shares
            # obtain "total" by adding the total of each row iterately
            total = total + row.total
        amount = cash + total
    return render_template("index.html", rows=rows, cash=cash, total=amount, usd=usd)
        #else:
            #amount = cash
            #return render_template("index.html", cash=cash, total=amount, usd=usd)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symb = request.form.get("symbol")
        if not symb:
            return apology("provide symbol please!" ,403)
        symbo = lookup(symb)
        if not symbo:
            return apology("invalid symbol!" ,403)
        price = symbo["price"]
        symbol = symbo["symbol"]
        share = request.form.get("shares")
        if not share:
            return apology("missing shares" ,403)
        n = 0
        for c in share:
            if c.isdigit():
                n = n + 1
        if n == len(share):
            shares = int(share)
            cost = price * shares
            row = Userr.query.get(session.get("user_id"))
            # check if the user could afford the exchange
            if row.cash < cost:
                return apology("sorry, couldn't afford it!" ,403)
            else:
                # reduce cash from user and add stock to the user's portfolio
                row.cash = row.cash - cost
                db.session.commit()
                # get the date and time when the transaction occurs
                # select the row in sql table(summ) where the stock belong to the current user and the symbol is get symbol("symbol")
                item = Summm.query.filter(and_(Summm.userId==row.id, Summm.symbol==symbol)).first()
                # if that row dosen't exist then add it to table("summ")
                if not item :
                    price = symbo["price"]
                    summ = Summm(userId=row.id, symbol=symbol, shares=shares, price=price, total=price*shares)
                    db.session.add(summ)
                    db.session.commit()
                    # if the row exists then just update "shares" and "total" in that row
                elif item != None:
                    price = symbo["price"]
                    item.shares = item.shares + shares
                    item.total = item.shares * price
                    db.session.commit()
                time = strftime("%Y-%m-%d  %H:%M:%S ", gmtime())
                # add stock to user's portfolio
                portfolio = Portfolioo(userId=row.id, symbol=symbol, shares=share, price=price, time=time)
                db.session.add(portfolio)
                db.session.commit()

            return redirect(url_for('index'))
        else:
            return apology("positive integer only" ,403)
            #return apology("请输入正整数" ,403)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # select all we want show to the user from table "portfolio"
    rows = Portfolioo.query.filter_by(userId=session.get("user_id")).all()
    #rows = db.execute("SELECT symbol, shares, price, time FROM portfolio WHERE userId = :id",
                        #id=session.get("user_id"))

    return render_template("history.html", rows=rows, usd=usd)




@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # store whatever symbol the user typed in in "symbol"
        symbol = request.form.get("symbol")
        # check did the user fill the blank
        if not symbol:
            return apology("missing symbol!" ,403)
            #return apology("请输入代码!" ,403)
        # check whether the symbol is valid of not, if it's not valid do an apology,else send them the "quoted.html" page(which show them the current price of that symbol)
        quote = lookup(symbol)
        if not quote:
            return apology("invalid symbol!" ,403)
            #return apology("代码有误!" ,403)
        return render_template("quoted.html", quote=quote, usd=usd)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        n = 0
        # get whatever the user typed in
        name = request.form.get("username")
        pwd = request.form.get("password")
        cof = request.form.get("confirmation")
        # make sure the user filled each blank
        if not name or not pwd or not cof:
            return apology("Missing name or password!" ,403)
            #return apology("用户名或秘密不能为空!" ,403)
        # make sure the user confirmed the password
        elif pwd != cof:
            return apology("password isn't matched!" ,403)
            #return apology("确认有误!" ,403)
        users = Userr.query.all()
        for user in users:
            if user.username == name:
                n = n + 1
        if n > 0:
            return apology("Sorry the user name already exists!" ,403)
        # hash password
        hash_pwd = generate_password_hash(pwd)
        # try to insert user's name and hashed password into "users"(which is a sql table)
                            #username=name, hash=hash_pwd)
        user = Userr(username=name, hash=hash_pwd, cash=10000)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        # check if the username has already existed, if existed then do an apology
        # the user has been registered then send he or she the "index.html" page
        return redirect(url_for('index'))
        # if the method is "GET",then show them the "register.html"
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # get the symbol,and shares user typed in
        symb = request.form.get("symbol")
        # check if the user filled the blank or not
        if not symb:
            return apology("provide symbol please!")
        # check the symbol via lookup() function
        symbo = lookup(symb)
        if not symbo:
            return apology("can't sell" ,403)
        # get the price and symbol of the stock
        price = symbo["price"]
        symbol = symbo["symbol"]
        companyName = symbo["name"]
        share = request.form.get("shares")
        if not share:
            return apology("missing shares" ,403)
        n = 0
        for c in share:
            if c.isdigit():
                n = n + 1
        if n == len(share):
            shares = int(share)
            # get the amount of money from the transaction
            # record the date and time when the transaction occurs
            time = strftime("%Y-%m-%d  %H:%M:%S ", gmtime())
            # select the row that the user has that contains the "symbol" via "GET"
            item = Summm.query.filter(and_(Summm.userId==session.get("user_id"), Summm.symbol==symbol)).first()
            if not item:
                return apology("nothing to sell" ,403)
            elif shares > item.shares:
                return apology(" can't sell such a number of stocks!" ,403)
            else :
                price = symbo["price"]
                income = shares * price
                user = Userr.query.get(item.userId)
                user.cash = user.cash + income
                db.session.commit()
                # insert the transaction into the user's portfolio
                portfolio = Portfolioo(symbol=symbol, shares=-shares, price=price, time=time, userId=item.userId)
                db.session.add(portfolio)
                db.session.commit()
                if shares < item.shares:
                    price = symbo["price"]
                    #income = price * shares
                    summ = Summm.query.filter(and_(Summm.symbol==symbol, Summm.userId==session.get("user_id"))).first()
                    summ.shares = summ.shares - shares
                    summ.total = summ.shares * price
                    db.session.commit()
                elif shares == item.shares :
                    summ = Summm.query.filter(and_(Summm.userId==session.get("user_id"), Summm.symbol==symbol)).first()
                    #for sum in summ:
                    db.session.delete(item)
                    db.session.commit()
                return redirect(url_for('index'))
        else:
            return apology("positive integer only" ,403)
    else:
        rows = Summm.query.filter_by(userId=session.get("user_id")).all()
        if len(rows) < 1:
            return apology("nothing to sell" ,403)
        else:
            return render_template("sell.html", rows=rows)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
