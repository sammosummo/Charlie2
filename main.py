import logging
from charlie2.tools.app import run_app


if __name__ == "__main__":

    logging.basicConfig(
        filename='charlie.log',
        filemode='w',
        level=logging.DEBUG,
        format='%(asctime)s::%(name)s::%(levelname)s::%(message)s'
    )
    run_app()
