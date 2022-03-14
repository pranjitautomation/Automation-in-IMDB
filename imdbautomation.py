
import logging
import os

import pandas as pd
from bs4 import BeautifulSoup
from retry import retry
from RPA.Browser.Selenium import Selenium
from selenium.common.exceptions import (ElementNotInteractableException,
                                        ElementNotVisibleException)

browser = Selenium()


class ImdbAutomation:

    def open_browser(self) -> None:
        browser.open_available_browser("https://www.imdb.com")
        browser.set_screenshot_directory(
            os.path.join(os.getcwd(), "output")
            )
        browser.wait_until_element_is_visible(
            'xpath://*[@id="imdbHeader-navDrawerOpen--desktop"]/div'
            )

    @retry( (AssertionError, ElementNotVisibleException, ElementNotInteractableException), tries=2, delay=2)
    def go_to_table_of_top_250_tv_shows(self) -> None:

        """
        This method is defined to go Top 20 TV shows list page
        WorkFlow:
        1) Home Page
        2) Drop Down Menu (On left corner)
        3) Top 20 Tv Shows List according to their Tv shows List

        """

        try:
            # Go to Menu bar
            browser.click_element_when_visible(
                'xpath://*[@id="imdbHeader-navDrawerOpen--desktop121"]/div'
                )

            # Clicking the element- Top 250 Tv Shows
            browser.click_element_when_visible(
                'xpath://*[contains(text(), "Top 250 TV Shows")]'
                )

            # Wait until the sort options will come
            browser.wait_until_element_is_visible(
                'xpath://*[@id="lister-sort-by-options"]'
                )

        except Exception as ex:
            logging.error('This is an error message', ex)
            browser.capture_page_screenshot("Last_page_before_error.png")

    @retry( (AssertionError, ElementNotVisibleException, ElementNotInteractableException), tries=2, delay=2)
    def sort_table_data(self, sort_by_options) -> None:
        """
        This method sorting table _data according to argument given by user

        Args:
            sort_by_options (string): The html table will be arranged
                                    according to the sort_by_options argument
        """

        try:
            # Selecting the release data option from sort menu
            browser.select_from_list_by_label(
                'xpath://*[@id="lister-sort-by-options"]',
                sort_by_options
                )
            browser.wait_until_element_is_visible(
                'xpath://*[@class = "lister"]'
                )

        except Exception as ex:
            logging.error('This is an error message', ex)
            browser.capture_page_screenshot("Last_page_before_error.png")

    def save_html_table(self) -> str:
        """
        This method takes the innerhtml data of a HTML Table
        & saves in a html file

        Returns:
            String : Return the path of Html file
                    Which contains innerhtml of HTML table
        """

        # taking innerhtml data of the html table
        html_data: str = browser.get_element_attribute(
            'xpath://*[@class = "lister"]', 'innerHTML'
            )

        #  making a html file where innerHTMl data is saving
        html_file_path: str = os.path.join(os.getcwd(), "innerhtml.html")

        f = open(html_file_path, "w")
        f.write(html_data)
        f.close()

        return html_file_path

    def html_table_to_csv(self) -> str:  # making csv
        """
        This method is defined to make a csv file from a html table
        Using BeautifulSoup method

        and  make a CSV sheet using Pandas Dataframe

        Returns:
            String: Returns the path of CSV file
                    Which contains the table of Top 250 TV Shows
        """

        html_file: str = self.save_html_table()

        soup = BeautifulSoup(open(html_file), 'html.parser')
        table: list = soup.find_all("table")[0]

        headers = []
        # heading row containing the name of column added to the headers list
        for th in table.find("tr").find_all("th"):
            headers.append(th.text.strip())

        rows = []
        # saving table data in a list
        for tr in table.find_all("tr")[1:]:
            cells = []
            tds: list = tr.find_all("td")

            for td in tds:
                # adding table data of each cell in cells list one by one
                cells.append(td.text.strip())

                if len(cells) != 1:
                    oneliner: str = cells[1].replace("\n", " ")
                    cells[1] = oneliner

            # adding cells list i.e each table row  data in rows list
            rows.append(cells)

        df = pd.DataFrame(rows, columns=headers)

        csv_file_name: str = "IMDB_TOP_250_TV_SHOWS_LIST.csv"

        csv_path: str = os.path.join(
            os.getcwd(), f'output/{csv_file_name}'
            )

        df.to_csv(csv_path, index=False)
        os.remove(html_file)

        return csv_path

    def generate_csv(self) -> None:
        """
        This method make some changes in csv file
        like delete some column:
        one is named Your Rating
        & another is unnamed columns

        """

        csv_path: str = self.html_table_to_csv()

        # reading the csv
        df = pd.read_csv(csv_path)
        # deleting the "Your rating" column
        df.drop("Your Rating", axis=1, inplace=True)

        # deleting all the unnamed column from the csv
        df.drop(
            df.columns[
                df.columns.str.contains('unnamed', case=False)
                ], axis=1, inplace=True
            )

        # Saving the dataframe to CSV
        df.to_csv(csv_path, index=False)
