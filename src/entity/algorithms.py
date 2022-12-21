import time
from abc import ABC, abstractmethod
import threading

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


class SimpleAlgorithm(Algorithm):
    def _process_data(self, lines, current_state):
        if self._high_priority_states:
            return self._high_priority_states[0]
        elif (len(lines['N']) + len(lines['S'])) >= (len(lines['E']) + len(lines['W'])):
            return LightState.NS
        else:
            return LightState.EW


# if __name__ == '__main__':
#     lines = {'N': [], 'S': [], 'W': [], 'E': []}
#     current_state = 'NS'
#     sa = SimpleAlgorithm(timeout=10)
#     print(sa._high_priority_states)
#     time.sleep(5)
#     print(f'recommended: {sa.recommend_state(lines=lines)}')
#     print(sa._high_priority_states)
#     time.sleep(5)
#     print(sa._high_priority_states)
#     time.sleep(5)
#     print(f'recommended: {sa.recommend_state(lines=lines)}')
#     print(sa._high_priority_states)
