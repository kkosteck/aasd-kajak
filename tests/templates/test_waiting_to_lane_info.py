from spade.message import Message
from spade.template import Template


class TestWaitingToLaneInfo:
    def test_message_should_match_template(self):
        template0 = Template()
        template1 = Template()
        template0.set_metadata("performative0", "inform0")
        template1.set_metadata("performative1", "inform1")

        msg = Message(to="receiver@localhost")  # Instantiate the message
        msg.set_metadata(f"performative0", f"inform0")  # Set the "inform" FIPA performative
        msg.body = f"Hello World 1"  # Set the message content
        assert template0.match(msg)
