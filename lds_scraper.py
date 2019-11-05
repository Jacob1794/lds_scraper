########################SELENIUM##################################################
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#################################################################################
from hometeachingLocators import DistrictLocators as DL, SignInLocators as SL
from hometeaching import District, Hometeacher, Hometeachee, Companionship
from urls import URLS
import datetime as dt
import unicodedata
import platform
import csv

from datetime import datetime

current_month = datetime.now().month


class HometeachingScraper:
    months = {1: ('January', 'Jan'),
              2: ('February', 'Feb'),
              3: ('March', 'Mar'),
              4: ('April', 'Apr'),
              5: ('May', 'May'),
              6: ('June', 'Jun'),
              7: ('July', 'Jul'),
              8: ('August', 'Aug'),
              9: ('September', 'Sept'),
              10: ('October', 'Oct'),
              11: ('November', 'Nov'),
              12: ('December', 'Dec')
              }

    def __init__(self, email, pass_word, csv_folder='csvs/'):
        date = dt.datetime.now()
        self.driver = None
        self.wait = None
        self.current_month = str(date.month)
        self.current_year = str(date.year)
        self.current_day = str(date.day)
        self.email = email
        self.pass_word = pass_word
        self.csv_folder = csv_folder
        self.scrape_started = False
        self.scrape_finished = False
        self.districts = []

    def get_csv_name(self, purpose=None):
        csv_name = 'hometeaching' + \
                   '-' + self.current_month + \
                   '-' + self.current_day + \
                   '-' + self.current_year
        if purpose is not None:
            csv_name += '-' + purpose
        return csv_name

    def open_browser(self):
        self.driver = webdriver.Chrome()
        self.driver.get(URLS.HOMETEACHING_PAGE)
        self.wait = WebDriverWait(self.driver, 10)

    def close(self):
        self.driver.quit()
        self.csv_file.close()

    def scrape(self, get_all=False):
        try:
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(DL.DISTRICTS))
        finally:
            pass

        districts_len = self.driver.find_elements(*DL.DISTRICTS)
        print(districts_len)
        # print(districts_len)
        # Add the district leaders to the districts
        for i in range(1, len(districts_len) + 1):
            district_leader = self.driver.find_element(
                *(By.XPATH, '//*[@id="organizeList"]/accordion/div/div[' + str(i) + ']/div[2]/div/div[1]/a')).text
            self.districts.append(District(district_leader=district_leader))

        # Look for the companionships within the district and add all that information to the district
        for i in range(len(districts_len)):
            companionships = districts_len[i].find_elements(*DL.COMPANIONSHIP)
            companionships = companionships[1:]
            res = []
            for companionship in companionships:
                # elem = companionship.find_element(By.CSS_SELECTOR, '.teacher-list')
                values = {}

                soup = BeautifulSoup(companionship.get_attribute('outerHTML'), 'lxml')
                teachers = soup.find('div', {'class': 'teacher-list'})
                teachers = teachers.find_all('li')
                teacher1 = teachers[0].text.replace('\n', '').strip()
                teacher2 = teachers[1].text.replace('\n', '').strip()
                values['comp1'] = teacher1
                values['comp2'] = teacher2
                values['teachees'] = []

                assignments = soup.find_all('div', {'ng-repeat': 'assignment in comp.assignments'})
                for assignment in assignments:
                    teachee = assignment.find('div', {'class': 'assignment-name'}).text.replace('\n', '').strip()
                    obj = {'name': teachee}
                    visits_cont = assignment.find('div', {'class': 'visit-cb-group'})
                    checkboxes = visits_cont.find_all('span', {'class': 'visit-cb'})
                    vals = {}
                    vals[self.get_month(-2)] = self.get_checked(checkboxes[0])
                    vals[self.get_month(-1)] = self.get_checked(checkboxes[1])
                    vals[self.get_month(0)] = self.get_checked(checkboxes[2])
                    obj['past3months'] = vals
                    values['teachees'].append(obj)
                res.append(values)
            print(res)
            print('\n\n')

            # hometeachee_data_temp = districts_len[i].find_elements(*DL.HOMETEACHEE_DATA)
            # hometeachee_data = []
            # for hometeachee in hometeachee_data_temp:
            #     if hometeachee.text is not u'':
            #         hometeachee_data.append(hometeachee)

    @staticmethod
    def get_month(dis):
        if current_month + dis <= 0:
            return current_month + dis % 12
        else:
            return current_month + dis

    @staticmethod
    def get_checked(cb):
        item = cb.find('span', 'visit-icon')
        classes = item.get('class')

        if 'icon-check-active' in classes:
            return 'visited'
        elif 'icon-close' in classes:
            return 'not visited'
        elif 'icon-open' in classes:
            return 'UNKNOWN'
        else:
            print('AWWAWUHEUHAEUHWAUHWAUAWHUAWAWAWAW UNKNOWN ERROR')
            # then they've been visited
            # print(f'>>>> {item.get("class")}\n\n')

    def print_data(self):
        for district in self.districts:
            print(district.to_string())

    def by_district_to_csv(self):
        csv_headers = [
            'District Leader',
            'Companionship',
            'Assignment',
            'Home taught',
            'Hometeaching Percentage'
        ]
        months = [self.months[i][1] for i in range(1, 13)]
        csv_headers.extend(months)

        with open(self.csv_folder + self.get_csv_name('by_district'), 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            self.write_row(writer, csv_file, csv_headers)
            for district in self.districts:
                self.write_row(writer, csv_file, [district.district_leader])
                for companionship in district.companionships:
                    for companion in companionship.companions:
                        self.write_row(writer, csv_file, ['', companion.get_name()])
                    for hometeachee in companionship.hometeachees:
                        self.write_row(writer, csv_file,
                                       ['', '', hometeachee.get_name()])  # TODO: ADD in hometeaching here

    def companionships_to_csv(self):
        csv_headers = [
            'Companionship',
            'Assignment',
            'Hometeaching Percentage'

        ]

        with open(self.csv_folder + self.get_csv_name('companionships'), 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            self.write_row(writer, csv_file, csv_headers)
            for district in self.districts:
                for companionship in district.companionships:
                    for companion in companionship.companions:
                        self.write_row(writer, csv_file, [companion.get_name()])
                    for hometeachee in companionship.hometeachees:
                        self.write_row(writer, csv_file,
                                       ['', hometeachee.get_name()])  # TODO: ADD in hometeaching here

    def csv_database_format(self):
        csv_headers = [
            'District Leader',
            'Companion 1',
            'Companion 2',
            'Companion 3',
            'Assignment 1',
            'Assignment 2',
            'Assignment 3',
            'Assignment 4',
            'Assignment 5',
            'Complete 1',
            'Complete 2',
            'Complete 3',
            'Complete 4',
            'Complete 5',

        ]

        with open(self.csv_folder + self.get_csv_name('csv_database'), 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            self.write_row(writer, csv_file, csv_headers)
            for district in self.districts:
                for companionship in district.companionships:
                    comp_data = [district.district_leader]

                    for i in range(3):
                        if i < len(companionship.companions):
                            comp_data.append(companionship.companions[i].get_name())
                        else:
                            comp_data.append('')

                    for i in range(6):
                        if i < len(companionship.hometeachees):
                            comp_data.append(companionship.hometeachees[i].get_name())
                        else:
                            comp_data.append('')
                    self.write_row(writer, csv_file, comp_data)

    def asciify(self, row):
        try:
            return [unicodedata.normalize('NFKD', datum).encode('ascii', 'ignore') for datum in row]
        except TypeError:
            return row

    def sign_in(self):
        email_field = self.driver.find_element(*SL.EMAIL_FIELD)
        pass_word_field = self.driver.find_element(*SL.PASS_FIELD)
        submit_btn = self.driver.find_element(*SL.SUBMIT_BTN)
        email_field.clear()
        email_field.send_keys(self.email)
        pass_word_field.clear()
        pass_word_field.send_keys(self.pass_word)
        submit_btn.click()

    def write_row(self, writer, csv_file, row):
        row = self.asciify(row)
        # print(''.join(row))
        writer.writerow(row)
        csv_file.flush()
