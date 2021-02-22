from typing import Generator
import random
import simpy


class Carwash:
    """A carwash has a limited number of machines to clean cars in parallel.

    Cars have to request one of the machines. When they got one, they
    can start the washing processes and wait for it to finish (which takes ``washtime`` minutes).

    """
    def __init__(self, env: simpy.Environment, num_machines: int, washtime: float):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.washtime = washtime

    def wash(self, car: str) -> Generator:
        """The washing processes.

        It takes a ``car`` processes and tries to clean it.

        """
        yield self.env.timeout(self.washtime)
        print(f"Carwash removed {random.randint(50, 99)}% of {car} dirt")


def main():
    # Setup and start the simulation
    print("*** Carwash ***")
    random.seed(42)
    num_machines = 2    # Number of machines in the carwash
    washtime = 5        # Minutes it takes to clean a car
    t_inter = 7         # Create a car every ~7 minutes
    sim_time = 20       # Simulation time in minutes

    # Create an environment and start the setup process
    env = simpy.Environment()
    env.process(setup(env, num_machines, washtime, t_inter))

    # Execute
    env.run(until=sim_time)

    return 0


def setup(env: simpy.Environment, num_machines: int, washtime: float, t_inter: int) -> Generator:
    """Create a carwash, a number of initial cars and keep creating cars approx. every ``t_inter`` minutes."""
    # Create the carwash
    carwash = Carwash(env, num_machines, washtime)

    # Create 4 initial cars
    i = 0
    while i < 4:
        env.process(car(env, f"Car #{i + 1}", carwash))
        i += 1

    # Create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        i += 1
        env.process(car(env, f"Car #{i + 1}", carwash))


def car(env: simpy.Environment, name: str, cw: Carwash) -> Generator:
    """The car process (each car has a ``name``) arrives at the carwash (``cw``) and requests a cleaning machine.

    It then starts the washing process, waits for it to finish and
    leaves to never come back ...

    """
    print(f"{name} arrives at the carwash at {env.now:.2f}")
    with cw.machine.request() as req:
        yield req

        print(f"{name} enters the carwash at {env.now:.2f}")
        yield env.process(cw.wash(name))

        print(f"{name} leaves the carwash at {env.now:.2f}")


if __name__ == '__main__':
    main()
