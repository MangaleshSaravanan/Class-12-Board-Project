from backend import *

start()

while True:
    print("-" * 30, "BANK OF PARADISE", "-" * 30)
    print("""
1. Create Customer
2. Add Money
3. Withdraw Money
4. Transfer Money
5. Customer Details
6. Transaction History
7. Balance Review
8. Exit
""")

    choice = input("Enter the option number: ").strip()
    try:
        if choice == "1":
            name = input("Enter Name: ")
            dob = input("Enter Date of Birth (YYYY-MM-DD): ")
            nationality = input("Enter Nationality: ")
            phnum = input("Enter Phone Number: ")
            email = input("Enter Email Address: ")
            passport = input("Enter Passport Number: ")
            visa_status = input("Enter Visa Status: ")
            address = input("Enter Address: ")
            tax_id = input("Enter Tax ID: ")
            tax_residency = input("Enter Tax Residency Country: ")
            occupation = input("Enter Occupation: ")
            source_of_funds = input("Enter Source of Funds: ")
            account_purpose = input("Enter Account Purpose: ")
            password = input("Enter Password: ")

            createAccount(
                password,
                name,
                dob,
                nationality,
                phnum,
                email,
                passport,
                visa_status,
                address,
                tax_id,
                tax_residency,
                occupation,
                source_of_funds,
                account_purpose
            )

        elif choice == "2":
            account = input("Account Number: ")
            password = input("Password: ")
            amount = input("Amount: ")
            addMoney(account, password, amount)

        elif choice == "3":
            account = input("Account Number: ")
            password = input("Password: ")
            amount = input("Amount: ")
            withdrawMoney(account, password, amount)

        elif choice == "4":
            sender = input("Sender Account: ")
            password = input("Password: ")
            receiver = input("Receiver Account: ")
            amount = input("Amount: ")
            transferMoney(sender, password, receiver, amount)

        elif choice == "5":
            customer_id = input("Customer ID: ")
            account = input("Account Number: ")
            password = input("Password: ")
            displayDetails(customer_id, account, password)

        elif choice == "6":
            account = input("Account Number: ")
            password = input("Password: ")
            getTransactions(account, password)

        elif choice == "7":
            account = input("Account Number: ")
            password = input("Password: ")
            getBalance(account, password)

        elif choice == "8":
            print("Thank you for using Bank of Paradise.")
            break

        else:
            print("Please enter a valid option.")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as err:
        print(f"Unexpected error: {err}")
    print()
