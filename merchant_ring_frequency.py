# merchant_ring_frequency.py
# A little program that calculates which Littfeld shop wagons are currently available based on a given date.
    
    
import random
import re
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

class Store:
    def __init__(self, name, availability_pattern, page):
        self.name = name
        self.availability_pattern = availability_pattern
        self.page = page
        self.random_weekends = None
        self.random_leave_months = None
        self.random_weeks = None
        if "leaves 1 weekend a month" in availability_pattern:
            self.random_weekend = self.select_random_weekends(datetime.now().year, datetime.now().month, 1)
        if "leaves for 1 month each season" in availability_pattern:
            self.random_leave_months = self.select_season_leave_months()
        if "2 weekends a month" in availability_pattern:
            self.random_weekends = self.select_random_weekends(datetime.now().year, datetime.now().month, 2)
        if "One week a month, except in winter" in availability_pattern:
            self.random_weeks = self.select_random_weeks(datetime.now().year, datetime.now().month, 1)
        if "leaves 1 week every month" in availability_pattern:
            self.random_weeks = self.select_random_weeks(datetime.now().year, datetime.now().month, 1)
        
        
    def select_random_weekends(self, year, month, num_weekends):
        """returns a random sample list of num_weekends number of tuples containing the days (i.e. 15, 21 etc.) of the start and end of each weekend 

        Args:
            year (datetime.year): the year of an availability period
            month (datetime.month): the month of an availability period
            num_weekends (int): number of weeks availabile within an availability frequency


        Returns:
            list: [(weekend_start_1, weekend_end_1), ... (weekend_start_n, weekend_end_n)]
        """
        weekends = []
        day = date(year, month, 1)
        while day.month == month:
            if day.weekday() == 5:  # Saturday
                weekend_end = day + timedelta(days=1)
                if weekend_end.month == month:  # Ensure the weekend is within the same month
                    weekends.append((day.day, weekend_end.day))
            day += timedelta(days=1)
        return random.sample(weekends, num_weekends) if len(weekends) >= num_weekends else weekends
    
    def select_random_weeks(self, year, month, num_weeks):
        """returns a random sample list of num_weeks number of tuples containing the days (i.e. 15, 21 etc.) of the start and end of each week 

        Args:
            year (datetime.year): the year of an availability period
            month (datetime.month): the month of an availability period
            num_weeks (int): number of weeks availabile within an availability frequency

        Returns:
            list: [(week_start_1, week_end_1), ... (week_start_n, week_end_n)]
        """
        weeks = []
        day = date(year, month, 1)
        while day.month == month:
            if day.weekday() == 0:  # Monday
                week_end = day + timedelta(days=6)
                if week_end.month == month: # Ensures week is within the same month
                    weeks.append((day.day, week_end.day))
            day += timedelta(days=1)
        return random.sample(weeks, num_weeks) if len(weeks) >= num_weeks else weeks
    
    def select_weeks_in_period(self, start_date, end_date, num_weeks):
        """returns a random sample list of num_weeks number of tuples containing the datetime objects of the start and end of weeks

        Args:
            start_date (datetime): start of an availability period
            end_date (datetime): end of an availability period
            num_weeks (int): number of weeks available within a availability frequency

        Returns:
            list: [(year_1, month_1, day_1), ..., (year_n, month_n, day_n)]
        """
        weeks = []
        day = start_date
        while start_date <= day <= end_date:
            if day.weekday() == 0:
                week_end = day + timedelta(days=6)
                if week_end.month <= end_date.month:
                    weeks.append((day, week_end))
            day += timedelta(days=1)
        return random.sample(weeks, num_weeks) if len(weeks) >= num_weeks else weeks
        
    
    def select_season_leave_months(self):
        """Selects 1 random month from each season

        Returns:
            list: [winterINT, springINT, summerINT, autumnINT]
        """
        seasons = {
            'winter': [12, 1, 2],
            'spring': [3, 4, 5],
            'summer': [6, 7, 8],
            'autumn': [9, 10, 11]
        }
        leave_months = []
        for months in seasons.values():
            leave_months.append(random.choice(months))
        return leave_months

    def is_available(self, current_date):
        """given a datetime, returns TRUE or FALSE based on the availability pattern of a Store object 

        Args:
            current_date (datetime): the current date

        Returns:
            boolean: TRUE/FALSE
        """
        pattern = self.availability_pattern
        if pattern == "always":
            return True
        elif pattern == "Six days a week":
            off_day = random.randint(0,6)
            return current_date.weekday() != off_day
        elif match := re.match(r"(\d+) weeks? every (\d+) months?", pattern):
            weeks, months = map(int, match.groups())
            period_start = date(current_date.year, 1 + ((current_date.month - 1) // months) * months, 1)
            period_end = (period_start + relativedelta(months=months+1)) - relativedelta(days=1)            
            on_weeks = self.select_weeks_in_period(period_start, period_end, weeks)
            for week_start, week_end in on_weeks:
                if week_start <= current_date <= week_end:
                    return True
            return False
        elif pattern == "leaves for 1 month each season":
            if current_date.month in self.random_leave_months:
                return False
            return True
        elif pattern == "2 weekends a month":
            for weekend_start, weekend_end in self.random_weekends:
                if current_date.weekday() >= 5 and weekend_start <= current_date.day <= weekend_end:
                    return True
            return False
        elif pattern == "leaves 1 weekend a month":
            if self.random_weekend:
                weekend_start, weekend_end = self.random_weekend[0]
                return not (current_date.weekday() >= 5 and weekend_start <= current_date.day <= weekend_end)
            return True  # If no valid weekend found, assume available
        elif pattern == "One week a month, except in winter":
            if current_date.month in [12, 1, 2]:  # Winter
                return False
            if self.random_weeks:
                week_start, week_end = self.random_weeks[0]
                return (week_start <= current_date.day <= week_end)
            return True # if no valid week found, assume available
        elif pattern == "leaves 1 week every month":
            if self.random_weeks:
                week_start, week_end = self.random_weeks[0]
                return not (week_start <= current_date.day <= week_end)
            return True # if no valid week found, assume available
        elif pattern == "Every other week":
            return ((current_date - date(current_date.year, 1, 1)).days // 7) % 2 == 0
        return False

# List of stores, their availability patterns and page numbers
stores = [
    Store("Morris's Miscibles", "1 week every 3 months", 39),
    Store("Gallery of Curios", "1 week every 2 months", 40),
    Store("Violet's Athaneum", "leaves for 1 month each season", 42),
    Store("Game Parlor", "2 weekends a month", 43),
    Store("Alver's Bakery", "leaves 1 weekend a month", 44),
    Store("Chunky's Pet Pals", "always", 45),
    Store("Hugo's Lifesavers", "always", 45),
    Store("Brauniard's Auctions", "2 weeks every 1 month", 46),
    Store("Bard's Magical Secret", "One week a month, except in winter", 46),
    Store("House of Fineries", "2 weeks every 3 months", 47),
    Store("Lucas and Grier's", "Every other week", 47),
    Store("Mutya's This n That", "leaves 1 week every month", 49),
    Store("Angeline's Forgewagon", "leaves 1 week every month", 50),
    Store("Ayvaire's Nest", "always", 50),
    Store("Bluebird Wagon", "Six days a week", 51),
    Store("Delver Delicacies", "always", 57),
]

def list_available_stores(current_date):
    """given a date will check the availability from a list of stores

    Args:
        current_date (datetime): current date

    Returns:
        list: [(store_name_1, store_page_1), ... (store_name_n, store_page_n)]
    """
    available_stores = [(store.name, store.page) for store in stores if store.is_available(current_date)]
    return available_stores

def get_user_date():
    while True:
        user_input = input("Enter the current date (DD-MM-YYYY): ")
        try:
            return datetime.strptime(user_input, "%d-%m-%Y").date()
        except ValueError:
            print("Invalid date format. Please enter the date in DD-MM-YYYY format.")

# Get the current date from user input
current_date = get_user_date()

# # List stores available today
available_stores_today = list_available_stores(current_date)

print("Shop wagons available today:")
for store_name, page in available_stores_today:
    print(f"{store_name} (Page {page})")

