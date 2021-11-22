from flask import Flask, jsonify, request
import requests
import sys
import time
import random
import concurrent.futures

ORDER_ID = 1
number_of_tables = 5
number_of_waiters = 3
tables = []
waiters = []
orders_to_be_served = []
SERVED_ORDERS = []
TIME_UNIT = 20


class Waiter:
    def __init__(self, ident):
        self.wait_time = None
        self.order = None
        self.orders = []
        self.ident = ident

    def pick_order(self):
        # for i in range(0, len(tables), self.ident + 1):
        for table in tables:
            if table.state == 1:  # tables[i].state
                self.order = table.generate_order(self.ident)  # tables[i].generate
                self.wait_time = random.randint(1, 4)
                self.orders.append(self.order)
                time.sleep(self.wait_time)
                self.send_order()
                # break

    def send_order(self):
        res = requests.post('http://172.17.0.2:8080/get_order', json=self.order)


class Table:
    def __init__(self, identification):
        self.state = 1
        self.id = identification

    def change_state(self):
        if self.state < 3:
            self.state += 1
        elif self.state == 3:
            self.state = 1

    def generate_order(self, ident):
        seed_value = random.randrange(sys.maxsize)
        random.seed(seed_value)
        max_wait_time = 0
        items = []

        for _ in range(random.randint(1, 5)):
            items.append(random.randint(1, 10))
            for item in items:
                if max_wait_time < foods[item]["preparation-time"]:
                    max_wait_time = foods[item]["preparation-time"]

        order = dict()
        global ORDER_ID
        order["id"] = ORDER_ID
        order["items"] = items
        order["priority"] = random.randint(1, 5)
        order["max_wait"] = max_wait_time * 1.3
        order["table_id"] = self.id
        order["waiter_id"] = ident
        ORDER_ID += 1

        self.change_state()
        return order


for i in range(number_of_tables):
    t = Table(i)
    tables.append(t)

for j in range(number_of_waiters):
    w = Waiter(j)
    waiters.append(w)

foods = [{"id": 1, "name": "pizza", "preparation-time": 20, "complexity": 2, "cooking-apparatus": "oven"},
         {"id": 2, "name": "salad", "preparation-time": 10, "complexity": 1, "cooking-apparatus": None},
         {"id": 3, "name": "zeama", "preparation-time": 7, "complexity": 1, "cooking-apparatus": "stove"},
         {"id": 4, "name": "Scallop", "preparation-time": 32, "complexity": 3, "cooking-apparatus": None},
         {"id": 5, "name": "Island Duck", "preparation-time": 35, "complexity": 3, "cooking-apparatus": "oven"},
         {"id": 6, "name": "Waffles", "preparation-time": 10, "complexity": 1, "cooking-apparatus": "stove"},
         {"id": 7, "name": "Aubergine", "preparation-time": 20, "complexity": 2, "cooking-apparatus": None},
         {"id": 8, "name": "Lasagna", "preparation-time": 30, "complexity": 2, "cooking-apparatus": "oven"},
         {"id": 9, "name": "Burger", "preparation-time": 15, "complexity": 1, "cooking-apparatus": "oven"},
         {"id": 10, "name": "Gyros", "preparation-time": 15, "complexity": 1, "cooking-apparatus": None}]


def start(waiter):
    waiter.pick_order()
    return "ok"


app = Flask(__name__)


@app.route('/start')
def start_hall_simulation():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            results = [executor.submit(start, waiter) for waiter in waiters]
            for f in concurrent.futures.as_completed(results):
                pass


@app.route('/serve_order', methods=["POST", "GET"])
def serve_order():
    if request.method == "POST":
        input_json = request.get_json(force=True)
        delivered_time = time.time()
        input_json["time"] = (delivered_time - input_json["time"]) * TIME_UNIT
        SERVED_ORDERS.append(input_json)
        for table in tables:
            SERVED_ORDERS.append(table.state)
            if table.id == input_json["table_id"]:
                table.change_state()
                table.change_state()
        return jsonify(SERVED_ORDERS)
    else:
        return jsonify(SERVED_ORDERS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
