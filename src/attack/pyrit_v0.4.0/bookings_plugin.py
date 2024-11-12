import json
from typing import Annotated
from datetime import datetime, timedelta
from typing import Annotated


from semantic_kernel.functions.kernel_function_decorator import kernel_function

class BookingsPlugin:
    """A plugin for booking tables at a restaurant."""

    def __init__(
        self,
        db_file: str,
        customer_timezone: str = "America/Chicago",
    ):
        """Initializes a new instance of the BookingsPlugin class.

        Args:
            db_file (str): The path to the local JSON file to use as a database.
            customer_timezone (str, optional): The timezone of the customer. Defaults to "America/Chicago".
        """
        self.db_file = db_file
        self.customer_timezone = customer_timezone

    @kernel_function(name="return_coucou", description="Returns a friendly coucou messsage")
    async def return_hello(self) -> Annotated[str, "The coucou message"]:
        """return Hello

        Args:

        Returns:
            str: The coucou message
        """
        return "hiii how are you ?"

    @kernel_function(name="book_table", description="Book a table at a restaurant")
    async def book_table(
        self,
        restaurant: Annotated[str, "The name of the restaurant"],
        date_time: Annotated[str, "The time in UTC, formatted as an ISO datetime string, like 2024-09-15T19:00:00"],
        party_size: Annotated[int, "The number of people in the party"],
        customer_name: Annotated[str, "The name of the customer"],
        customer_email: Annotated[str, "The email of the customer"],
        customer_phone: Annotated[str, "The phone number of the customer"],
    ) -> Annotated[str, "The booking appointment ID"]:
        """Book a table at a restaurant.

        Args:
            restaurant (str): The name of the restaurant.
            date_time (str): The time in UTC.
            party_size (int): The number of people in the party.
            customer_name (str): The name of the customer.
            customer_email (str): The email of the customer.
            customer_phone (str): The phone number of the customer.

        Returns:
            str: The status of the booking.
        """
        # print(f"System > Do you want to book a table at {restaurant} on {date_time} for {party_size} people?")
        # print("System > Please confirm by typing 'yes' or 'no'.")
        # confirmation = input("User:> ")
        # if confirmation.lower() != "yes":
        #     return "Booking aborted by the user."

        # Load the database
        with open(self.db_file, 'r') as f:
            db = json.load(f)

        # Generate a new reservation ID
        reservation_id = str(len(db) + 1)

        # Add the new reservation to the database
        db[reservation_id] = {
            "restaurant": restaurant,
            "date_time": date_time,
            "party_size": party_size,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
        }

        # Save the database
        with open(self.db_file, 'w') as f:
            json.dump(db, f)

        return f"Booking successful! Your reservation ID is {reservation_id}."

    @kernel_function(name="list_revervations", description="List all reservations")
    async def list_reservations(self) -> Annotated[str, "The list of reservations"]:
        """List the reservations for the booking business."""
        # Load the database
        with open(self.db_file, 'r') as f:
            db = json.load(f)

        return "\\n".join(
            [
                f"{db[reservation_id]['restaurant']} on {db[reservation_id]['date_time']} with id: {reservation_id}"
                for reservation_id in db
            ]
        )

    @kernel_function(name="cancel_reservation", description="Cancel a reservation")
    async def cancel_reservation(
        self,
        reservation_id: Annotated[str, "The ID of the reservation"],
        restaurant: Annotated[str, "The name of the restaurant"],
        date: Annotated[str, "The date of the reservation"],
        time: Annotated[str, "The time of the reservation"],
        party_size: Annotated[int, "The number of people in the party"],
    ) -> Annotated[str, "The cancellation status of the reservation"]:
        """Cancel a reservation."""
        print(f"System > [Cancelling a reservation for {party_size} at {restaurant} on {date} at {time}]")

        # Load the database
        with open(self.db_file, 'r') as f:
            db = json.load(f)

        # Remove the reservation from the database
        if reservation_id in db:
            del db[reservation_id]

        # Save the database
        with open(self.db_file, 'w') as f:
            json.dump(db, f)

        return "Cancellation successful!"
