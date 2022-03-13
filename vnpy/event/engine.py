"""
Event-driven framework of VeighNa framework.
"""
from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from time import sleep
from typing import Any, Callable, List

import pika
from vnpy.trader.object import TickData, LogData

from jnpy.utils.utils_json import convert_object_to_json
from vnpy.trader.event import EVENT_TICK, EVENT_TRADE, EVENT_ORDER, EVENT_POSITION, EVENT_ACCOUNT, EVENT_QUOTE, \
    EVENT_CONTRACT, EVENT_LOG, EVENT_TIMER
from vnpy.trader.utility import load_json


class Event:
    """
    Event object consists of a type string which is used
    by event engine for distributing event, and a data
    object which contains the real data.
    """

    def __init__(self, type: str, data: Any = None):
        """"""
        self.type: str = type
        self.data: Any = data


# Defines handler function to be used in event engine.
HandlerType = Callable[[Event], None]


class EventEngine:
    """
    Event engine distributes event object based on its type
    to those handlers registered.

    It also generates timer event by every interval seconds,
    which can be used for timing purpose.
    """

    def __init__(self, interval: int = 1):
        """
        Timer event is generated every 1 second by default, if
        interval not specified.
        """
        self._interval: int = interval
        self._queue: Queue = Queue()
        self._active: bool = False
        self._thread: Thread = Thread(target=self._run)
        self._timer: Thread = Thread(target=self._run_timer)
        self._handlers: defaultdict = defaultdict(list)
        self._general_handlers: List = []

        # fangyang add
        self.message_queue_setting_filename = "message_queue_setting.json"
        self.message_queue_setting = load_json(self.message_queue_setting_filename)

        self.connection: pika.BlockingConnection = None
        self.tick_send_channel = None
        self.log_send_channel = None

        if self.message_queue_setting:
            self.msq_host: str = self.message_queue_setting['host']
            self.msq_port: int = self.message_queue_setting['port']
            self.msq_username: str = self.message_queue_setting['username']
            self.msq_password: str = self.message_queue_setting['password']

            self.tick_exchange: str = "tick_ex"
            self.log_exchange: str = "log_ex"

            self.queue_list = [
                EVENT_TIMER, EVENT_TICK, EVENT_TRADE, EVENT_ORDER,
                EVENT_POSITION, EVENT_ACCOUNT, EVENT_QUOTE, EVENT_CONTRACT,
                EVENT_LOG
            ]

            # self.recv_channel_map = {
            #     queue_name: {
            #         routing_key: {
            #             "channel": channel,
            #             "thread": Thread(),
            #         }
            #     }
            # }
            # self.recv_channel_map = {k: {} for k in self.queue_list}

            self._init_rabbitmq()

    # fangyang add
    def _init_rabbitmq(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.msq_host,
                    port=self.msq_port,
                    credentials=pika.PlainCredentials(self.msq_username, self.msq_password)
                )
            )
        except Exception as e:
            self.connection = None
            print(e)

        if self.connection is not None:
            if self.tick_send_channel is None:
                self.tick_send_channel = self.connection.channel()
                self.tick_send_channel.exchange_declare(
                    exchange=self.tick_exchange,
                    exchange_type="topic",
                    durable=True
                )
            if self.log_send_channel is None:
                self.log_send_channel = self.connection.channel()
                self.log_send_channel.exchange_declare(
                    exchange=self.log_exchange,
                    exchange_type="topic",
                    durable=True
                )

    @staticmethod
    def callback(ch, method, props, body):
        # r = json.loads(body)
        # print(r)
        print(f"[*] routing_key({method.routing_key}) Received {body}")

    def _run(self) -> None:
        """
        Get event from queue and then process it.
        """
        while self._active:
            try:
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event) -> None:
        """
        First distribute event to those handlers registered listening
        to this type.

        Then distribute event to those general handlers which listens
        to all types.
        """
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self) -> None:
        """
        Sleep by interval second(s) and then generate a timer event.
        """
        while self._active:
            sleep(self._interval)
            event = Event(EVENT_TIMER)
            self.put(event)

    def start(self) -> None:
        """
        Start event engine to process events and generate timer events.
        """
        self._active = True
        self._thread.start()
        self._timer.start()

    def stop(self) -> None:
        """
        Stop event engine.
        """
        self._active = False
        self._timer.join()
        self._thread.join()

    def put(self, event: Event) -> None:
        """
        Put an event object into event queue.
        """
        self._queue.put(event)
        if event.type != EVENT_TIMER:
            print("[put] ", event.type, event.data)

        if (self.tick_send_channel is not None) \
                and isinstance(event.data, TickData) \
                and (event.type != EVENT_TICK):
            try:
                body_msg = convert_object_to_json(event.data)
                self.tick_send_channel.basic_publish(
                    exchange=self.tick_exchange,
                    routing_key=event.type,  # 'eTick.2205.SHFE'
                    body=body_msg
                )
            except Exception as e:
                print(e)

        if (self.log_send_channel is not None) and isinstance(event.data, LogData):
            try:
                body_msg = convert_object_to_json(event.data)
                self.log_send_channel.basic_publish(
                    exchange=self.log_exchange,
                    routing_key=event.type,
                    body=body_msg
                )
            except Exception as e:
                print(e)

        # if self.recv_channel_map.get(event.type):
        #     self.tick_send_channel.basic_publish(
        #         exchange=self.tick_exchange, routing_key=event.type, body=event.data
        #     )

    def register(self, type: str, handler: HandlerType) -> None:
        """
        Register a new handler function for a specific event type. Every
        function can only be registered once for each event type.
        """
        handler_list = self._handlers[type]
        # print(type, self._handlers)

        if handler not in handler_list:
            handler_list.append(handler)

            # recv_channel = self.connection.channel()
            # recv_channel.exchange_declare(
            #     exchange=self.tick_exchange,
            #     exchange_type='topic',
            #     durable=True,  # golang 那边设置了这个参数, 如果不设置为True, 生成的exchange是同名, 但是是不一致的, py和go先后执行会报错
            # )
            # # result =
            # type = type[:-1] if type.endswith(".") else type
            #
            # recv_channel.queue_declare(
            #     queue=type,  # 不指定queue的名字, 让RBMQ自动生成
            #     # durable=True,
            #     exclusive=True,  # 用后即焚, conn关闭,队列删除
            # )
            #
            # # queue_name = result.method.queue
            # routing_key = f"{type}.{handler.__name__}"
            # recv_channel.queue_bind(
            #     exchange=self.tick_exchange,
            #     routing_key=routing_key,
            #     queue=type
            # )  # 根据queue_name去绑定一个exchange
            #
            # print(f"[*] Exchange:{self.tick_exchange}, queue_name: {type}, routing_key: {routing_key}. To exit press CTRL+C")
            #
            # recv_channel.basic_consume(
            #     queue=type,
            #     on_message_callback=partial(handler, ch=None, method=None, props=None, body=None),
            #     # 默认为false, 需要在callback中定义basic_ack, 如果不人工设置ack, client带着消息die了, produce不会重发
            #     # 设置成true, 省去人工设置ack, client 带着消息 die 了, produce会重发
            #     auto_ack=True,
            # )
            # print(f"[*] routing_key:{routing_key} bind consumer: {handler.__name__}. To exit press CTRL+C")
            #
            # # channel.start_consuming()
            # recv_thread = Thread(target=recv_channel.start_consuming)
            #
            # self.recv_channel_map[type][routing_key] = {
            #     'channel': recv_channel,
            #     'thread': recv_thread
            # }
            #
            # recv_thread.start()
            # # recv_channel.start_consuming()
            # print(111)

    def unregister(self, type: str, handler: HandlerType) -> None:
        """
        Unregister an existing handler function from event engine.
        """
        handler_list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)
            # routing_key = f"{type}.{handler.__name__}"
            # self.recv_channel_map[type][routing_key]['channel'].close()
            # self.recv_channel_map[type][routing_key]['thread'].join()

        if not handler_list:
            self._handlers.pop(type)

    def register_general(self, handler: HandlerType) -> None:
        """
        Register a new handler function for all event types. Every
        function can only be registered once for each event type.
        """
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: HandlerType) -> None:
        """
        Unregister an existing general handler function.
        """
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)
