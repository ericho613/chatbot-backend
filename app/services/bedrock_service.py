from typing import AsyncGenerator
import boto3

from app.config import get_settings
from app.exceptions import AIServiceException
from app.models import ChatMessage, GenerationConfig
from app.services.ai_service import BaseAIService


class BedrockService(BaseAIService):
    """
    Uses Bedrock Runtime converse / converse_stream style APIs.
    """
    def __init__(self):
        settings = get_settings()

        session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_REGION,
        )

        self.client = session.client("bedrock-runtime")
        self._model = settings.BEDROCK_MODEL_ID

    def model_name(self) -> str:
        return self._model

    def _to_bedrock_messages(self, messages: list[ChatMessage]) -> tuple[list[dict], list[dict]]:
        """
        Convert app chat messages into Bedrock converse message format.
        Returns:
        - regular messages
        - system prompts
        """
        bedrock_messages = []
        system_prompts = []

        for msg in messages:
            if msg.role == "system":
                system_prompts.append({"text": msg.content})
            else:
                bedrock_messages.append(
                    {
                        "role": msg.role,
                        "content": [{"text": msg.content}],
                    }
                )

        return bedrock_messages, system_prompts

    async def generate_text(
        self,
        messages: list[ChatMessage],
        generation_config: GenerationConfig,
    ) -> str:
        try:
            bedrock_messages, system_prompts = self._to_bedrock_messages(messages)

            response = self.client.converse(
                modelId=self._model,
                system=system_prompts,
                messages=bedrock_messages,
                inferenceConfig={
                    "maxTokens": generation_config.max_tokens,
                    "temperature": generation_config.temperature,
                    "topP": generation_config.top_p,
                },
            )

            output_message = response.get("output", {}).get("message", {})
            parts = output_message.get("content", [])
            text = "".join(part.get("text", "") for part in parts if "text" in part)
            return text
        except Exception as exc:
            raise AIServiceException(f"Bedrock converse failed: {str(exc)}") from exc

    async def stream_text(
        self,
        messages: list[ChatMessage],
        generation_config: GenerationConfig,
    ) -> AsyncGenerator[str, None]:
        try:
            bedrock_messages, system_prompts = self._to_bedrock_messages(messages)

            response = self.client.converse_stream(
                modelId=self._model,
                system=system_prompts,
                messages=bedrock_messages,
                inferenceConfig={
                    "maxTokens": generation_config.max_tokens,
                    "temperature": generation_config.temperature,
                    "topP": generation_config.top_p,
                },
            )

            stream = response.get("stream")
            if not stream:
                return

            for event in stream:
                # Bedrock stream event structure may vary slightly by SDK/model
                if "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"]
                    delta_content = delta.get("delta", {})
                    text = delta_content.get("text")
                    if text:
                        yield text
        except Exception as exc:
            raise AIServiceException(f"Bedrock converse_stream failed: {str(exc)}") from exc