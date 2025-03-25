import json
import time
import logging
import re
import hashlib
import anthropic
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AnthropicService:
    def __init__(self, api_key, model="claude-3-haiku-20240307", max_retries=3, timeout=60):

        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        
        try:
            self.client = Anthropic(api_key=api_key)
            logger.info(f"Initialized Anthropic client with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
        
        # Response cache to avoid duplicate requests
        self.response_cache = {}
        
    def _create_cache_key(self, system_message, user_message):

        # Create a hash of the combined messages
        content = f"{system_message}|||{user_message}"
        return hashlib.md5(content.encode()).hexdigest()
        
    def send_message(self, system_message, user_message, use_cache=True):
        cache_key = self._create_cache_key(system_message, user_message)
        
        # Check cache first if enabled
        if use_cache and cache_key in self.response_cache:
            logger.info("Using cached response")
            return self.response_cache[cache_key]
            
        # Initialize error tracking
        last_error = None
        
        # Implement retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Sending request to Claude API (attempt {attempt+1}/{self.max_retries})")
                
                start_time = time.time()
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2500,
                    temperature=0,
                    system=system_message,
                    messages=[
                        {
                            "role": "user",
                            "content": user_message
                        },
                    ]
                )
                
                # Log request statistics
                request_time = time.time() - start_time
                logger.info(f"Request completed in {request_time:.2f}s")
                
                # Calculate cost (approximate)
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                cost_usd = (input_tokens / 1_000_000) * 0.80 + (output_tokens / 1_000_000) * 4
                cost_inr = cost_usd * 86.93  # Approximate conversion to INR
                
                logger.info(f"Request tokens: {input_tokens} in, {output_tokens} out (est. cost: ${cost_usd:.6f}, ₹{cost_inr:.2f})")
                # Parse the response
                result = self._parse_response(response)
                
                # Cache the successful response if enabled
                if use_cache and result.get("success", False):
                    self.response_cache[cache_key] = result
                    
                return result
                
            except anthropic.APIError as e:
                last_error = e
                logger.warning(f"API error on attempt {attempt+1}: {e}")
                
                # Don't retry on certain error types
                if hasattr(e, 'status_code') and e.status_code in [400, 401, 403]:
                    logger.error(f"Non-retryable error: {e}")
                    break
                    
                # Exponential backoff
                if attempt < self.max_retries - 1:
                    sleep_time = 2 ** attempt
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    
            except anthropic.APIConnectionError as e:
                last_error = e
                logger.warning(f"Connection error on attempt {attempt+1}: {e}")
                
                # Exponential backoff
                if attempt < self.max_retries - 1:
                    sleep_time = 2 ** attempt
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error on attempt {attempt+1}: {e}", exc_info=True)
                # Don't retry on unexpected errors
                break
                
        # If we get here, all retries failed
        error_message = str(last_error) if last_error else "Unknown error"
        logger.error(f"All {self.max_retries} attempts failed: {error_message}")
        
        return {
            "error": f"Failed to get response from Claude API: {error_message}",
            "success": False
        }
        
    def _parse_response(self, response):
        try:
            message = response.content[0].text
            
            # Look for output tags
            json_pattern = re.compile(r'<output>([\s\S]*?)</output>', re.DOTALL)
            matches = json_pattern.findall(message)
            
            if matches:
                # Use the first JSON block found
                clean_json = matches[0].strip()
            else:
                # If no JSON blocks in the expected format, try to extract JSON directly
                # First find the first { character
                if '{' in message:
                    start_idx = message.find('{')
                    # Find the last } character
                    end_idx = message.rfind('}')
                    
                    if end_idx > start_idx:
                        clean_json = message[start_idx:end_idx+1].strip()
                    else:
                        raise ValueError("Could not locate valid JSON in response")
                else:
                    raise ValueError("No JSON object found in response")
            
            # Parse the JSON
            plan_data = json.loads(clean_json)
            
            # Add success flag
            plan_data["success"] = True
            
            return plan_data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing response: {e}")
            logger.debug(f"Raw response content: {response.content[0].text}")
            
            return {
                "error": f"Failed to parse JSON response: {e}",
                "raw_response": response.content[0].text,
                "success": False
            }