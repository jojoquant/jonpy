import pika
from jnpy.app.pub_sub.setting import qapubsub_ip, qapubsub_port, qapubsub_user, qapubsub_password


class base_ps:

    def __init__(
            self, host=qapubsub_ip, port=qapubsub_port, user=qapubsub_user, password=qapubsub_password,
            channel_number=1, queue_name='', routing_key='default', exchange='', vhost='/'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.queue_name = queue_name
        self.exchange = exchange
        self.routing_key = routing_key
        self.vhost = vhost
        self.channel_number = channel_number
        # fixed: login with other user, pass failure @zhongjy
        credentials = pika.PlainCredentials(
            self.user, self.password, erase_on_connect=True)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost,
                                      credentials=credentials, heartbeat=0, socket_timeout=5,
                                      )
        )

        self.channel = self.connection.channel(
            channel_number=self.channel_number)

    def reconnect(self):
        try:
            self.connection.close()
        except:
            pass

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port,
                                      heartbeat=0, virtual_host=self.vhost,
                                      socket_timeout=5, ))

        self.channel = self.connection.channel(
            channel_number=self.channel_number)
        return self
