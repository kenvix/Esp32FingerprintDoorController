IO_BLOCK_SLEEP_TIME = 0.05
IO_READ_TIMEOUT = 5

LED_STATUS_PIN = 2

LED_TM1637_ENABLE = False
LED_TM1637_PIN_CLK = 5
LED_TM1637_PIN_DIO = 4

REBOOT_PIN = 32

DOOR_MOTOR_ENABLE = True
DOOR_MOTOR_MODEL = "mg996r"
DOOR_MOTOR_PIN = 12
DOOR_MOTOR_PWM_OPEN_FREQ = 1000
DOOR_MOTOR_PWM_OPEN_DUTY = 50
DOOR_MOTOR_PWM_CLOSE_FREQ = 1000
DOOR_MOTOR_PWM_CLOSE_DUTY = 100
DOOR_MOTOR_ROLLTATE_DELAY = 5

# Direct Door Controller
DOOR_DIRECT_ENABLE = False
DOOR_DIRECT_PIN_OPEN = 0
DOOR_DIRECT_PIN_CLOSE = 0
DOOR_DIRECT_ROLLTATE_DELAY = 0.5

DOOR_AUTOCLOSE_DELAY = 8

FINGER_ENABLE = True
FINGER_MODEL = "as608"
FINGER_WAK_IRQ_ENABLE = True
FINGER_WAK_PIN = 4
FINGER_UART_PORT = "COM3"
FINGER_SECURITY_LEVEL = 5
FINGER_STATUS_PIN = 2

BEEP_OUTSIDE_PIN = 13
BEEP_INSIDE_PIN = 14