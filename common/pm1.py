
import csv
import json
import os


my_cats = ['01_industry', '02_agro', '03_mines', '04_plantations', '06_urban_center',
           '09_misc_resource', '11_private_infrastructure']


class Goods:
    def __init__(self):
        self.dict = read_v3_file(r"goods\00_goods.txt")

    def cost(self, name) -> int:
        return int(self.dict[name]["cost"])


class ProductionMethods:
    def __init__(self, cats: list[str, ...], era: int = 3):
        self.cats = cats
        self.era = era

        self.goods = Goods()

        self.dict = {}
        for cat in cats:
            pm_file_name = r"production_methods\\" + cat + ".txt"
            self.dict.update(read_v3_file(pm_file_name))

        self.techs = unlocked_technologies(era)
        self.ans = []

    def unlocked(self, name: str):
        pm = self.dict[name]
        if "unlocking_technologies" not in pm:
            return True
        if not pm["unlocking_technologies"]:
            return True
        return pm["unlocking_technologies"][0] in self.techs

    def parse(self, name: str) -> tuple[int, int] | None:
        pm = self.dict[name]
        net = 0
        employment = 0

        if "building_modifiers" not in pm:
            return net, employment

        if "level_scaled" in pm["building_modifiers"]:
            employment = sum(int(i) for i in pm["building_modifiers"]["level_scaled"].values())

        if "workforce_scaled" not in pm["building_modifiers"]:
            return net, employment

        for order, amount in pm["building_modifiers"]["workforce_scaled"].items():
            parts = order.split("_")
            if len(parts) == 5:
                parts[2] += "_" + parts[3]

            if parts[1] == "output":
                sign = 1
            elif parts[1] == "input":
                sign = -1
            else:
                sign = 0
                print("This shouldn't happen")

            net += sign * self.goods.cost(parts[2]) * float(amount)

        return net, employment

    def parse_all(self):
        for name in self.dict.keys():
            temp = self.parse(name)
            if temp:
                self.ans.append((*temp, name[3:]))

    def print_ans_sorted(self):
        if not self.ans:
            self.parse_all()
        self.ans.sort(reverse=True)
        for i in self.ans:
            print(*i)


class Buildings:
    def __init__(self, cats: list[str, ...], era: int = 3):
        self.cats = cats
        self.era = era

        self.dict = {}
        self.pmgs_dict = {}

        for cat in cats:
            building_file_name = r"buildings\\" + cat + ".txt"
            pmg_file_name = r"production_method_groups\\" + cat + ".txt"

            self.dict.update(read_v3_file(building_file_name))
            self.pmgs_dict.update(read_v3_file(pmg_file_name))

        self.pms = ProductionMethods(cats, era)

        self.building_name = ""
        self.building_pmgs = []
        self.n_pmgs = 0
        self.ans = []

    def recursive(self, net: int = 0, employment: int = 0, used_pms: tuple = ()):
        len_used_pms = len(used_pms)
        if len_used_pms >= self.n_pmgs:
            if employment == 0:
                employment = 850
                print(f"{self.building_name} has no employees. ")
            self.ans.append((net / employment, int(net), employment, self.building_name, *used_pms))
            return

        next_pmg = self.building_pmgs[len_used_pms]
        for pm_name in self.pmgs_dict[next_pmg]["production_methods"]:
            if not self.pms.unlocked(pm_name):
                continue
            dn, de = self.pms.parse(pm_name)
            self.recursive(net + dn, employment + de, used_pms + (pm_name[3:],))

    def print_ans(self):
        if not self.ans:
            self.test_all()
        self.ans.sort(reverse=True)
        for eff, *rest in self.ans:     # net, employment, building_name, used_pms
            print(f"{eff * 100:.0f}", *rest, sep='\t')

    def export_ans(self):
        if not self.ans:
            self.test_all()
        self.ans.sort(reverse=True)

        file_path = r"D:\Python\PycharmProjects\vic3\data"
        os.chdir(file_path)
        csv_file_name = "output.csv"

        with open(csv_file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.ans)

    def test_all(self):
        for key, value in self.dict.items():
            self.building_name = key[9:]
            self.building_pmgs = value["production_method_groups"]
            self.n_pmgs = max(len(self.building_pmgs) - 1, 1)
            self.recursive()


def read_v3_file(rel_file_path: str):
    os.chdir(r"D:\SteamLibrary\steamapps\common\Victoria 3\game\common")   # D:\Python\PycharmProjects\vic3\common

    processed_data = ["{"]

    with open(rel_file_path, 'r', encoding='utf-8-sig') as file:
        for line in file:
            parse_line(line.strip(), processed_data)

        processed_data.append("}")
        processed_data = "\n".join(processed_data)
        # for i, line in enumerate(processed_data.split("\n")):
        #     print(i, line)
        return json.loads(processed_data)


def parse_line(line: str, processed_data: list) -> None:

    add = processed_data.append
    todo = ""

    if '#' in line:  # remove comments
        line = line.split('#')[0].strip()

    if not line:  # blank line
        return

    if '>=' in line:
        # print('>=')
        line = line.replace('>=', '=')
    elif '>' in line:
        # print('>')
        line = line.replace('>', '=')
    elif '<' in line:
        # print('<')
        line = line.replace('<', '=')

    if '=' in line:
        key, value = line.split(" = ", maxsplit=1)

        if value == '{':
            add(f'"{key}": {{')
        elif value[0] == '{':
            add(f'"{key}": {{')
            todo = value[1:-1].strip()
        elif value.startswith('"') and value.endswith('"'):
            add(f'"{key}": {value},')
        else:
            add(f'"{key}": "{value}",')

        if any(char in processed_data[-2] for char in ['}', ']']):
            processed_data[-2] += ','

        if todo:
            parse_line(todo, processed_data)
            parse_line("}", processed_data)

    elif '}' in line:
        processed_data[-1] = processed_data[-1].replace(',', '')

        if any(char in processed_data[-1] for char in [':', '}', ']']):
            add('}')
        else:
            add(']')

    else:
        add(f'"{line}",')
        if processed_data:
            processed_data[-2] = processed_data[-2].replace('{', '[')

        # if any(char in processed_data[-2] for char in ['}', ']']):
        #     processed_data[-2] += ','


def unlocked_technologies(era: int = 3) -> set:
    tech_dict = read_v3_file(r"technology\technologies\10_production.txt")
    return {key for key, value in tech_dict.items() if int(value["era"][4]) <= era}


def main() -> None:
    # ProductionMethods().print_ans_sorted()
    Buildings(my_cats, era=4).export_ans()


if __name__ == "__main__":
    main()

