
from emirates import run_emirates, origin_insertion, destination_insertion, select_dropdown_menu_origin, select_dropdown_menu_destination, select_departure_date, scrape_and_save

if __name__ == '__main__':
    run_emirates()
    origin_insertion()
    select_dropdown_menu_origin()
    destination_insertion()
    select_dropdown_menu_destination()
    select_departure_date()
    #turn_mileage_on()
    scrape_and_save()
    #serching()



