import gspread
import datetime


class SheetManager:
    def __init__(self, keys_file, workbook, sheet, clients_file):
        access = gspread.service_account(filename=keys_file)
        self.worksheet = access.open(workbook).worksheet(sheet)
        self.client_file = clients_file
        self.clients = SheetManager.__load_clients_from_file(self.client_file)

    def log_session(self):
        row = []
        row.append(SheetManager.__get_date("Was this session today? Enter \"y\" for yes or \"n\" for no: "))
        row.append(self.__get_client())

        description = input("Description: ").strip()
        row.append(description)

        hours = input("Time (hours): ").strip()
        while float(hours) < 0:
            print("Input must be a positive number")
            hours = input("Time (hours): ").strip()
        row.append(hours)

        rate = input("Rate: ").strip()
        while not rate.isnumeric or int(rate) < 0:
            print("Rate must be a positive integer")
            rate = input("Rate: ").strip()
        row.append(int(rate) * float(hours))

        print(row)
        check_submit = input("Are you sure you want to enter this record? (y or n): ").strip().lower()
        while check_submit != 'y' and check_submit != 'n':
            print("You must enter \"y\" or \"n\"")
            check_submit = input("Are you sure you want to enter this record? (y or n): ").strip().lower()

        if check_submit == 'y':
            self.worksheet.insert_row(row, self.get_row_count() + 1)

    def get_invoice(self):
        client = self.__get_client()
        filter_client = list(filter(lambda el: el['Client'] == client, self.get_all_lines()))
        filter_paid = list(filter(lambda el: el['Paid?'] != 'Paid', filter_client))

        end_date = SheetManager.__get_date("Is today the end of the billing period? Enter \"y\" or \"n\": ")
        filter_date = list(filter(lambda el: SheetManager.__compare_dates(el['Date'], end_date), filter_paid))

        count = 0
        for row in filter_date:
            count += int((row['Amount'][1:]))

        print(f"Total for the billing period is: ${count}")

    def log_invoice(self):
        client = self.__get_client()
        filter_client = list(filter(lambda el: el['Client'] == client, self.get_all_lines()))
        filter_paid = list(filter(lambda el: el['Paid?'] != 'Paid', filter_client))

        end_date = ""
        amount = int(input("Payment amount? (Enter -1 to close all open payments): "))

        while amount != 0:
            if amount == -1:
                end_date = datetime.datetime.now().strftime("%x")
                break
            else:
                i = 0
                while i < len(filter_paid) and amount > 0:
                    row = filter_paid[i]
                    amount -= int((row['Amount'][1:]))
                    end_date = row['Date']
                    i += 1

                if amount != 0:
                    print("Incorrect amount entered")
                    amount = int(input("Payment amount? (Enter -1 to close all open payments): "))

        filter_date = list(filter(lambda el: SheetManager.__compare_dates(el['Date'], end_date), filter_paid))

        for row in filter_date:
            row_num = self.__get_row_by_date(row['Date'])
            col_num = self.__get_col_by_name('Paid?')
            self.worksheet.update_cell(row_num, col_num, 'Paid')

    def get_open_payments(self):
        filter_paid = list(filter(lambda el: el['Paid?'] != 'Paid', self.get_all_lines()))
        print(f"Incoming cash: ${SheetManager.__sum_payments_in_list(filter_paid)}")

    def get_payment_totals(self):
        resp = input("Would you like to include open payments? (y or n): ").lower().strip()
        while resp != "y" and resp != "n":
            print("You must enter \"y\" or \"n\"")
            resp = input("Would you like to include open payments? (y or n): ").lower().strip()

        filtered_list = self.get_all_lines()
        if resp == "n":
            filtered_list = list(filter(lambda el: el['Paid?'] == 'Paid', filtered_list))

        today = datetime.date.today()

        filter_month = list(filter(lambda el: SheetManager.__parse_date(el['Date']).month == today.month and
                                              SheetManager.__parse_date(el['Date']).year == today.year, filtered_list))
        print('\n')
        print("This month...")
        print(f"Hours: {SheetManager.__sum_hours_in_list(filter_month)}")
        print(f"Total: ${SheetManager.__sum_payments_in_list(filter_month)}\n")

        print("This year...")
        today_last_yr = today.replace(year=today.year - 1)

        filter_year = list(filter(lambda el: SheetManager.__parse_date(el['Date']) >= today_last_yr, filtered_list))
        print(f"Hours: {SheetManager.__sum_hours_in_list(filter_year)}")
        print(f"Amount per month: {SheetManager.__sum_payments_in_list(filter_year) / 12.0}")
        print(f"Total: ${SheetManager.__sum_payments_in_list(filter_year)}\n")

        print("All time...")
        print(f"Hours: {SheetManager.__sum_hours_in_list(filtered_list)}")
        print(f"Total: ${SheetManager.__sum_payments_in_list(filtered_list)}\n")

    def edit_clients(self):
        action = input("Would you like to \"add\" or \"remove\" a client from your list? ").strip().lower()
        while action != "add" and action != "remove":
            print("You must enter add or remove")
            action = input("Would you like to \"add\" or \"remove\" a client from your list? ").strip().lower()

        if action == "add":
            alias = input("Enter an alias for this client (i.e. Max Herman --> \"max\"): ").strip().lower()
            while alias.find(" ") != -1 or len(alias) == 0:
                print("Alias must be one word")
                alias = input("Enter an alias for this client (i.e. Max Herman --> \"max\"): ").strip().lower()

            name = input("Enter the name you would like to appear in your records: ").strip()
            while len(name) == 0:
                name = input("Enter the name you would like to appear in your records: ").strip()

            self.clients[alias] = name

            file = open(self.client_file, "a")
            file.write(f"\n{alias}: {name}")
            file.close()

        else:
            delete_client = input("Which client would you like to remove "
                                  "(enter \"options\" to show all options): ").strip().lower()
            while delete_client not in self.clients:
                if delete_client == "options":
                    print(self.clients)
                else:
                    print(f"\"{delete_client}\" does not exist. Please enter an existing client.")
                delete_client = input("Which client would you like to remove "
                                      "(enter \"options\" to show all options): ").strip().lower()

            self.clients.pop(delete_client)

            file = open(self.client_file, "w")
            for key, val in self.clients.items():
                file.write(f"{key}: {val}\n")

            file.close()

    @staticmethod
    def __sum_payments_in_list(_list):
        amount = 0
        for row in _list:
            amount += int((row['Amount'][1:]))

        return amount

    @staticmethod
    def __sum_hours_in_list(_list):
        amount = 0
        for row in _list:
            if str(row['Duration (hr)']).isnumeric():
                amount += int((row['Duration (hr)']))

        return amount

    def __get_client(self):
        client = input("Client (enter \"options\" to show all options): ").strip().lower()
        while client not in self.clients:
            if client == "options":
                options = []
                for key, value in self.clients.items():
                    options.append(key)
                print(options)
            else:
                print(f"\"{client}\" does not exist. Please enter an existing client.")
            client = input("Client (enter \"options\" to show all options): ").strip().lower()
        return str(self.clients[client])

    @staticmethod
    def __get_date(prompt):
        date_resp = input(prompt).lower().strip()
        while date_resp != "y" and date_resp != "n":
            print("You must enter \"y\" or \"n\"")
            date_resp = input(prompt).lower().strip()

        if date_resp == "y":
            date = datetime.datetime.now()
        else:
            date_input = input("Enter in date in the format MM/dd/YY: ")
            date_arr = date_input.split('/')

            date = datetime.datetime(int("20" + date_arr[2] if len(date_arr[2]) == 2 else date_arr[2]),
                                     int(date_arr[0]), int(date_arr[1]))

        return date.strftime("%m/%d/%Y")

    # returns if d1 was before d2
    @staticmethod
    def __compare_dates(d1, d2):
        d1_arr = d1.split('/')
        date1 = datetime.date(int(d1_arr[2]), int(d1_arr[0]), int(d1_arr[1]))

        d2_arr = d2.split('/')
        date2 = datetime.date(int(d2_arr[2]), int(d2_arr[0]), int(d2_arr[1]))

        return date1 <= date2

    @staticmethod
    def __parse_date(date_str):
        date_arr = date_str.split('/')
        return datetime.date(int(date_arr[2]), int(date_arr[0]), int(date_arr[1]))

    def get_all_lines(self):
        return self.worksheet.get_all_records()

    def get_row_count(self):
        str_list = list(filter(None, self.worksheet.col_values(1)))
        return len(str_list)

    def __get_row_by_date(self, date):
        # first line of data is on row 2
        count = 2
        for row in self.get_all_lines():
            if date == row['Date']:
                break
            else:
                count += 1
        return count

    def __get_col_by_name(self, name):
        count = 1
        for key, val in self.get_all_lines()[0].items():
            if key.lower() == name.lower():
                break
            else:
                count += 1

        return count

    @staticmethod
    def __load_clients_from_file(filepath):
        file = open(filepath)

        ret = {}
        for line in file:
            line_arr = line.split(":")
            ret[line_arr[0].strip().lower()] = line_arr[1].strip()

        file.close()
        return ret
