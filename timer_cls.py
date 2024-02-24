from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from typing import Union, TypeAlias, Any
import warnings

# Type aliases
TimerIndex: TypeAlias = int
TimerName: TypeAlias = str


def warning_message(message: str, arguments: list = None, print_only: bool = False, warning_type: type = RuntimeWarning):
    count = 1
    if arguments:
        if isinstance(arguments, str):
            arguments = [arguments]
        for argument in arguments:
            message = message.replace("#" + str(count), f'"\033[31m{argument}\033[33m"')
            count += 1

    text = f"\n\033[34mWarning: \033[33m{message}\033[0m"
    if print_only:
        print(text.strip())
    else:
        warnings.warn(text, warning_type)


class AbstractTimer:
    def __init__(self,
                 parent,
                 name: str,
                 interval: int,
                 duration: int,
                 delay: int = 0,
                 single_shot: bool = True,
                 function_on_finished: callable = None,
                 function_on_timeout: callable = None,
                 data: Any = None
                 ):
        
        if not isinstance(parent, TimerHandler):
            warning_message("Parent must be TimerHandler not '#1'", type(parent), print_only=True)
            raise ValueError("Parent must be TimerHandler")

        self._parent: TimerHandler = parent
        self.name = name
        self.data = data
        self.function_on_finished = function_on_finished
        self.function_on_timeout = function_on_timeout
        
        if delay is None:
            self._delay = 0
        else:
            self._delay = delay

        if interval:
            self._interval = interval
        else:
            warning_message("Interval must be specified. Cannot be '#1", interval, print_only=True)
            raise ValueError("Interval must be specified.")
        
        if duration:
            self._duration = duration
        else:
            warning_message("Duration must be specified. Cannot be '#1", duration, print_only=True)
            raise ValueError("Duration must be specified.")
        
        if self._interval > self._duration:
            warning_message("Interval must be less or equal than duration. Interval (#1) > Duration (#2)", [self._interval, self._duration], print_only=True)
            warning_message("Interval set to Duration")
            self._interval = self._duration

        self._single_shot = single_shot
        self.index = None
        self.__tick_state = 0

        self.__start_tick_state: int = None
        self.__stop_tick_state: int = None
        self.__end_tick_state: int = None
        self.__count_ticks = 0

        self.__active = False

    def start(self):
        self._init_tick_states()
        self.__active = True

    def stop(self):
        self.__active = False

    def get_tick_state(self):
        return self.__tick_state
    
    def get_count_ticks(self):
        return self.__count_ticks
    
    def is_active(self):
        return self.__active
    
    def get_interval(self):
        return self._interval
    
    def set_interval(self, value: int):
        if self._single_shot:
            warning_message("Cannot set interval for single shot timer. Only continuous timers can have an interval.", print_only=True)
            warning_message("Interval not set !")
            return
        if value > self._duration:
            warning_message("Interval must be less or equal than duration. Interval (#1) > Duration (#2)", [value, self._duration], print_only=True)
            warning_message("Interval not set !")
            return
        self._interval = value
        self._check_for_timeout()

    def get_duration(self):
        return self._duration
    
    def set_duration(self, value: int):
        self._duration = value
        self._check_for_timeout()

    def get_delay(self):
        return self._delay
    
    def set_delay(self, value: int):
        self._delay = value
        self._check_for_timeout()

    def is_single_shot(self):
        return self._single_shot
    
    def get_interval_remaining_time(self):
        return self.__stop_tick_state - self.__tick_state
    
    def get_total_remaining_time(self):
        return self.__end_tick_state - self.__tick_state
    
    def get_elapsed_time(self):
        return self.__tick_state - self.__start_tick_state

    def _set_tick_state(self, value: int):
        self.__tick_state = value
        self.__count_ticks += 1
        self._check_for_timeout()

    def _check_for_timeout(self):
        if not self.__active:
            return
        
        if self._single_shot:
            if self.__tick_state >= self.__end_tick_state:
                self._parent._child_timer_finished(self)
                self.__active = False
        else:
            if self.__tick_state >= self.__stop_tick_state:
                self._parent._child_timer_timeout(self)
                if self.__tick_state >= self.__end_tick_state:
                    self._parent._child_timer_finished(self)
                    self.__active = False

    def _init_tick_states(self):
        self.__count_ticks = 0
        self.__start_tick_state = self._parent.tick_state()
        self.__stop_tick_state = self.__start_tick_state + self._interval + self._delay
        self.__end_tick_state = self.__start_tick_state + self._duration + self._delay


class ContinuousTimer(AbstractTimer):
    def __init__(self, parent: 'TimerHandler', name: str = None, interval: int = None, duration: int = None, delay: int = None, function_on_finished: callable = None, function_on_timeout: callable = None, data: Any = None):
        
        super().__init__(parent=parent,
                         name=name,
                         interval=interval,
                         duration=duration,
                         delay=delay,
                         single_shot=False,
                         function_on_finished=function_on_finished,
                         function_on_timeout=function_on_timeout,
                         data=data
                         )


class SingleShotTimer(AbstractTimer):
    def __init__(self, parent: 'TimerHandler', name: str = None, duration: int = None, delay: int = None, function_on_finished: callable = None, data: Any = None):

        super().__init__(parent=parent,
                         name=name,
                         interval=duration,
                         duration=duration,
                         delay=delay,
                         single_shot=True,
                         function_on_finished=function_on_finished,
                         function_on_timeout=None,
                         data=data
                         )


class TimerHandler(QObject):
    signalTimerTimeOut = pyqtSignal(AbstractTimer)
    signalTimerFinished = pyqtSignal(AbstractTimer)

    def __init__(self, parent: QWidget = None, interval: int = 50, auto_start: bool = True):
        super().__init__(parent)

        self.interval = interval

        self.__timer = None
        self.__tick_state = 0

        self.__timers = []

        if auto_start:
            self.start()

    def _child_timer_finished(self, timer: Union[ContinuousTimer, SingleShotTimer]):
        if timer.function_on_finished:
            timer.function_on_finished(timer=timer)
        
        self.signalTimerFinished.emit(timer)

    def _child_timer_timeout(self, timer: Union[ContinuousTimer, SingleShotTimer]):
        if timer.function_on_timeout:
            timer.function_on_timeout(timer=timer)
        
        self.signalTimerTimeOut.emit(timer)

    def add_timer(self, timer: Union[ContinuousTimer, SingleShotTimer, dict], auto_start: bool = False) -> Union[ContinuousTimer, SingleShotTimer, None]:
        if isinstance(timer, ContinuousTimer) or isinstance(timer, SingleShotTimer):
            index = len(self.__timers)
            timer.index = index
            if auto_start:
                timer.start()
            self.__timers.append(timer)

        if isinstance(timer, dict):
            timer = self._create_timer_from_dict(timer)
            if not timer:
                warning_message("Timer not added.", print_only=True)
                return None

    def remove_timer(self, timer: Union[ContinuousTimer, SingleShotTimer, TimerIndex, TimerName]) -> Union[ContinuousTimer, SingleShotTimer, None]:
        index = self._find_timer_index(timer)
        if index is None:
            return None
        
        timer = self.__timers.pop(index)
        timer.stop()

        return timer

    def find_timer(self, timer: Union[ContinuousTimer, SingleShotTimer, TimerIndex, TimerName]) -> Union[ContinuousTimer, SingleShotTimer, None]:
        index = self._find_timer_index(timer)
        if index is None:
            return None
        
        return self.__timers[index]

    def count_timers(self):
        return len(self.__timers)
    
    def stop_all_timers(self):
        for timer in self.__timers:
            timer.stop()
    
    def start_all_timers(self):
        for timer in self.__timers:
            timer.start()

    def get_all_timers(self) -> list:
        return self.__timers

    def remove_all_timers(self):
        for timer in self.__timers:
            timer.stop()
        
        self.__timers = []

    def _find_timer_index(self, timer: Union[ContinuousTimer, SingleShotTimer, TimerIndex, TimerName]) -> int:
        if isinstance(timer, TimerIndex):
            if timer >= 0 and timer < len(self.__timers):
                return timer
            else:
                return None
            
        if isinstance(timer, TimerName):
            for i in range(len(self.__timers)):
                if self.__timers[i].name == timer:
                    return i
            
            return None
        
        if isinstance(timer, ContinuousTimer) or isinstance(timer, SingleShotTimer):
            for i in range(len(self.__timers)):
                if self.__timers[i] == timer:
                    return i
            
            return None
        
        return None

    def _create_timer_from_dict(self, timer_dict: dict) -> Union[ContinuousTimer, SingleShotTimer, None]:
        if timer_dict.get("type") == "continuous" or timer_dict.get("single_shot") is False:
            timer = ContinuousTimer(parent=self, name=timer_dict.get("name"), interval=timer_dict.get("interval"))
        elif timer_dict.get("type") == "single_shot" or timer_dict.get("single_shot") is True:
            timer = SingleShotTimer(parent=self, name=timer_dict.get("name"), duration=timer_dict.get("duration"))
        else:
            warning_message("Unable to create timer from dict:\n#1", str(timer_dict), print_only=True)
            return None
        
        return timer

    def start(self):
        if self.__timer:
            self.__timer.stop()
            self.__timer.deleteLater()
            self.__tick_state = 0

        self.__timer = QTimer()
        self.__timer.setInterval(self.interval)
        self.__timer.timeout.connect(self._timer_timeout)
        self.__timer.start()

    def stop(self):
        if self.__timer:
            self.__timer.stop()
            self.__timer.deleteLater()
            self.__tick_state = 0
            self.__timer = None

    def tick_state(self):
        return self.__tick_state
    
    def _timer_timeout(self):
        self.__tick_state += self.interval
        for timer in self.__timers:
            timer._set_tick_state(self.__tick_state)




