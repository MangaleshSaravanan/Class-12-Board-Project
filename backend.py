import mysql.connector
from mysql.connector import connect
from random import randint, choices
from datetime import datetime
from decimal import Decimal, InvalidOperation
import string

myConn = None
myCur = None

def start():
    global myConn, myCur
    while True:
        password = input("Enter your MySQL password: ")

        try:
            myConn = connect(host="127.0.0.1",user="root",passwd=password)
            myCur = myConn.cursor()
            myCur.execute("CREATE DATABASE IF NOT EXISTS __mangalesh__")
            myCur.execute("USE __mangalesh__")
            break

        except mysql.connector.Error as err:
            if err.errno == 1045:
                print("Incorrect password. Access denied.\n")
            else:
                print(f"Database Connection Error: {err}\n")

    customer_table = """
        customer_id VARCHAR(30) PRIMARY KEY,
        account_number VARCHAR(30) UNIQUE NOT NULL,
        password VARCHAR(20) NOT NULL,
        name VARCHAR(100) NOT NULL,
        dob DATE NOT NULL,
        nationality VARCHAR(50),
        phnum VARCHAR(20),
        email VARCHAR(100) UNIQUE,
        passport VARCHAR(50),
        visa_status VARCHAR(50),
        address TEXT,
        tax_id VARCHAR(50),
        tax_residency VARCHAR(100),
        occupation VARCHAR(100),
        source_of_funds VARCHAR(255),
        account_purpose VARCHAR(255),
        account_status VARCHAR(10),
        balance DECIMAL(20,2) CHECK(balance >= 0)
    """

    transaction_table = """
        transaction_id VARCHAR(30) PRIMARY KEY,
        customer_id VARCHAR(30) NOT NULL,
        transaction_type VARCHAR(30) NOT NULL,
        amount DECIMAL(20,2) NOT NULL CHECK(amount > 0),
        sender_account VARCHAR(30),
        receiver_account VARCHAR(30),
        transaction_date DATETIME NOT NULL,
        status VARCHAR(20) NOT NULL,
        fees DECIMAL(15,2),
        tax_amount DECIMAL(15,2),
        FOREIGN KEY(customer_id)
        REFERENCES __bankCustomers__(customer_id)
    """

    try:
        myCur.execute(f"CREATE TABLE IF NOT EXISTS __bankCustomers__ ({customer_table})" )
        myCur.execute(f"CREATE TABLE IF NOT EXISTS __bankTransactions__ ({transaction_table})")
        myConn.commit()

    except mysql.connector.Error as err:
        print(f"Error creating tables: {err}")

def createCustomerId():
    try:
        myCur.execute("SELECT customer_id FROM __bankCustomers__")
        existing_ids = [row[0] for row in myCur.fetchall()]
        while True:
            customer_id = ("BOP-CUS-" +"".join(choices(string.ascii_uppercase + string.digits,k=12)))

            if customer_id not in existing_ids:
                return customer_id

    except mysql.connector.Error as err:
        print(f"Error generating Customer ID: {err}")
        return None


def createAccountNumber():
    try:
        myCur.execute("SELECT account_number FROM __bankCustomers__")
        existing_accounts = [row[0] for row in myCur.fetchall()]
        while True:
            account_number = str(randint(10 ** 15 + 1, 10 ** 16 - 1))
            if account_number not in existing_accounts:
                return account_number

    except mysql.connector.Error as err:
        print(f"Error generating Account Number: {err}")
        return None

def createTransactionId():
    try:
        myCur.execute("SELECT transaction_id FROM __bankTransactions__")
        existing_ids = [row[0] for row in myCur.fetchall()]
        while True:
            transaction_id = ("BOP-TXID-" +"".join(choices(string.ascii_uppercase + string.digits,k=21)))
            if transaction_id not in existing_ids:
                return transaction_id

    except mysql.connector.Error as err:
        print(f"Error generating Transaction ID: {err}")
        return None

def createAccount(password,name,dob,nationality,phnum,email,passport,
    visa_status,address,tax_id,tax_residency,occupation,source_of_funds,account_purpose):

    customer_id = createCustomerId()
    account_number = createAccountNumber()

    if customer_id is None or account_number is None:
        return
    status = "ACTIVE"
    try:
        query = """INSERT INTO __bankCustomers__VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,0)"""

        values = (customer_id,account_number,password,name,dob,nationality,phnum,email,
                  passport,visa_status,address,tax_id,tax_residency,occupation,source_of_funds,account_purpose,status)

        myCur.execute(query, values)
        myConn.commit()

        print("\nAccount created successfully.")
        print(f"Customer ID   : {customer_id}")
        print(f"Account Number: {account_number}")

    except mysql.connector.Error as err:
        myConn.rollback()
        print(f"Unable to create account.\nReason: {err}")

def addMoney(acn, pwd, money):
    try:
        amount = Decimal(str(money))

    except (ValueError, InvalidOperation):
        print("Invalid deposit amount format.")
        return

    transaction_id = createTransactionId()

    try:
        myCur.execute("SELECT customer_id FROM __bankCustomers__ WHERE account_number=%s",(acn,))
        result = myCur.fetchone()
        if result is None:
            print("Invalid account number")
            return

        customer_id = result[0]
        myCur.execute("""UPDATE __bankCustomers__SET balance = balance + %sWHERE account_number=%sAND password=%s""",(amount, acn, pwd))

        if myCur.rowcount == 0:
            print("Invalid account number or password")
            status = "FAILED"
        else:
            print("Deposit successful")
            status = "SUCCESSFUL"

        myCur.execute("""INSERT INTO __bankTransactions__ VALUES(%s,%s,'deposit',%s,%s,NULL,%s,%s,0,0)""",
            (transaction_id,customer_id,amount,acn,datetime.now(),status))
        myConn.commit()

    except mysql.connector.Error as err:
        myConn.rollback()
        print(f"Database error during deposit: {err}")

def withdrawMoney(acn, pwd, money):
    try:
        amount = Decimal(str(money))

    except (ValueError, InvalidOperation):
        print("Invalid withdrawal amount format.")
        return

    transaction_id = createTransactionId()
    fee = amount * Decimal("0.01")
    tax = fee * Decimal("0.18")
    total_amount = round(amount + fee + tax, 2)

    try:
        myCur.execute("""SELECT customer_id FROM __bankCustomers__ WHERE account_number=%s""",(acn,))
        customer = myCur.fetchone()
        myCur.execute("""SELECT balance FROM __bankCustomers__ WHERE account_number=%s AND password=%s""",(acn, pwd))
        balance = myCur.fetchone()

        if customer is None or balance is None:
            print("Invalid account number or password")
            return

        if total_amount <= balance[0]:

            myCur.execute( """UPDATE __bankCustomers__ SET balance = balance - %s WHERE account_number=%s
                AND password=%s""",(total_amount, acn, pwd))

            print("Withdrawal Successful")
            status = "SUCCESSFUL"

        else:
            print("Insufficient Funds")
            status = "FAILED"

        myCur.execute("""INSERT INTO __bankTransactions__ VALUES(%s,%s,'withdrawal',%s,%s,NULL,%s,%s,%s,%s)""",
            (transaction_id,customer[0],amount,acn,datetime.now(),status,float(fee),float(tax)))
        myConn.commit()

    except mysql.connector.Error as err:
        myConn.rollback()
        print(f"Database error during withdrawal: {err}")

def transferMoney(acn, pwd, racn, money):
    if acn == racn:
        print("Self transfer not possible")
        return

    try:
        amount = Decimal(str(money))

    except (ValueError, InvalidOperation):
        print("Invalid transfer amount format.")
        return

    transaction_id = createTransactionId()
    try:
        myCur.execute("""SELECT customer_id FROM __bankCustomers__ WHERE account_number=%s """,(acn,))
        customer = myCur.fetchone()
        myCur.execute("""SELECT balance FROM __bankCustomers__ WHERE account_number=%s AND password=%s""",(acn, pwd))
        balance = myCur.fetchone()

        if customer is None or balance is None:
            print("Invalid account number or password")
            return

        myCur.execute("""SELECT account_number FROM __bankCustomers__ WHERE account_number=%s""",(racn,))
        receiver = myCur.fetchone()
        
        if receiver is None:
            print("Invalid Receiver Account")
            myCur.execute("""INSERT INTO __bankTransactions__ VALUES(%s,%s,'transfer',%s,%s,%s,%s,%s,0,0)""",
                (transaction_id,customer[0],amount,acn,racn,datetime.now(),"FAILED"))
            myConn.commit()
            return

        fee = amount * Decimal("0.01")
        tax = fee * Decimal("0.18")
        total_amount = round(amount + fee + tax, 2)

        if total_amount <= balance[0]:
            myCur.execute("""UPDATE __bankCustomers__ SET balance = balance - %s WHERE account_number=%s
                AND password=%s""",(total_amount, acn, pwd))
            myCur.execute("""UPDATE __bankCustomers__ SET balance = balance + %s WHERE account_number=%s""",(amount, racn))
            print("Transfer Successful")
            status = "SUCCESSFUL"

        else:
            print("Insufficient Funds")
            status = "FAILED"

        myCur.execute("""INSERT INTO __bankTransactions__ VALUES(%s,%s,'transfer',%s,%s,%s,%s,%s,%s,%s)""",
            (transaction_id,customer[0],amount,acn,racn,datetime.now(),status,float(fee),float(tax)))
        myConn.commit()

    except mysql.connector.Error as err:
        myConn.rollback()
        print(f"Database error during transfer: {err}")

def displayDetails(cusId, accNum, passWd):
    try:
        query = """SELECT * FROM __bankCustomers__ WHERE customer_id=%s AND account_number=%s AND password=%s"""
        values = (cusId, accNum, passWd)
        myCur.execute(query, values)
        records = myCur.fetchall()

        if records:
            for record in records:
                print(record)
        else:
            print("No matching customer found.")

    except mysql.connector.Error as err:
        print(f"Unable to retrieve customer details.\nReason: {err}")

def getBalance(acn, pwd):
    try:
        myCur.execute("""SELECT balance FROM __bankCustomers__ WHERE account_number=%s AND password=%s""",(acn, pwd))
        balance = myCur.fetchone()

        if balance is None:
            print("Invalid account number or password.")
            return
        print(f"Current Balance : ${balance[0]}")

    except mysql.connector.Error as err:
        print(f"Unable to retrieve balance.\nReason: {err}")

def getTransactions(acn, pwd):
    headings = ("Transaction ID","Customer ID","Type","Amount","Sender","Receiver","Date & Time","Status","Fees","Tax")
    print(headings)
    print("-" * 150)

    try:
        myCur.execute("""SELECT password FROM __bankCustomers__ WHERE account_number=%s""",(acn,))
        row = myCur.fetchone()

        if row is None:
            print("Invalid account number.")
            return

        if pwd != row[0]:
            print("Invalid password.")
            return

        myCur.execute("""SELECT * FROM __bankTransactions__ WHERE sender_account=%s OR receiver_account=%s
            ORDER BY transaction_date DESC""",(acn, acn))
        transactions = myCur.fetchall()

        if not transactions:
            print("No transactions found.")
            return

        for transaction in transactions:
            transaction = list(transaction)
            transaction[3] = float(transaction[3])
            transaction[6] = str(transaction[6])
            transaction[8] = float(transaction[8]) if transaction[8] else 0.0
            transaction[9] = float(transaction[9]) if transaction[9] else 0.0
            print(tuple(transaction))

    except mysql.connector.Error as err:
        print(f"Unable to fetch transaction history.\nReason: {err}")
