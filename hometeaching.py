class District:
    def __init__(self, district_leader, companionships=None, number_of_companionships=0):
        self.district_leader = district_leader
        if companionships is None:
            self.companionships = []
        else:
            self.companionships = companionships
        self.number_of_companionships = number_of_companionships

    def add_companionship(self, companionship):
        self.companionships.append(companionship)
        self.number_of_companionships += 1

    def to_string(self):
        return_string = ''
        return_string += 'District Leader: ' + self.district_leader + '\n'
        for comp in self.companionships:
            return_string += comp.to_string()
        return return_string


class Hometeacher:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def to_string(self):
        return self.first_name + ' ' + self.last_name + '\n'

    def get_name(self):
        return self.first_name + ' ' + self.last_name


class Hometeachee:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        from lds_scraper import HometeachingScraper as hs
        months = hs.months
        self.hometeaching = {months[i][1]: 0 for i in range(1, 13)}

    def to_string(self):
        return '\t' + self.first_name + ' ' + self.last_name + '\n'

    def get_name(self):
        return self.first_name + ' ' + self.last_name


class Companionship:
    def __init__(self, companions=None, hometeachees=None):
        if companions is None:
            self.companions = []
        else:
            self.companions = companions
        if hometeachees is None:
            self.hometeachees = []
        else:
            self.hometeachees = hometeachees

    def to_string(self):
        return_string = ''
        for comp in self.companions:
            return_string += comp.to_string()
        for hometeachee in self.hometeachees:
            return_string += hometeachee.to_string()
        return return_string
