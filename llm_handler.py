# llm_handler.py
from llama_cpp import Llama
from typing import Dict, Any, Optional
import json
import logging

class LLMHandler:
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 512,
        n_batch: int = 512,
        n_threads: Optional[int] = None,
        use_gpu: bool = False,
        gpu_layers: Optional[int] = None
    ):
        """Initialize the LLM handler with llama.cpp"""
        # Initialize model with specified parameters
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_batch=n_batch,
            n_threads=n_threads,
            n_gpu_layers=gpu_layers if use_gpu else 0
        )

    def generate_response(
        self,
        prompt: str,
        max_tokens: int = 128,  # Reduced from 256
        temperature: float = 0.3,  # Reduced from 0.7
        response_format: str = "text"
    ) -> Dict[str, Any]:
        """Generate a response using the LLM"""
        
        if response_format == "json":
            system_prompt = """You are a PLC control system. For any device command, return a JSON response:
{"command": "read|set", "device": "device_id", "value": "optional_value"}"""
        else:
            system_prompt = "You are a PLC control system. Provide clear, concise responses."

        # Keep the prompt simple and direct
        full_prompt = f"[INST] {system_prompt}\n\n{prompt} [/INST]"

        try:
            # Generate response with tighter constraints
            response = self.llm(
                full_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                echo=False
            )

            # Extract generated text
            generated_text = response["choices"][0]["text"].strip()

            # Parse JSON if requested
            if response_format == "json":
                try:
                    result = json.loads(generated_text)
                except json.JSONDecodeError:
                    result = {"command": "error", "error": "Failed to parse command"}
            else:
                result = {"response": generated_text}

            return result

        except Exception as e:
            return {"command": "error", "error": f"LLM generation error: {str(e)}"}
