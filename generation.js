// backend/generation.js
import { v4 as uuidv4 } from 'uuid';
import { generateText } from './ai-utils.js';

/**
 * Generate content ideas based on transcript
 */
export async function generateContentIdeas(config, transcript, instructions = "") {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider } = config;
    
    // Validate API configuration
    if (preferredProvider === "anthropic" && (!anthropicApiKey || anthropicApiKey.trim() === "")) {
      throw new Error("Anthropic API key is missing. Please add your API key in settings.");
    }

    if (preferredProvider === "openai" && (!openaiApiKey || openaiApiKey.trim() === "")) {
      throw new Error("OpenAI API key is missing. Please add your API key in settings.");
    }

    const prompt = `
You are an expert content strategist for an AI consulting company. Based on this transcript & being open to adding more to it, what are some ideas for videos that you can come up with?

TRANSCRIPT:
${transcript}

${instructions ? `ADDITIONAL INSTRUCTIONS: ${instructions}` : ""}

For each idea, provide:
1. A catchy title
2. A brief description of what the video would cover

IMPORTANT: Format your response STRICTLY as a valid JSON array of objects with 'title' and 'description' fields. Do not include any explanations, markdown formatting, or additional text outside of the JSON array.
Example format:
[
  {
    "title": "Example Title 1",
    "description": "Example description 1"
  },
  {
    "title": "Example Title 2",
    "description": "Example description 2"
  }
]
`;

    let text = "";

    // Generate text with the appropriate model
    text = await generateText(config, prompt, 1000);

    // Validate and parse the response
    if (!text || text.trim() === "") {
      throw new Error("Received empty response from AI service.");
    }

    try {
      // Try to extract JSON from the response
      // First attempt to parse directly
      try {
        const parsedData = JSON.parse(text);
        if (Array.isArray(parsedData)) {
          const ideas = parsedData.map(
            (idea, index) => ({
              id: `idea-${uuidv4().slice(0, 8)}`,
              title: idea.title || "Untitled Idea",
              description: idea.description || "No description provided",
            })
          );
          return ideas;
        }
      } catch (e) {
        // Initial parsing failed, try to extract JSON from the text
        console.warn("Direct JSON parsing failed, trying to extract JSON", e);
      }

      // Try to extract a JSON array from the text using regex
      const jsonMatch = text.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        try {
          const extractedJson = jsonMatch[0];
          const parsedData = JSON.parse(extractedJson);

          if (Array.isArray(parsedData)) {
            const ideas = parsedData.map(
              (idea, index) => ({
                id: `idea-${uuidv4().slice(0, 8)}`,
                title: idea.title || "Untitled Idea",
                description: idea.description || "No description provided",
              })
            );
            return ideas;
          }
        } catch (e) {
          console.warn("JSON extraction attempt failed", e);
        }
      }

      // If we still can't parse the JSON, throw an error
      console.error("Error parsing AI response - no valid JSON found in:", text);
      throw new Error(
        "Failed to parse response from AI service. The response was not in the expected JSON format."
      );
    } catch (parseError) {
      console.error("Error parsing AI response:", parseError);
      throw new Error(
        "Failed to parse response from AI service. The response was not in the expected JSON format."
      );
    }
  } catch (error) {
    console.error("Error generating content ideas:", error);
    
    // Provide more detailed error messages based on error type
    if (error.message?.includes("401") || error.message?.toLowerCase().includes("unauthorized")) {
      throw new Error(
        "API authentication failed. Please check your API key and ensure it's correctly formatted."
      );
    } else if (error.message?.includes("429")) {
      throw new Error("Rate limit exceeded. Please try again later.");
    } else if (error.message?.includes("timeout") || error.name === "AbortError") {
      throw new Error("Request timed out. The API didn't respond in time. Please try again.");
    } else if (error.message?.includes("parse") || error.message?.includes("JSON")) {
      throw new Error("Failed to parse the AI response. Please try again or adjust your instructions.");
    } else if (!config.anthropicApiKey && !config.openaiApiKey) {
      throw new Error("No API keys configured. Please add your API keys in the settings.");
    } else if (config.preferredProvider === "anthropic" && !config.anthropicApiKey) {
      throw new Error("Anthropic API key is missing but selected as preferred provider. Please add your Anthropic API key in settings.");
    } else if (config.preferredProvider === "openai" && !config.openaiApiKey) {
      throw new Error("OpenAI API key is missing but selected as preferred provider. Please add your OpenAI API key in settings.");
    }
    
    // If we can't determine a specific error, provide a general message with the original error
    throw new Error(`Error generating content: ${error.message || "Unknown error occurred"}`);
  }
}

/**
 * Generate video script from content idea
 */
export async function generateVideoScript(config, idea, transcript, instructions = "") {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider } = config;
    
    // Validate API configuration
    if (preferredProvider === "anthropic" && (!anthropicApiKey || anthropicApiKey.trim() === "")) {
      throw new Error("Anthropic API key is missing. Please add your API key in settings.");
    }

    if (preferredProvider === "openai" && (!openaiApiKey || openaiApiKey.trim() === "")) {
      throw new Error("OpenAI API key is missing. Please add your API key in settings.");
    }

    const prompt = `
Convert this transcript into a blog-style video script, keeping the proper hook & tone, refining the examples and concepts to make them clearer. The script should be written in first person and feel personal.

CONTENT IDEA:
Title: ${idea.title}
Description: ${idea.description}

ORIGINAL TRANSCRIPT:
${transcript}

${instructions ? `ADDITIONAL INSTRUCTIONS: ${instructions}` : ""}

Create a well-structured blog-style script that includes:
1. An attention-grabbing introduction
2. Clear sections with headers
3. Engaging talking points in first person perspective
4. Personal anecdotes or examples where appropriate

Format your response as a well-structured blog post that could be read as a script. Use a conversational tone throughout.
`;

    // Generate text with the appropriate model
    const text = await generateText(config, prompt, 2000);

    if (!text || text.trim() === "") {
      throw new Error("Received empty response from AI service.");
    }

    return {
      id: `script-${uuidv4().slice(0, 8)}`,
      ideaId: idea.id,
      title: idea.title,
      script: text,
    };
  } catch (error) {
    console.error("Error generating video script:", error);
    
    // More specific error messages for better user feedback
    if (error.message?.includes("401")) {
      throw new Error(
        "API authentication failed. Please check your API key and ensure it is correctly formatted."
      );
    } else if (error.message?.includes("429")) {
      throw new Error("Rate limit exceeded. Please try again in a few minutes.");
    } else if (error.message?.includes("timeout") || error.message?.includes("timed out")) {
      throw new Error("The API request timed out. This could be due to high traffic or complex instructions. Try again with simpler instructions.");
    } else if (error.message?.includes("settings") || error.message?.includes("configuration")) {
      throw new Error("API configuration issue. Please check your provider selection and API keys in settings.");
    }
    
    // Pass through the original error if none of the above matched
    throw error;
  }
}

/**
 * Refine existing video script
 */
export async function refineVideoScript(config, script, instructions) {
  try {
    console.log("===== STARTING SCRIPT REFINEMENT =====");
    console.log("Script ID:", script.id);
    console.log("Script title:", script.title);
    console.log("Instructions length:", instructions.length);
    console.log("Using provider:", config.preferredProvider);
    
    const { anthropicApiKey, openaiApiKey, preferredProvider } = config;
    
    // Validate API configuration
    if (preferredProvider === "anthropic" && (!anthropicApiKey || anthropicApiKey.trim() === "")) {
      throw new Error("Anthropic API key is missing. Please add your API key in settings.");
    }

    if (preferredProvider === "openai" && (!openaiApiKey || openaiApiKey.trim() === "")) {
      throw new Error("OpenAI API key is missing. Please add your API key in settings.");
    }

    const prompt = `
Refine this video script based on the following instructions. Maintain the original structure and tone where appropriate, but implement the requested changes.

ORIGINAL SCRIPT:
${script.script}

REFINEMENT INSTRUCTIONS:
${instructions}

Please provide the complete refined script. Keep what works well from the original and modify only what needs to be changed according to the instructions.
`;

    // Generate text with the appropriate model
    const text = await generateText(config, prompt, 2000);

    if (!text || text.trim() === "") {
      throw new Error("Received empty response from AI service.");
    }

    return {
      id: script.id,
      ideaId: script.ideaId,
      title: script.title,
      script: text,
    };
  } catch (error) {
    console.error("Error refining video script:", error);
    
    // More specific error messages for better user feedback
    if (error.message?.includes("401")) {
      throw new Error(
        "API authentication failed. Please check your API key and ensure it is correctly formatted."
      );
    } else if (error.message?.includes("429")) {
      throw new Error("Rate limit exceeded. Please try again in a few minutes.");
    } else if (error.message?.includes("timeout") || error.message?.includes("timed out")) {
      throw new Error("The API request timed out. This could be due to high traffic or complex instructions. Try again with simpler instructions.");
    } else if (error.message?.includes("settings") || error.message?.includes("configuration")) {
      throw new Error("API configuration issue. Please check your provider selection and API keys in settings.");
    }
    
    // Pass through the original error if none of the above matched
    throw error;
  }
}

/**
 * Regenerate video script completely
 */
export async function regenerateVideoScript(config, idea, transcript, instructions) {
  try {
    console.log("===== STARTING SCRIPT REGENERATION =====");
    console.log("Content idea ID:", idea.id);
    console.log("Content idea title:", idea.title);
    console.log("Transcript length:", transcript.length);
    console.log("Instructions length:", instructions.length);
    console.log("Using provider:", config.preferredProvider);
    
    const { anthropicApiKey, openaiApiKey, preferredProvider } = config;
    
    // Validate API configuration
    if (preferredProvider === "anthropic" && (!anthropicApiKey || anthropicApiKey.trim() === "")) {
      throw new Error("Anthropic API key is missing. Please add your API key in settings.");
    }

    if (preferredProvider === "openai" && (!openaiApiKey || openaiApiKey.trim() === "")) {
      throw new Error("OpenAI API key is missing. Please add your API key in settings.");
    }

    const prompt = `
Create a completely new blog-style video script based on the content idea and transcript. Follow the specific instructions provided.

CONTENT IDEA:
Title: ${idea.title}
Description: ${idea.description}

ORIGINAL TRANSCRIPT:
${transcript}

SPECIFIC INSTRUCTIONS:
${instructions}

Create a well-structured blog-style script that includes:
1. An attention-grabbing introduction
2. Clear sections with headers
3. Engaging talking points in first person perspective
4. Personal anecdotes or examples where appropriate

Format your response as a well-structured blog post that could be read as a script. Use a conversational tone throughout.
`;

    // Generate text with the appropriate model
    const text = await generateText(config, prompt, 2000);

    if (!text || text.trim() === "") {
      throw new Error("Received empty response from AI service.");
    }

    return {
      id: `script-${uuidv4().slice(0, 8)}`,
      ideaId: idea.id,
      title: idea.title,
      script: text,
    };
  } catch (error) {
    console.error("Error regenerating video script:", error);
    if (error.message?.includes("401")) {
      throw new Error(
        "API authentication failed. Please check your API key."
      );
    } else if (error.message?.includes("429")) {
      throw new Error("Rate limit exceeded. Please try again later.");
    }
    throw error;
  }
}

/**
 * Generate LinkedIn post from script
 */
export async function generateLinkedInPost(config, script) {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider } = config;
    
    // Validate API configuration
    if (preferredProvider === "anthropic" && (!anthropicApiKey || anthropicApiKey.trim() === "")) {
      throw new Error("Anthropic API key is missing. Please add your API key in settings.");
    }

    if (preferredProvider === "openai" && (!openaiApiKey || openaiApiKey.trim() === "")) {
      throw new Error("OpenAI API key is missing. Please add your API key in settings.");
    }

    const prompt = `
You are a social media expert specializing in LinkedIn content for an AI consulting company. Create an engaging LinkedIn post to promote a video with the following script.

VIDEO TITLE: ${script.title}

VIDEO SCRIPT:
${script.script}

Create a LinkedIn post that:
1. Has an attention-grabbing first line
2. Highlights the key value points from the video
3. Includes relevant hashtags related to AI consulting and technology
4. Has a clear call-to-action

Format your response as a ready-to-post LinkedIn update. Do not include any explanations or additional text outside the post.
`;

    // Generate text with the appropriate model
    const text = await generateText(config, prompt, 1000);

    if (!text || text.trim() === "") {
      throw new Error("Received empty response from AI service.");
    }

    return {
      id: `linkedin-${uuidv4().slice(0, 8)}`,
      scriptId: script.id,
      post: text,
    };
  } catch (error) {
    console.error("Error generating LinkedIn post:", error);
    if (error.message?.includes("401")) {
      throw new Error(
        "API authentication failed. Please check your API key."
      );
    } else if (error.message?.includes("429")) {
      throw new Error("Rate limit exceeded. Please try again later.");
    }
    throw error;
  }
}