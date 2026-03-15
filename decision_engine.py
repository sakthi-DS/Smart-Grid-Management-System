from simulator.grid_network import create_grid, route_power

# battery storage level
battery_storage = 0

# maximum battery capacity
BATTERY_MAX = 300


def take_action(status, value):

    global battery_storage

    grid = create_grid()

    if status == "SURPLUS":

        print("\nGrid has surplus power")

        charge = min(value, BATTERY_MAX - battery_storage)

        battery_storage += charge

        print("AI Action:")
        print("• Storing energy in battery")

        print("Battery charged:", charge, "MW")
        print("Battery level:", battery_storage, "MW")

    elif status == "DEFICIT":

        print("\n⚠ Grid deficit detected:", value, "MW")

        if battery_storage >= value:

            battery_storage -= value

            print("\nAI Action:")
            print("• Using battery storage")

            print("Battery supplied:", value, "MW")
            print("Battery remaining:", battery_storage, "MW")

        else:

            print("\nBattery not sufficient")

            routed = route_power(grid, "Plant", "Area1", value)

            if routed:

                print("\nAI Action:")
                print("• Rerouting power through grid")

            else:

                print("\nAI Action:")
                print("• Reducing EV charging")

    else:

        print("\nGrid operating normally")