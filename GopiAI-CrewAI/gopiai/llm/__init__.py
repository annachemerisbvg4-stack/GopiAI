# Re-export handy LLM building blocks for DeerFlow integration
from .tool_spec import ToolSpec, to_openai_tools, to_gemini_tools
from .payload_builder import build_payload
from .provider_factory import ProviderClient, build_client, get_api_key
