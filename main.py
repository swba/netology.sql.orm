from os import getcwd, path

from prettytable import PrettyTable
from sqlalchemy.orm import Session

from db import get_engine, setup, import_data, search_sales_by_publisher


def main():
    engine = get_engine()
    filename = path.join(getcwd(), 'fixtures', 'test_data.json')

    # Set up the tables and import test data.
    setup(engine)
    import_data(engine, filename)

    with Session(engine) as session:
        # Pretty table to print selected data.
        table = PrettyTable(["Book", "Shop", "Price", "Date"])
        table.align["Book"] = "l"
        table.align["Shop"] = "l"

        # Test variants.
        tests = {
            "%press%": "Publisher's name should include \"press\":",
            "3": "Publisher has ID 3:",
            "Pearson": "Publisher is Pearson",
            "%reilly": "Publisher's name ends with \"reilly\"",
        }
        for q in tests:
            print(tests[q])
            table.clear_rows()
            for sale in search_sales_by_publisher(session, q):
                stock = sale.stock
                shop = stock.shop
                book = stock.book

                table.add_row([
                    book.title,
                    shop.name,
                    sale.price,
                    sale.date_sale.strftime("%d-%m-%Y")
                ])
            print(table)
            print()


if __name__ == "__main__":
    main()