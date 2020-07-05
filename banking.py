import random
import string
from sys import exit
import sqlite3


DATABASE_PATH = "card.s3db"
DATABASE = "card"
DB_ATTRIBUTES = ["id", "number", "pin", "balance"]
current_user = {}
user_id = 1


def create_card(institution):
    card = "400000" + "".join([random.choice(string.digits) for i in range(9)])
    checksum = luhn_algo(card)
    card = card + str(checksum[0])
    print("Your card has been created")
    print("Your card number: \n{}".format(card))
    return card


def create_pin():
    pin = str("".join([random.choice(string.digits) for i in range(4)]))
    print("Your card PIN:\n{}".format(pin))
    return pin


def luhn_algo(card_):
    counter = 0
    control_sum = 0
    card_number = None
    card_holder = []
    if len(card_) == 16:
        card_number = card_[0:15]
    else:
        card_number = card_
    for i in card_number:
        if counter % 2 == 0:
            card_holder.append(int(i) * 2)
        else:
            card_holder.append(int(i))
        if int(card_holder[counter]) > 9:
            card_holder[counter] = int(card_holder[counter]) - 9
        control_sum = control_sum + int(card_holder[counter])
        counter = counter + 1
    if control_sum % 10 != 0:
        checksum = 10 - control_sum % 10
    else:
        checksum = 0
    return [checksum, control_sum]


def create_account(conn, institution=4):
    global user_id
    card = create_card(institution)
    pin = create_pin()
    cur = conn.cursor()
    try:
        cur.execute(r"""INSERT INTO {} ({}, {}, {}, {})
        VALUES ({}, {}, {}, {})
        """.format(DATABASE, DB_ATTRIBUTES[0], DB_ATTRIBUTES[1], DB_ATTRIBUTES[2], DB_ATTRIBUTES[3],
                   user_id, card, pin, 0))
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
    user_id = user_id + 1


def login(conn_):
    global current_user
    print("Enter your card number:")
    card = input()
    print("Enter your pin:")
    pin = input()
    cur = conn_.cursor()
    cur.execute("""SELECT number, pin FROM card""")
    conn_.commit()
    list_data = cur.fetchall()
    for i in list_data:
        if i == (card, pin):
            current_user = [card, pin]
            return True
    return False


def balance(conn_, usage=1):
    cur = conn_.cursor()
    cur.execute("""SELECT balance FROM card WHERE number={} and pin={};""".format(current_user[0], current_user[1]))
    conn_.commit()
    amount = cur.fetchone()[0]
    if usage:
        print("Balance: {}".format(amount))
    return amount


def add_income(conn_):
    print("Enter income:")
    amount = input()
    cur = conn_.cursor()
    cur.execute("""UPDATE card 
    SET balance= balance + {} 
    WHERE number={} and pin={}""".format(amount, current_user[0], current_user[1]))
    conn_.commit()
    print("Income was added!")


def check_card(number_card):
    card_sec = luhn_algo(number_card)
    if card_sec[0] == int(number_card[-1]) and (card_sec[1] + card_sec[0]) % 10 == 0:
        return True
    else:
        return False


def do_transfer(conn_):
    print("Enter card number:")
    card = input()
    if card == current_user[0]:
        print("You can't transfer money to the same account!")
    else:
        if check_card(card):
            cur = conn_.cursor()
            cur.execute("""SELECT number, balance FROM card WHERE number={}""".format(card))
            conn_.commit()
            holder = cur.fetchall()
            if len(holder) >= 1:
                # user_to = cur.fetchall()
                print("Enter how much money you want to transfer:")
                transfer = int(input())
                user_balance = balance(conn_, 0)
                if user_balance >= transfer:
                    cur.execute("""UPDATE card SET balance = balance + {} 
                    WHERE number = {} """.format(transfer, card))
                    conn_.commit()
                    cur.execute("""UPDATE card SET balance = balance - {} 
                    WHERE number = {} """.format(transfer, current_user[0]))
                    conn_.commit()
                    print("Success!")
                else:
                    print("Not enough money!")
            else:
                print("Such a card does not exist.")

        else:
            print("Probably you made mistake in the card number. Please try again!")


def close_acc(conn_):
    cur = conn_.cursor()
    cur.execute("""DELETE FROM card 
                WHERE number={} and pin={}""".format(current_user[0], current_user[1]))
    conn_.commit()
    print("The account has been closed!")


def menu2(conn):
    while True:
        print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
        choice = input()
        if choice == "1":
            balance(conn)
        elif choice == "2":
            add_income(conn)
        elif choice == "3":
            do_transfer(conn)
        elif choice == "4":
            close_acc(conn)
        elif choice == "5":
            print("You have successfully logged out.")
            current_user.clear()
            break
        elif choice == "0":
            print("Bye!")
            conn.close()
            exit(-1)


def menu1():
    conn = connect_db()
    while True:
        print("1. Create an account\n2. Log into account\n0. Exit\n")
        choice = input()
        if choice == "1":
            create_account(conn)
        elif choice == "2":
            if login(conn):
                print("You have successfully logged in.")
                menu2(conn)
            else:
                print("Wrong card number or PIN.")
        elif choice == "0":
            print("Bye!")
            conn.close()
            break


def connect_db():
    try:
        dburi = 'file:{}?mode=rw'.format(DATABASE_PATH)
        conn = sqlite3.connect(dburi, uri=True)
    except sqlite3.OperationalError as e:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE card(
        id INTEGER,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0);
        """)
    return conn
# **********************************************************************************************************************\


menu1()



