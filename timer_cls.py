from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from typing import Union, TypeAlias, Any

import UTILS


# Type aliases
TimerIndex: TypeAlias = int
TimerName: TypeAlias = str


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
                 data: Any = None,
                 standalone: bool = False
                 ):
        
        if not isinstance(parent, TimerHandler):
            UTILS.TerminalUtility.WarningMessage("Parent must be TimerHandler not #1", type(parent), exception_raised=True)
            raise ValueError("Parent must be TimerHandler")

        self._parent: TimerHandler = parent
        self._standalone = standalone
        self.name = name
        self.data = data
        self.function_on_finished = function_on_finished
        self.function_on_timeout = function_on_timeout
        
        if delay is None:
            self._delay = 0
        else:
            self._delay = delay

        if single_shot:
            if interval:
                UTILS.TerminalUtility.WarningMessage("Interval cannot be specified for SingleShot timer. Interval is ignored")
            self._interval = 0
        else:
            if interval:
                self._interval = interval
            else:
                UTILS.TerminalUtility.WarningMessage("Interval must be specified for Continuous timer. Cannot be #1", interval, exception_raised=True)
                raise ValueError("Interval must be specified.")
        
        if single_shot:
            if duration:
                self._duration = duration
            else:
                UTILS.TerminalUtility.WarningMessage("Duration must be specified. Cannot be #1", duration)
                raise ValueError("Duration must be specified.")
        else:
            if duration:
                self._duration = duration
            else:
                self._duration = float("inf")
            
        if not single_shot and self._interval > self._duration:
            UTILS.TerminalUtility.WarningMessage("Interval must be less or equal than duration. Interval (#1) > Duration (#2)\nInterval set to Duration", [self._interval, self._duration])
            self._interval = self._duration

        self._single_shot = single_shot
        if self._standalone:
            self.index = 0
        else:
            self.index = None
        self.__tick_state = 0

        self.__start_tick_state: int = None
        self.__stop_tick_state: int = None
        self.__end_tick_state: int = None
        self.__count_ticks = 0

        self.__active = False

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def start(self) -> bool:
        if not self.can_be_started():
            UTILS.TerminalUtility.WarningMessage("Timer cannot be started. #1", "Configuration error")
            return False
        
        if self._standalone and not self._parent.is_running():
            self._parent.start()

        self._init_tick_states()
        self.__active = True

        return self.__active

    def can_be_started(self) -> bool:
        if self._single_shot:
            if self._interval:
                UTILS.TerminalUtility.WarningMessage("Cannot set interval for single shot timer. Only continuous timers can have an interval.\nInterval set to #1", "0")
                self._interval = 0

            if not self._duration:
                UTILS.TerminalUtility.WarningMessage("Duration must be specified. Cannot be #1", self._duration)
                return False
        else:
            if not self._interval:
                UTILS.TerminalUtility.WarningMessage("Interval must be specified for Continuous timer. Cannot be #1", self._interval)
                return False
            
            if not self._duration:
                UTILS.TerminalUtility.WarningMessage("Duration cannot be #1\nDuration set to #2", [self._duration, "Infinity"])
                self._duration = float("inf")

            if self._interval > self._duration:
                UTILS.TerminalUtility.WarningMessage("Interval must be less or equal than duration. Interval (#1) > Duration (#2)\nInterval set to Duration", [self._interval, self._duration])
                self._interval = self._duration
        
        return True                

    def stop(self):
        self.__active = False

    def get_tick_state(self):
        return self.__tick_state
    
    def get_count_ticks(self):
        return self.__count_ticks
    
    def is_active(self):
        return self.__active

    def is_standalone(self):
        return self._standalone

    def get_interval(self):
        return self._interval
    
    def set_interval(self, value: int) -> bool:
        if value is None:
            return False
        
        if self._single_shot:
            UTILS.TerminalUtility.WarningMessage("Cannot set interval for single shot timer. Only continuous timers can have an interval.\nInterval not set !")
            return False
        if value > self._duration:
            UTILS.TerminalUtility.WarningMessage("Interval must be less or equal than duration. Interval (#1) > Duration (#2)\nInterval not set !", [value, self._duration])
            return False
        self._interval = value
        self._check_for_timeout()

        return True

    def get_duration(self):
        return self._duration
    
    def set_duration(self, value: int) -> bool:
        if value is None:
            value = float("inf")
        
        if not self._single_shot and value < self._interval:
            UTILS.TerminalUtility.WarningMessage("Duration must be greater or equal than interval. Duration (#1) < Interval (#2)\nDuration not set !", [value, self._interval])
            return False

        self._duration = value
        self._check_for_timeout()

        return True

    def get_delay(self):
        return self._delay
    
    def set_delay(self, value: int) -> bool:
        if value is None:
            return False
        
        self._delay = value
        self._check_for_timeout()

        return True

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
                self.__stop_tick_state += self._interval
                if self.__tick_state >= self.__end_tick_state:
                    self._parent._child_timer_finished(self)
                    self.__active = False

    def _init_tick_states(self):
        self.__count_ticks = 0
        self.__start_tick_state = self._parent.tick_state()
        self.__tick_state = self.__start_tick_state
        self.__stop_tick_state = self.__start_tick_state + self._interval + self._delay
        self.__end_tick_state = self.__start_tick_state + self._duration + self._delay

    def close_me(self):
        if self._standalone:
            # self._parent.stop()
            # self._parent.remove_timer(self)
            self._parent.close_me()
        else:
            self._parent.remove_timer(self)


class ContinuousTimer(AbstractTimer):
    def __init__(self, parent: 'TimerHandler' = None, name: str = None, interval: int = None, duration: int = None, delay: int = None, function_on_finished: callable = None, function_on_timeout: callable = None, data: Any = None):

        if isinstance(parent, TimerHandler):
            standalone = False
        else:
            parent = TimerHandler(None, auto_start=False)
            standalone = True

        if not duration:
            # Set duration to infinite
            duration = float('inf')

        super().__init__(parent=parent,
                         name=name,
                         interval=interval,
                         duration=duration,
                         delay=delay,
                         single_shot=False,
                         function_on_finished=function_on_finished,
                         function_on_timeout=function_on_timeout,
                         data=data,
                         standalone=standalone
                         )

        if standalone:
            parent._force_add_timer(self)

    def start(self, interval: int = None, duration: int = None, delay: int = None) -> bool:
        if interval is not None:
            result = self.set_interval(interval)
            if not result:
                UTILS.TerminalUtility.WarningMessage("Unable to start timer. Interval not set !")
                return False
        
        if duration is not None:
            result = self.set_duration(duration)
            if not result:
                UTILS.TerminalUtility.WarningMessage("Unable to start timer. Duration not set !")
                return False

        if delay is not None:
            result = self.set_delay(delay)
            if not result:
                UTILS.TerminalUtility.WarningMessage("Unable to start timer. Delay not set !")
                return False

        return super().start()
        


class SingleShotTimer(AbstractTimer):
    def __init__(self, parent: 'TimerHandler' = None, name: str = None, duration: int = None, delay: int = None, function_on_finished: callable = None, data: Any = None):

        if isinstance(parent, TimerHandler):
            standalone = False
        else:
            parent = TimerHandler(None, auto_start=False)
            standalone = True

        super().__init__(parent=parent,
                         name=name,
                         interval=0,
                         duration=duration,
                         delay=delay,
                         single_shot=True,
                         function_on_finished=function_on_finished,
                         function_on_timeout=None,
                         data=data,
                         standalone=standalone
                         )
        
        if standalone:
            parent._force_add_timer(self)

    def start(self, duration: int = None, delay: int = None) -> bool:
        if duration is not None:
            result = self.set_duration(duration)
            if not result:
                UTILS.TerminalUtility.WarningMessage("Unable to start timer. Duration not set !")
                return False
        
        if delay is not None:
            result = self.set_delay(delay)
            if not result:
                UTILS.TerminalUtility.WarningMessage("Unable to start timer. Delay not set !")
                return False

        return super().start()


class TimerHandler(QObject):
    signalTimerTimeOut = pyqtSignal(AbstractTimer)
    signalTimerFinished = pyqtSignal(AbstractTimer)

    def __init__(self, parent: QWidget = None, interval: int = 25, auto_start: bool = True):
        super().__init__(parent)

        self.interval = interval

        self.__timer = None
        self.__tick_state = 0
        self._parent = parent

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

    def _force_add_timer(self, timer: Union[ContinuousTimer, SingleShotTimer]):
        if isinstance(timer, ContinuousTimer) or isinstance(timer, SingleShotTimer):
            self.__timers.append(timer)
        else:
            UTILS.TerminalUtility.WarningMessage("Timer must be of type ContinuousTimer or SingleShotTimer.\ntype(timer) = #1\ntimer = #2", [type(timer), timer], exception_raised=True)
            raise ValueError("Timer must be of type ContinuousTimer or SingleShotTimer.")
        
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
                UTILS.TerminalUtility.WarningMessage("Timer not added.\nFunction: #1\ntimer = #2", ["add_timer", timer])
                return None
        
        return timer

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
        self.stop_all_timers()
        
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
            UTILS.TerminalUtility.WarningMessage("Unable to create timer from dict:\n#1", str(timer_dict))
            return None
        
        return timer

    def start(self):
        if isinstance(self.__timer, QTimer):
            self.__timer.stop()
            self.__timer.deleteLater()
            self.__tick_state = 0

        self.__timer = QTimer()
        self.__timer.setInterval(self.interval)
        self.__timer.timeout.connect(self._timer_timeout)
        self.__timer.start()

    def stop(self):
        if isinstance(self.__timer, QTimer):
            self.__timer.stop()
            self.__timer.deleteLater()
            self.__tick_state = 0
        self.__timer = None

    def is_running(self):
        return self.__timer is not None

    def tick_state(self):
        return self.__tick_state
    
    def _timer_timeout(self):
        self.__tick_state += self.interval
        for timer in self.__timers:
            try:
                timer._set_tick_state(self.__tick_state)
            except Exception as e:
                UTILS.LogHandler.add_log_record("#1: Exception in function #2.\nException: #3", ["TimerHandler", "_timer_timeout", str(e)], exception_raised=True)

    def close_me(self):
        self.remove_all_timers()
        try:
            if self.__timer is not None:
                self.__timer.stop()
                self.__timer.deleteLater()
        except Exception as e:
            UTILS.LogHandler.add_log_record("#1: Exception in function #2 method (timer delete).\nException: #3\ntype(self.__timer) = #4\nself__timer = #5", ["TimerHandler", "close_me", str(e), type(self.__timer), self.__timer], exception_raised=True)

        self.__timer = None

        self.deleteLater()
        self.setParent(None)




