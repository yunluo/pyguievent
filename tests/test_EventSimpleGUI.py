import sys
from tests.windom_sim import WinSimulator
from pysimpleevent import EventSimpleGUI
from io import StringIO


class Test:
    """ Testing all features from main code """
    def test_if_event_go_to_list_of_events_using_decor(self):
        loop = EventSimpleGUI()

        @loop.event('test')
        def event_test(*args):
            """ Just a test event """
        assert event_test in loop.get_events

    def test_if_simulated_win_return_event_values_and_close(self):
        loop = EventSimpleGUI()
        win = WinSimulator(event='test', values={})

        @loop.event('test')
        def test_event(*args):
            return True
        result = loop.run_window(win, return_values=True, close_event='test')
        assert result['test_event']

    def test_if_simulated_win_return_event_values_and_close_from_lists(self):
        loop = EventSimpleGUI()
        win = WinSimulator(event='test1', values={})

        @loop.event(['test1', 'test1'])
        def test_event_1(*args):
            return True

        result1 = loop.run_window(win, return_values=True, close_event='test1')
        win.chage_event('test2')
        result2 = loop.run_window(win, return_values=True, close_event='test2')
        assert result1['test_event_1'] and result2['test_event_1']

    def test_if_event_go_to_list_of_events_using_add_event(self):
        loop = EventSimpleGUI()

        def event_test(*args):
            """ Just a test event """
        loop.add_event(event_test)
        assert event_test in loop.get_events

    def test_run_events_as_run_win_args(self):
        loop = EventSimpleGUI()
        win = WinSimulator(event='test', values={})

        def event_test(*args):
            event, values, _ = args
            if event == 'test':
                values[event_test.__name__] = True
        result = loop.run_window(win, event_test, close_event='test')
        assert result['event_test']

    def test_if_loop_run_taks(self):
        loop = EventSimpleGUI()
        win = WinSimulator(event='test', values={})

        string_io = StringIO()
        sys.stdout = string_io

        def test_task(*args):
            print('test')

        loop.run_window(win, close_event='test', task=test_task)

        console_output = string_io.getvalue().strip()
        sys.stdout = sys.__stdout__

        assert console_output == 'test'

    def test_log(self):
        loop = EventSimpleGUI()
        win = WinSimulator(event='test', values={})

        string_io = StringIO()
        sys.stdout = string_io

        loop.run_window(win, close_event='test', window_log=True)

        console_output = string_io.getvalue().strip()
        sys.stdout = sys.__stdout__
        log = 'Event ->   test\nValues ->  {}'

        assert console_output == log

    def test_if_win_can_return_values(self):
        loop = EventSimpleGUI()
        win = WinSimulator(event='test', values={})

        result = loop.run_window(win, return_values=True, close_event='test')

        assert result == {}

    def test_closing_window_insede_a_event_and_if_loop_can_return_a_window(self):
        loop = EventSimpleGUI()
        win = WinSimulator(event='test', values={})

        @loop.event('test')
        def close_event(event, values: dict, window):
            if values:
                window.close()

        result = loop.run_window(win, return_values=True)
        assert result == {'close_event': None, 'Window': win}



