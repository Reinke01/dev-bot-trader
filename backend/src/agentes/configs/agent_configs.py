from agno.models.anthropic import Claude
# from agno.models.groq import Groq

# Verificação de importação do Gemini
try:
    from agno.models.google import Gemini
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from agno.models.groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from agno.models.ollama import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from agno.models.deepseek import DeepSeek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

from ..instructions.trade_conductor_v1 import TRADE_CONDUCTOR_V1
from ..instructions.trade_conductor_v2 import TRADE_CONDUCTOR_V2
from ..instructions.trade_conductor_v3 import TRADE_CONDUCTOR_V3
from ..instructions.trade_entry_evaluator_v1 import TRADE_ENTRY_EVALUATOR_V1
from ..instructions.trade_entry_evaluator_v2 import TRADE_ENTRY_EVALUATOR_V2

class ModelConfigs:
    CLAUDE_SONNET = Claude(id="claude-sonnet-4-20250514")
    CLAUDE_SONNET_4_5 = Claude(id="claude-sonnet-4-5-20250929")
    CLAUDE_HAIKU = Claude(id="claude-3-5-haiku-20241022")

    if GEMINI_AVAILABLE:
        GEMINI_FLASH = Gemini(id="gemini-2.0-flash")
        GEMINI_PRO = Gemini(id="gemini-2.0-pro")
    
    if GROQ_AVAILABLE:
        GROQ_LLAMA = Groq(id="llama-3.3-70b-versatile")
        
    if OLLAMA_AVAILABLE:
        OLLAMA_MODEL = Ollama(id="llama3")

    if DEEPSEEK_AVAILABLE:
        DEEPSEEK_CHAT = DeepSeek(id="deepseek-chat")

    MODEL_MAP = {
        "sonnet": CLAUDE_SONNET,
        "sonnet-4-5": CLAUDE_SONNET_4_5,
        "haiku": CLAUDE_HAIKU,
    }
    
    if GEMINI_AVAILABLE:
        MODEL_MAP["gemini-flash"] = GEMINI_FLASH
        MODEL_MAP["gemini-pro"] = GEMINI_PRO
    
    if GROQ_AVAILABLE:
        MODEL_MAP["groq"] = GROQ_LLAMA

    if OLLAMA_AVAILABLE:
        MODEL_MAP["ollama"] = OLLAMA_MODEL
    
    if DEEPSEEK_AVAILABLE:
        MODEL_MAP["deepseek"] = DEEPSEEK_CHAT

class InstructionSets:
    TRADE_CONDUCTOR_V1 = TRADE_CONDUCTOR_V1
    TRADE_CONDUCTOR_V2 = TRADE_CONDUCTOR_V2
    TRADE_CONDUCTOR_V3 = TRADE_CONDUCTOR_V3
    TRADE_ENTRY_EVALUATOR_V1 = TRADE_ENTRY_EVALUATOR_V1
    TRADE_ENTRY_EVALUATOR_V2 = TRADE_ENTRY_EVALUATOR_V2

class AgentConfigs:
    @staticmethod
    def get_trade_conductor_config(version="v1", model="sonnet-4-5"):
        instruction_map = {
            "v1": InstructionSets.TRADE_CONDUCTOR_V1,
            "v2": InstructionSets.TRADE_CONDUCTOR_V2,
            "v3": InstructionSets.TRADE_CONDUCTOR_V3
        }
        
        return {
            "model": ModelConfigs.MODEL_MAP[model],
            "instructions": instruction_map[version]
        }
    
    @staticmethod
    def get_trade_entry_evaluator_config(version="v1", model="sonnet-4-5"):
        instruction_map = {
            "v1": InstructionSets.TRADE_ENTRY_EVALUATOR_V1,
            "v2": InstructionSets.TRADE_ENTRY_EVALUATOR_V2
        }

        return {
            "model": ModelConfigs.MODEL_MAP[model],
            "instructions": instruction_map[version]
        }