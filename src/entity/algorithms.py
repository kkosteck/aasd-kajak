import time
from abc import ABC, abstractmethod
import threading
import time

from src.agents.crossroad_handler import LightState


class Algorithm(ABC):
    def __init__(self, timeout: float):
        self._timers_timeout = timeout
        self._high_priority_states = []
        self._state_timers = {
            state: threading.Timer(
                self._timers_timeout,
                lambda: self._high_priority_states.append(state))
            for state in LightState.__dict__.keys()
        }
        for t in self._state_timers.values():
            t.start()

    def recommend_state(self, **kwargs):
        if 'current_state' in kwargs:
            if kwargs['current_state'] in self._high_priority_states:
                self._high_priority_states.remove(kwargs['current_state'])
            self._reset_timer(kwargs['current_state'])

        best_state = self._process_data(**kwargs)

        if best_state in self._high_priority_states:
            self._high_priority_states.remove(best_state)
        self._reset_timer(best_state)
        return best_state

    @abstractmethod
    def _process_data(self, **kwargs):
        raise NotImplementedError

    def _reset_timer(self, state: str):
        self._state_timers[state].cancel()
        self._state_timers[state] = threading.Timer(self._timers_timeout,
                                                    lambda: self._high_priority_states.append(state))
        self._state_timers[state].start()


class LargestFirst(Algorithm):
    def _process_data(self, lines, current_state):
        if self._high_priority_states:
            return self._high_priority_states[0]
        elif (len(lines['N']) + len(lines['S'])) >= (len(lines['E']) + len(lines['W'])):
            return LightState.NS
        else:
            return LightState.EW


class AverageWait(Algorithm):
    def _process_data(self, lines, current_state):
        if self._high_priority_states:
            return self._high_priority_states[0]

        current_ts = time.time()
        wait_dict = {}
        for line, cars in lines.items():
            if not cars:
                wait_dict[line] = 0
            else:
                wait_dict[line] = sum([current_ts - car['create_timestamp'] for car in cars]) / len(cars)

        if ((wait_dict['N'] + wait_dict['S'])/2) >= ((wait_dict['W'] + wait_dict['E'])/2):
            return LightState.NS
        else:
            return LightState.EW


class WeightedSum(Algorithm):
    def _process_data(self, lines, current_state):
        if self._high_priority_states:
            return self._high_priority_states[0]

        current_ts = time.time()
        wait_dict = {}
        for line, cars in lines.items():
            if not cars:
                wait_dict[line] = 0
            else:
                wait_dict[line] = sum([current_ts - car['create_timestamp'] for car in cars]) / len(cars)

        if (wait_dict['N']*len(lines['N']) + wait_dict['S']*len(lines['S'])) >= \
                (wait_dict['W']*len(lines['W']) + wait_dict['E']*len(lines['E'])):
            return LightState.NS
        else:
            return LightState.EW



