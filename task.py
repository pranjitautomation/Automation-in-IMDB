import imdbautomation

obj = imdbautomation.ImdbAutomation()


obj.open_browser()
obj.go_to_table_of_top_250_tv_shows()
obj.sort_table_data('Release Date')
obj.save_html_table()
obj.generate_csv()
