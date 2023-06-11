"""

These are mainly data holding classes

"""

file_path = "../common/goods.txt"
goods_price_dict = dict()
with open(file_path, 'r') as goods_file:
    for line in goods_file:
        s = line.split(',')
        goods_price_dict[s[0]] = int(s[1])


class PopGroup:
    def __init__(self, pop_type: str, amount: float):
        self.pop_type = pop_type
        self.amount = amount
        self.sol = 10
        self.wealth = 10

    def __add__(self, other):
        if self.pop_type != other.pop_type:
            print("Error, pop types need to be the same for addition")
        return PopGroup(self.pop_type, self.amount + other.amount)

    def __str__(self):
        return f"pop_type: {self.pop_type}, amount: {self.amount:.0f}"


class MarketGood:
    def __init__(self, supply: float, demand: float):
        self.supply = supply
        self.demand = demand

    def __add__(self, other):
        return MarketGood(self.supply + other.supply, self.demand + other.demand)

    def __str__(self):
        return f"supply: {self.supply:.2f}, demand: {self.demand:.2f}"

    def price_mult(self) -> float:  # only useful for a total market
        if self.supply == 0:
            return False
        # elif self.supply < 0:     # should never be smaller than 0
        #     return False

        max_price_mult = 10
        min_price_mult = 1 / max_price_mult

        ans = self.demand / self.supply
        if ans >= max_price_mult:
            return max_price_mult
        elif ans <= min_price_mult:
            return min_price_mult
        else:
            return ans


class Building:
    def __init__(self,
                 name: str,
                 color: tuple[int, int, int],
                 level: int = 1,
                 market_dict: dict[str, MarketGood] = None,
                 pop_list: list[PopGroup] = None):

        self.name = name
        self.color = color
        self.level = level
        self.market_dict = market_dict if market_dict else dict()
        self.pop_list = pop_list if pop_list else []
        self.cash_reserve = 0

    def __str__(self):
        return f"{self.market_dict}"

    def add_level(self):
        for market_good in self.market_dict.values():
            market_good.supply *= (self.level + 1) / self.level
            market_good.demand *= (self.level + 1) / self.level
        self.level += 1

    def next_turn(self, tmd: dict[str, MarketGood]):
        cash_flow = 0
        for key, value in self.market_dict.items():
            good_price = goods_price_dict[key] * tmd[key].price_mult()
            if value.supply:
                cash_flow += value.supply * good_price
            if value.demand:
                cash_flow -= value.demand * good_price
        print(cash_flow)
        self.cash_reserve += cash_flow
