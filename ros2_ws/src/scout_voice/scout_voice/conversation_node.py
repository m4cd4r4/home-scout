"""Conversation manager node.

Receives transcripts, classifies intent, queries object memory or LLM,
and publishes response text to TTS.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ConversationNode(Node):
    def __init__(self) -> None:
        super().__init__("conversation_node")
        self.declare_parameter("llm_model", "llama-3.2-1b-instruct")
        self.declare_parameter("conversation_timeout", 30.0)

        self.transcript_sub = self.create_subscription(
            String, "/scout/transcript", self.on_transcript, 10
        )
        self.speak_pub = self.create_publisher(String, "/scout/speak", 10)

        self.get_logger().info("Conversation node ready.")

    def on_transcript(self, msg: String) -> None:
        text = msg.data.strip()
        if not text:
            return

        self.get_logger().info(f"Heard: {text}")
        intent = self.classify_intent(text)
        response = self.generate_response(intent, text)

        out = String()
        out.data = response
        self.speak_pub.publish(out)

    def classify_intent(self, text: str) -> str:
        """Classify user intent from transcript."""
        lower = text.lower()
        if any(kw in lower for kw in ["where is", "where are", "find my", "seen my"]):
            return "object_query"
        if any(kw in lower for kw in ["patrol", "check the house", "look around"]):
            return "start_patrol"
        if any(kw in lower for kw in ["who am i", "do you know me"]):
            return "face_query"
        return "general"

    def generate_response(self, intent: str, text: str) -> str:
        """Generate response based on intent."""
        # TODO: For object_query, call WhereIs service
        # TODO: For start_patrol, call StartPatrol service
        # TODO: For general, run Llama-3.2-1B LLM inference
        return f"I heard you say: {text}. Intent: {intent}. (LLM not yet connected)"


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ConversationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
