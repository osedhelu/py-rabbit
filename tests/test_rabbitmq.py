import pytest
from unittest.mock import Mock, patch
import json
import threading
import time
from src.producer import MessageProducer
from src.consumer import MessageConsumer


# Registrar el marcador de integración
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


class TestMessageProducer:
    @pytest.fixture
    def producer(self):
        with patch("pika.BlockingConnection") as mock_connection:
            mock_channel = Mock()
            mock_connection.return_value.channel.return_value = mock_channel
            producer = MessageProducer()
            yield producer
            producer.close()

    def test_add_observer(self, producer):
        observer = Mock()
        producer.add_observer(observer)
        assert observer in producer._observers

    def test_remove_observer(self, producer):
        observer = Mock()
        producer.add_observer(observer)
        producer.remove_observer(observer)
        assert observer not in producer._observers

    def test_notify_observers(self, producer):
        observer1 = Mock()
        observer2 = Mock()
        producer.add_observer(observer1)
        producer.add_observer(observer2)

        test_message = "Test message"
        producer.notify_observers(test_message)

        observer1.assert_called_once_with(test_message)
        observer2.assert_called_once_with(test_message)

    def test_publish_message(self, producer):
        test_message = "Test message"
        producer.publish_message(test_message)

        # Verificar que se llamó a basic_publish con los parámetros correctos
        producer.channel.basic_publish.assert_called_once()
        call_args = producer.channel.basic_publish.call_args[1]
        assert call_args["exchange"] == ""
        assert call_args["routing_key"] == "notifications"
        assert json.loads(call_args["body"]) == {"message": test_message}


class TestMessageConsumer:
    @pytest.fixture
    def consumer(self):
        with patch("pika.BlockingConnection") as mock_connection:
            mock_channel = Mock()
            mock_connection.return_value.channel.return_value = mock_channel
            consumer = MessageConsumer()
            yield consumer
            consumer.close()

    def test_callback(self, consumer):
        # Crear un mensaje de prueba
        test_message = {"message": "Test message"}
        test_body = json.dumps(test_message).encode()

        # Llamar al callback
        consumer.callback(None, None, None, test_body)

        # Verificar que se imprimió el mensaje correcto
        # Nota: En una prueba real, deberías capturar la salida stdout
        # o usar un logger mockeado

    def test_start_consuming(self, consumer):
        consumer.start_consuming()

        # Verificar que se configuró el consumo correctamente
        consumer.channel.basic_consume.assert_called_once_with(
            queue="notifications",
            on_message_callback=consumer.callback,
            auto_ack=True
        )

        # Verificar que se inició el consumo
        consumer.channel.start_consuming.assert_called_once()


@pytest.mark.integration
class TestIntegration:
    def setup_method(self):
        """Setup antes de cada prueba"""
        self.producer = None
        self.consumer = None
        self.consumer_thread = None
        self.stop_event = threading.Event()

    def teardown_method(self):
        """Cleanup después de cada prueba"""
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.stop_event.set()
            if self.consumer and self.consumer.channel:
                try:
                    self.consumer.channel.stop_consuming()
                except Exception:
                    pass
            self.consumer_thread.join(timeout=2)
            if self.consumer_thread.is_alive():
                self.consumer_thread._stop()

        if self.producer:
            try:
                self.producer.close()
            except Exception:
                pass

        if self.consumer:
            try:
                self.consumer.close()
            except Exception:
                pass

    def consumer_target(self):
        """Función objetivo para el thread del consumer"""
        try:
            self.consumer.start_consuming()
        except Exception as e:
            if not self.stop_event.is_set():
                pytest.fail(f"Error en el consumer: {str(e)}")

    def test_producer_consumer_integration(self):
        """Prueba de integración entre producer y consumer"""
        try:
            # Inicializar producer y consumer
            self.producer = MessageProducer()
            self.consumer = MessageConsumer()

            # Crear thread para el consumer
            self.consumer_thread = threading.Thread(
                target=self.consumer_target
            )
            self.consumer_thread.daemon = True
            self.consumer_thread.start()

            # Esperar a que el consumer se conecte
            time.sleep(2)

            # Enviar mensaje de prueba
            test_message = "Integration test message"
            self.producer.publish_message(test_message)

            # Esperar a que el mensaje sea procesado
            time.sleep(2)

        except Exception as e:
            pytest.fail(f"Error en la prueba de integración: {str(e)}")
