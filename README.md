# E-ink Calendar Display - Architecture

## Design Patterns Used

### 1. State Pattern (Screen Management)

The application uses the **State Pattern** to manage different display screens. Each screen is a separate state, and the `ScreenManager` controls transitions between states.

```
┌─────────────────────────────────────────────────────────────┐
│                      ScreenManager                          │
│  (Context - manages screen states and transitions)          │
├─────────────────────────────────────────────────────────────┤
│  - register_screen(screen)                                  │
│  - next_screen()    ←── triggered by button press           │
│  - render_current()                                         │
│  - current_screen                                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ manages
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     BaseScreen (ABC)                        │
│              (Abstract State Interface)                     │
├─────────────────────────────────────────────────────────────┤
│  + render() → Image                                         │
│  + get_data() → dict                                        │
│  + on_enter()                                               │
│  + on_exit()                                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┬───────────────┐
          │                 │                 │               │
          ▼                 ▼                 ▼               ▼
┌─────────────────┐ ┌───────────────┐ ┌─────────────┐ ┌─────────────┐
│ EventsToday    │ │ EventsTomorrow│ │ TasksScreen │ │ DHT11Screen │
│ Screen         │ │ Screen        │ │             │ │             │
│                │ │               │ │             │ │             │
│ (State 1)      │ │ (State 2)     │ │ (State 3)   │ │ (State 4)   │
└─────────────────┘ └───────────────┘ └─────────────┘ └─────────────┘
```

### 2. Observer Pattern (LED Notifications)

The `EventNotifier` observes changes in today's events and triggers LED notifications when an event is approaching (10 minutes before start).

```
┌─────────────────────────────────────────────────────────────┐
│                    EventNotifier                            │
│              (Observer - monitors events)                   │
├─────────────────────────────────────────────────────────────┤
│  - update_events(events)  ←── called when events change     │
│  - check_notifications()                                    │
│  - start() / stop()                                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ observes
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               EventsTodayScreen                             │
│           (Subject - provides event data)                   │
├─────────────────────────────────────────────────────────────┤
│  - get_events() → List[Event]                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ triggers (10 min before event)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     LED Driver                              │
│                 (Notification output)                       │
├─────────────────────────────────────────────────────────────┤
│  - turn_on()                                                │
│  - turn_off()                                               │
└─────────────────────────────────────────────────────────────┘
```

## Application Flow

```
┌───────────────────────────────────────────────────────────────────────┐
│                          AppController                                │
│                    (Main Application Orchestrator)                    │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────────┐      ┌──────────────┐      ┌─────────────────┐     │
│   │   Button    │──────│ScreenManager │──────│   E-ink EPD     │     │
│   │   Driver    │      │              │      │   Display       │     │
│   └─────────────┘      └──────────────┘      └─────────────────┘     │
│         │                     │                                       │
│         │ press               │ sync events                          │
│         ▼                     ▼                                       │
│   ┌─────────────┐      ┌──────────────┐                              │
│   │ next_screen │      │EventNotifier │────────► LED                 │
│   │     ()      │      │  (Observer)  │       (10 min before)        │
│   └─────────────┘      └──────────────┘                              │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Screen Rotation

```
    Button Press          Button Press          Button Press
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   Events    │   →    │   Events    │   →    │   Tasks     │
│   Today     │        │  Tomorrow   │        │             │
│   (1/4)     │        │   (2/4)     │        │   (3/4)     │
└─────────────┘        └─────────────┘        └─────────────┘
       ↑                                              │
       │                                              ▼
       │                                       ┌─────────────┐
       │                                       │   DHT11     │
       └───────────────────────────────────────│   Sensor    │
                    Button Press               │   (4/4)     │
                                               └─────────────┘
```

## File Structure

```
src/
├── app/
│   ├── __init__.py
│   ├── controller.py          # Main application orchestrator
│   ├── event_notifier.py      # Observer for LED notifications
│   └── screens/
│       ├── __init__.py
│       ├── base_screen.py     # Abstract base screen (State interface)
│       ├── screen_manager.py  # State manager (Context)
│       ├── events_today_screen.py
│       ├── events_tomorrow_screen.py
│       ├── tasks_screen.py
│       └── dht11_screen.py
├── hardware/
│   ├── button_driver.py       # Button input
│   ├── led_driver.py          # LED output
│   ├── dht11_driver.py        # Temperature/humidity sensor
│   └── epd_*.py               # E-ink display drivers
├── services/
│   └── structure_parser.py    # Google Calendar/Tasks API
└── main.py                    # Entry point
```

## Key Features

1. **Screen Rotation**: 4 screens cycle through button press
   - Screen 1: Today's events (from Google Calendar)
   - Screen 2: Tomorrow's events
   - Screen 3: Tasks (from Google Tasks)
   - Screen 4: DHT11 temperature & humidity

2. **LED Notification**: LED turns on 10 minutes before any timed event starts

3. **Data Refresh**: Events are refreshed every 5 minutes in background

4. **Mock Support**: Works with mock display for development/testing

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy from env.sample)
cp env.sample .env
# Edit .env with your configuration

# Run the application
python -m src.main
```

## Running Tests

```bash
pytest src/tests/
```
