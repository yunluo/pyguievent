# Events For SimpleGui

> Status of project: in progress...


<div align="center">
<img alt="GitHub" src="https://img.shields.io/github/license/MikalROn/EventSimpleGUI?style=for-the-badge"/>
<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/eventsimplegui?style=for-the-badge"/>
<a href="https://github.com/MikalROn/EventSimpleGUI">
<img alt="GitHub" src="https://img.shields.io/badge/Github-Open%20source-green?style=for-the-badge&amp;logo=github"/>
</a>
<a href="https://smokeshow.helpmanual.io/474z2x1c0s2u3j101i26/">
<img alt="Conv100%" src="https://img.shields.io/badge/coverage-100%25-green?style=for-the-badge">
</a>
</div>

<em>This project has the intention to make easier, scalable and readable events on PySimpleGUI</em>

## Download

<p>Download from PyPi</p>

````shell
$pip install EventSimpleGUI
````

## Fast-Start 

<p> Here is a basic window </p>

````python
from pysimpleevent import EventSimpleGUI
import PySimpleGUI as sg

loop = EventSimpleGUI()
win = sg.Window('Win', [[sg.B('click')]])

@loop.event('click')
def simple_event(*args):
    print('click')

if __name__ == '__main__':
    loop.run_window(win)
````
<p>The key that's trigger the event has to be passed as an argument of loop.event()
</p>

## Event Function Arguments
<p> Every event functions will recive 3 arguments (event, values, window) </p>

- <b>Event:</b> is a string that's comes from <em>Window.Read()</em>
- <b>Values:</b> is a dict that's comes from <em>Window.Read()</em> and also contain return of event function(with the name of function)
- <b>Window:</b> is a sg.Window object, same window that's being runned on <em>loop.run_window(window)</em>

## Demonstration

<h3> Creating an event function </h3>

<p>Using the decorator event to run an event, you can pass the element key as an argument for decorator, when the event 
is called, function is going to be called two</p>

````python
from pysimpleevent import EventSimpleGUI
import PySimpleGUI as sg

loop = EventSimpleGUI()


@loop.event('_click')
def when_btn_was_clicked(*ags):
    print('Just a normal event')

layout = [[sg.B('Just a button', key='_click')]]
window = sg.Window('Just a Window.', layout)

if __name__ == '__main__':
    loop.run_window(window)
````
Events can be passed as an argument of run window like in the exemple
````python
from pysimpleevent import EventSimpleGUI
import PySimpleGUI as sg

loop = EventSimpleGUI()



def when_btn_was_clicked(*args):
    event, _, _ = args
    if event == '_click':
        print('Just a normal event')

layout = [[sg.B('Just a button', key='_click')]]
window = sg.Window('Just a Window.', layout)

if __name__ == '__main__':
    loop.run_window(window, when_btn_was_clicked)
````
And can also pass an event using add_event
````python
from pysimpleevent import EventSimpleGUI
import PySimpleGUI as sg

loop = EventSimpleGUI()



def when_btn_was_clicked(*args):
    event, _, _ = args
    if event == '_click':
        print('Just a normal event')

loop.add_event(when_btn_was_clicked)
layout = [[sg.B('Just a button', key='_click')]]
window = sg.Window('Just a Window.', layout)

if __name__ == '__main__':
    loop.run_window(window)
````

## Events

<p> You can use a sting or list of keys to trigger your events </p>

````python
from pysimpleevent import EventSimpleGUI
import PySimpleGUI as sg


loop = EventSimpleGUI()

keys = ['_click', '_click1']
@loop.event(keys)
def when_btn_was_clicked(*args):
    print('Just a normal event')


layout = [
    [sg.B(f'{"Just a button":54}', key='_click')],
    [sg.B(f'{"Just another button":50}', key='_click1')]
]
window = sg.Window('Just a Window.', layout, scaling=1.5)
if __name__ == '__main__':
    loop.run_window(window, window_log=True)
````

#### Change log 0.2.7

- Tests are implemented 97% cov
- Close event replaced to the end of loop

####  Change log 0.2.5

- Now events can return values on Values dict







