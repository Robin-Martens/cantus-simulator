import math
from dataclasses import dataclass


@dataclass
class Barrel:
    content: int
    price: int


@dataclass
class Venue:
    name: str
    max_guests: int
    rent_price: float
    small_barrel: Barrel
    big_barrel: Barrel


@dataclass
class Params:
    beer_per_person: int
    percentage_beer_drinkers: float
    amount_of_alumni: int
    alumni_paying: bool
    alumni_discount: float
    net_result: float


MEMBERS = 15
# in liter
BIG_BARREL_CONTENT = 50
# in liter
SMALL_BARREL_CONTENT = 30

BEERS_BIG_BARREL = 170
BEERS_SMALL_BARREL = 102
BEER_CONTENT = BIG_BARREL_CONTENT / BEERS_BIG_BARREL


@dataclass
class Simulator:
    params: Params
    venue: Venue

    def get_amount_of_beer_drinkers(self) -> int:
        return round((self.venue.max_guests) * self.params.percentage_beer_drinkers)

    def get_amount_of_beers(self) -> int:
        return self.get_amount_of_beer_drinkers() * self.params.beer_per_person

    # amount of small barrels, amount of big barrels
    def get_barrels(self) -> tuple[int, int]:
        amount_of_beers = self.get_amount_of_beers()

        remaining_beers = amount_of_beers - 0 * BEERS_SMALL_BARREL
        amount_of_big_barrels = math.ceil(remaining_beers / BEERS_BIG_BARREL)
        return (0, amount_of_big_barrels)

    def get_total_price(self) -> float:
        amount_of_small_barrels, amount_of_large_barrels = self.get_barrels()
        beer_price = (
            amount_of_small_barrels * self.venue.small_barrel.price
            + amount_of_large_barrels * self.venue.big_barrel.price
        )

        return beer_price + self.venue.rent_price

    # total, paying beer non member, paying non-beer non-member, paying beer member, paying non-beer, member
    def get_total_paying(self) -> tuple[int, int, int, int, int]:
        total_paying = self.venue.max_guests - MEMBERS

        paying_beer_non_member = round(
            (total_paying - self.params.amount_of_alumni)
            * self.params.percentage_beer_drinkers
        )
        paying_non_beer_non_member = round(
            (total_paying - self.params.amount_of_alumni)
            * (1 - self.params.percentage_beer_drinkers)
        )
        paying_beer_member = (
            round((self.params.amount_of_alumni) * self.params.percentage_beer_drinkers)
            if self.params.alumni_paying
            else 0
        )
        paying_non_beer_member = (
            round(
                (self.params.amount_of_alumni)
                * (1 - self.params.percentage_beer_drinkers)
            )
            if self.params.alumni_paying
            else 0
        )

        return (
            total_paying,
            paying_beer_non_member,
            paying_non_beer_non_member,
            paying_beer_member,
            paying_non_beer_member,
        )

    # beer price non-member, non-beer price non-member, beer price member, non-beer price member
    def calc_ticket_price(self) -> tuple[float, float, float, float]:
        total_price = self.get_total_price() + self.params.net_result

        total_paying = self.get_total_paying()[0]
        beer_price_non_member = round(
            (2 * total_price)
            / (
                (
                    total_paying
                    - self.params.alumni_discount * self.params.amount_of_alumni
                )
                * (1 + self.params.percentage_beer_drinkers)
            ),
            1,
        )

        non_beer_price_non_member = round(beer_price_non_member / 2, 1)

        beer_price_member = round(
            (1 - self.params.alumni_discount) * beer_price_non_member, 1
        )
        non_beer_price_member = round(
            (1 - self.params.alumni_discount) * non_beer_price_non_member, 1
        )

        return (
            beer_price_non_member,
            non_beer_price_non_member,
            beer_price_member,
            non_beer_price_member,
        )

    def gen_beer_info(self) -> tuple[float, float]:
        """
        total_beer_drunk, total_beer_bought, difference
        """
        # in liter
        total_beer_drunk = self.get_amount_of_beers() * BEER_CONTENT
        small_barrels, big_barrels = self.get_barrels()
        # in liter
        total_beer_bought = (
            small_barrels * SMALL_BARREL_CONTENT + big_barrels * BIG_BARREL_CONTENT
        )

        return round(total_beer_drunk, 1), round(total_beer_bought, 1)

    def gen_output(self) -> str:
        amount_of_small_barrels, amount_of_large_barrels = self.get_barrels()
        (
            beer_price_non_member,
            non_beer_price_non_member,
            beer_price_member,
            non_beer_price_member,
        ) = self.calc_ticket_price()
        (
            total_paying,
            beer_paying_non_member,
            non_beer_paying_non_member,
            beer_paying_member,
            non_beer_paying_member,
        ) = self.get_total_paying()

        beer_drunk, beer_bought = self.gen_beer_info()

        return f"""
=== Venue information ===
Name:                                   {self.venue.name}
Rent price:                             {self.venue.rent_price} euro
Max guests:                             {self.venue.max_guests}
Big barrel price:                       {self.venue.big_barrel.price} euro
small barrel price:                     {self.venue.small_barrel.price} euro

=== Simulation information ===
Beers per person:                       {self.params.beer_per_person}
Percentage of beer drinkers:            {self.params.percentage_beer_drinkers * 100}%
Amount of beer drinkers:                {self.params.percentage_beer_drinkers * self.venue.max_guests}
Amount of members:                      {MEMBERS}
Amount of alumni:                       {self.params.amount_of_alumni}
Alumni paying:                          {'Yes' if self.params.alumni_paying else 'No'}
Alumni discount:                        {self.params.alumni_discount * 100}%

Amount of beers per big barrel          {BEERS_BIG_BARREL}
Amount of beers per small barrel        {BEERS_SMALL_BARREL}

Net result:                             {self.params.net_result} euro

=== Simulation Results ===
Total price:                            {self.get_total_price()}

Amount of small barrels:                {amount_of_small_barrels}
Amount of large barrels:                {amount_of_large_barrels}

Total beer drunk                        {beer_drunk} liter
Total beer bought                       {beer_bought} liter
Difference                              {round(beer_bought - beer_drunk, 1)} liter

Paying beer drinkers non-members:       {beer_paying_non_member}
Paying non-beer drinkers non-members:   {non_beer_paying_non_member}
Total paying non-members:               {beer_paying_non_member + non_beer_paying_non_member}

Paying beer drinkers members:           {beer_paying_member}
Paying non-beer drinkers memberss:      {non_beer_paying_member}
Total paying members:                   {beer_paying_member + non_beer_paying_member}

Ticket price beer non-member:           {beer_price_non_member} euro
Ticket price non-beer non-member:       {non_beer_price_non_member} euro

Ticket price beer member:               {beer_price_member} euro
Ticket price non-beer member:           {non_beer_price_member} euro

Total revenue: {round(beer_paying_non_member * beer_price_non_member + non_beer_paying_non_member * non_beer_price_non_member + beer_paying_member * beer_price_member + non_beer_paying_member * non_beer_price_member, 1)} euro
        """


def write_output(sims: list[Simulator]) -> None:
    FILE_NAME = "simulation_result.txt"

    with open(FILE_NAME, "w+") as f:
        for sim in sims:
            f.write(sim.gen_output())
            f.write(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    venues = [
        # Venue(
        #     name="Recup",
        #     max_guests=100,
        #     rent_price=225,
        #     small_barrel=Barrel(30, 160),
        #     big_barrel=Barrel(50, 220),
        # ),
        Venue(
            name="Zamo",
            max_guests=100,
            rent_price=230,
            small_barrel=Barrel(30, 145),
            big_barrel=Barrel(50, 205),
        ),
        # Venue(
        #     name="Pavo",
        #     max_guests=80,
        #     rent_price=320,
        #     small_barrel=Barrel(30, 130),
        #     big_barrel=Barrel(50, 200),
        # ),
    ]

    params = [
        Params(
            beer_per_person=10,
            percentage_beer_drinkers=0.8,
            amount_of_alumni=10,
            alumni_paying=True,
            alumni_discount=1,
            net_result=0,
        ),
        Params(
            beer_per_person=10,
            percentage_beer_drinkers=0.8,
            amount_of_alumni=10,
            alumni_paying=True,
            alumni_discount=0.5,
            net_result=-300,
        ),
        Params(
            beer_per_person=10,
            percentage_beer_drinkers=0.8,
            amount_of_alumni=10,
            alumni_paying=True,
            alumni_discount=1,
            net_result=-300,
        ),
        # Params(
        #     beer_per_person=10,
        #     percentage_beer_drinkers=0.8,
        #     amount_of_alumni=10,
        #     alumni_paying=True,
        #     alumni_discount=0.2,
        #     net_result=-300,
        # ),
    ]

    sims = [
        Simulator(
            params=param,
            venue=venue,
        )
        for venue in venues
        for param in params
    ]

    for sim in sims:
        print(sim.gen_output())
        print("=" * 60)

    write_output(sims)
