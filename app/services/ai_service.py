from typing import List, Dict, Any, Optional
import uuid
import json
import re
import os
from app.models.api_models import ContentIdea, VideoScript, LinkedInPost, ApiConfig

class AIService:
    def __init__(self, config: ApiConfig):
        self.config = config
        
        # Initialize clients based on provided API keys
        self.anthropic_client = None
        self.openai_client = None
        
        if config.preferredProvider == "anthropic":
            api_key = config.anthropicApiKey or os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                try:
                    import anthropic
                    self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                except ImportError:
                    raise ValueError("Anthropic SDK not installed properly. Install with: pip install anthropic>=0.19.1")
            else:
                raise ValueError("Anthropic API key is missing.")
        elif config.preferredProvider == "openai":
            api_key = config.openaiApiKey or os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    import openai
                    self.openai_client = openai.OpenAI(api_key=api_key)
                except ImportError:
                    raise ValueError("OpenAI SDK not installed properly.")
            else:
                raise ValueError("OpenAI API key is missing.")
        else:
            raise ValueError(f"Invalid provider: {config.preferredProvider}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the AI provider"""
        try:
            if self.config.preferredProvider == "anthropic" and self.anthropic_client:
                try:
                    # Using Messages API for Claude 3
                    message = self.anthropic_client.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens=10,
                        messages=[
                            {"role": "user", "content": "Return the text 'API connection successful' as a response."}
                        ]
                    )
                    return {
                        "success": True, 
                        "provider": "anthropic", 
                        "message": "Anthropic API connection successful"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "provider": "anthropic",
                        "message": f"Anthropic API error: {str(e)}",
                        "error": str(e)
                    }
            elif self.config.preferredProvider == "openai" and self.openai_client:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Return the text 'API connection successful' as a response."}],
                    max_tokens=10
                )
                return {
                    "success": True, 
                    "provider": "openai", 
                    "message": "OpenAI API connection successful"
                }
            else:
                return {
                    "success": False, 
                    "message": "No valid API configuration found"
                }
        except Exception as e:
            return {
                "success": False, 
                "message": f"Failed to connect to API service: {str(e)}",
                "error": str(e)
            }
    
    async def _get_anthropic_response(self, prompt_content: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Helper method to get a response from Anthropic using the Messages API"""
        message = self.anthropic_client.messages.create(
            model="claude-3-7-sonnet-20250219",  # Latest Claude model
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt_content}
            ]
        )
        
        return message.content[0].text
    
    async def generate_content_ideas(self, transcript: str, instructions: str = "") -> List[ContentIdea]:
        """Generate content ideas from transcript"""
        prompt = f"""
You are an expert content strategist for an AI consulting company. Based on this transcript & being open to adding more to it, what are some ideas for videos that you can come up with?

TRANSCRIPT:
{transcript}

{f"ADDITIONAL INSTRUCTIONS: {instructions}" if instructions else ""}

For each idea, provide:
1. A catchy title
2. A brief description of what the video would cover

IMPORTANT: Format your response STRICTLY as a valid JSON array of objects with 'title' and 'description' fields. Do not include any explanations, markdown formatting, or additional text outside of the JSON array.
Example format:
[
  {{
    "title": "Example Title 1",
    "description": "Example description 1"
  }},
  {{
    "title": "Example Title 2",
    "description": "Example description 2"
  }}
]
"""
        try:
            text = ""
            # Generate text based on provider
            if self.config.preferredProvider == "anthropic" and self.anthropic_client:
                text = await self._get_anthropic_response(prompt, 1000, 0.7)
            elif self.config.preferredProvider == "openai" and self.openai_client:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                text = completion.choices[0].message.content
            else:
                raise ValueError("No valid AI provider configured")
            
            # Parse response
            return self._parse_content_ideas_response(text)
        except Exception as e:
            raise Exception(f"Error generating content ideas: {str(e)}")
    
    def _parse_content_ideas_response(self, text: str) -> List[ContentIdea]:
        """Parse the AI response into ContentIdea objects"""
        if not text or text.strip() == "":
            raise ValueError("Received empty response from AI service")
        
        try:
            # Try direct JSON parsing
            parsed_data = json.loads(text)
            if isinstance(parsed_data, list):
                return [
                    ContentIdea(
                        id=f"idea-{uuid.uuid4().hex[:8]}",
                        title=idea.get("title", "Untitled Idea"),
                        description=idea.get("description", "No description provided")
                    )
                    for idea in parsed_data
                ]
        except json.JSONDecodeError:
            # Try extracting JSON with regex
            json_match = re.search(r'\[([\s\S]*)\]', text)
            if json_match:
                try:
                    extracted_json = json_match.group(0)
                    parsed_data = json.loads(extracted_json)
                    if isinstance(parsed_data, list):
                        return [
                            ContentIdea(
                                id=f"idea-{uuid.uuid4().hex[:8]}",
                                title=idea.get("title", "Untitled Idea"),
                                description=idea.get("description", "No description provided")
                            )
                            for idea in parsed_data
                        ]
                except:
                    pass
        
        # If we get here, we couldn't parse the JSON
        raise ValueError("Failed to parse AI response as JSON. The response was not in the expected format.")
    
    async def generate_video_script(self, idea: ContentIdea, transcript: str, instructions: str = "") -> VideoScript:
        """Generate a video script from content idea"""
        prompt = f"""
Convert this transcript into a blog-style video script, keeping the proper hook & tone, refining the examples and concepts to make them clearer. The script should be written in first person and feel personal.

CONTENT IDEA:
Title: {idea.title}
Description: {idea.description}

ORIGINAL TRANSCRIPT:
{transcript}

{f"ADDITIONAL INSTRUCTIONS: {instructions}" if instructions else ""}

Create a well-structured blog-style script that includes:
1. An attention-grabbing introduction
2. Clear sections with headers
3. Engaging talking points in first person perspective
4. Personal anecdotes or examples where appropriate

Format your response as a well-structured blog post that could be read as a script. Use a conversational tone throughout.
"""
        try:
            text = ""
            # Generate text based on provider
            if self.config.preferredProvider == "anthropic" and self.anthropic_client:
                text = await self._get_anthropic_response(prompt, 2000, 0.7)
            elif self.config.preferredProvider == "openai" and self.openai_client:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0.7
                )
                text = completion.choices[0].message.content
            else:
                raise ValueError("No valid AI provider configured")
            
            if not text or text.strip() == "":
                raise ValueError("Received empty response from AI service")
            
            # Create video script
            return VideoScript(
                id=f"script-{uuid.uuid4().hex[:8]}",
                ideaId=idea.id,
                title=idea.title,
                script=text
            )
        except Exception as e:
            raise Exception(f"Error generating video script: {str(e)}")
    
    async def refine_video_script(self, script: VideoScript, instructions: str) -> VideoScript:
        """Refine an existing video script"""
        prompt = f"""
Refine this video script based on the following instructions. Maintain the original structure and tone where appropriate, but implement the requested changes.

ORIGINAL SCRIPT:
{script.script}

REFINEMENT INSTRUCTIONS:
{instructions}

Please provide the complete refined script. Keep what works well from the original and modify only what needs to be changed according to the instructions.
"""
        try:
            text = ""
            # Generate text based on provider
            if self.config.preferredProvider == "anthropic" and self.anthropic_client:
                text = await self._get_anthropic_response(prompt, 2000, 0.7)
            elif self.config.preferredProvider == "openai" and self.openai_client:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0.7
                )
                text = completion.choices[0].message.content
            else:
                raise ValueError("No valid AI provider configured")
            
            if not text or text.strip() == "":
                raise ValueError("Received empty response from AI service")
            
            # Create refined video script
            return VideoScript(
                id=script.id,
                ideaId=script.ideaId,
                title=script.title,
                script=text
            )
        except Exception as e:
            raise Exception(f"Error refining video script: {str(e)}")
    
    async def regenerate_video_script(self, idea: ContentIdea, transcript: str, instructions: str) -> VideoScript:
        """Regenerate a video script completely"""
        prompt = f"""
Create a completely new blog-style video script based on the content idea and transcript. Follow the specific instructions provided.

CONTENT IDEA:
Title: {idea.title}
Description: {idea.description}

ORIGINAL TRANSCRIPT:
{transcript}

SPECIFIC INSTRUCTIONS:
{instructions}

Create a well-structured blog-style script that includes:
1. An attention-grabbing introduction
2. Clear sections with headers
3. Engaging talking points in first person perspective
4. Personal anecdotes or examples where appropriate

Format your response as a well-structured blog post that could be read as a script. Use a conversational tone throughout.
"""
        try:
            text = ""
            # Generate text based on provider
            if self.config.preferredProvider == "anthropic" and self.anthropic_client:
                text = await self._get_anthropic_response(prompt, 2000, 0.7)
            elif self.config.preferredProvider == "openai" and self.openai_client:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0.7
                )
                text = completion.choices[0].message.content
            else:
                raise ValueError("No valid AI provider configured")
            
            if not text or text.strip() == "":
                raise ValueError("Received empty response from AI service")
            
            # Create new video script
            return VideoScript(
                id=f"script-{uuid.uuid4().hex[:8]}",
                ideaId=idea.id,
                title=idea.title,
                script=text
            )
        except Exception as e:
            raise Exception(f"Error regenerating video script: {str(e)}")
    
    async def generate_linkedin_post(self, script: VideoScript) -> LinkedInPost:
        """Generate a LinkedIn post from a video script"""
        prompt = f"""
You are a social media expert specializing in LinkedIn content for an AI consulting company. Create an engaging LinkedIn post to promote a video with the following script.

VIDEO TITLE: {script.title}

VIDEO SCRIPT:
{script.script}

Create a LinkedIn post that:
1. Has an attention-grabbing first line
2. Highlights the key value points from the video
3. Includes relevant hashtags related to AI consulting and technology
4. Has a clear call-to-action

Format your response as a ready-to-post LinkedIn update. Do not include any explanations or additional text outside the post.
"""
        try:
            text = ""
            # Generate text based on provider
            if self.config.preferredProvider == "anthropic" and self.anthropic_client:
                text = await self._get_anthropic_response(prompt, 1000, 0.7)
            elif self.config.preferredProvider == "openai" and self.openai_client:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                text = completion.choices[0].message.content
            else:
                raise ValueError("No valid AI provider configured")
            
            if not text or text.strip() == "":
                raise ValueError("Received empty response from AI service")
            
            # Create LinkedIn post
            return LinkedInPost(
                id=f"linkedin-{uuid.uuid4().hex[:8]}",
                scriptId=script.id,
                post=text
            )
        except Exception as e:
            raise Exception(f"Error generating LinkedIn post: {str(e)}")