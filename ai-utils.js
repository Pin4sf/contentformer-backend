// backend/ai-utils.js
import { anthropic } from '@ai-sdk/anthropic';
import { openai } from '@ai-sdk/openai';

/**
 * Generates text using the appropriate AI model based on config
 * 
 * @param {Object} config - The API configuration
 * @param {string} prompt - The prompt to send to the AI model
 * @param {number} maxTokens - Maximum number of tokens to generate
 * @param {number} temperature - Temperature for generation (higher = more creative)
 * @returns {Promise<string>} The generated text
 */
export async function generateText(config, prompt, maxTokens = 1000, temperature = 0.7) {
  const { anthropicApiKey, openaiApiKey, preferredProvider } = config;
  
  // Create abort controller to handle timeouts
  const controller = new AbortController();
  const timeoutDuration = 120000; // 2 minutes
  const timeoutId = setTimeout(() => controller.abort(), timeoutDuration);

  try {
    let response;
    
    if (preferredProvider === 'anthropic' && anthropicApiKey) {
      // Use Anthropic's Claude
      console.log('Using Anthropic Claude for generation');
      
      response = await anthropic('claude-3-5-sonnet-20241022', {
        apiKey: anthropicApiKey,
      }).generateText({
        prompt,
        temperature,
        maxTokens,
        signal: controller.signal,
      });
      
      return response.text;
    } else if (preferredProvider === 'openai' && openaiApiKey) {
      // Use OpenAI's GPT-4
      console.log('Using OpenAI GPT-4 for generation');
      
      response = await openai('gpt-4', { 
        apiKey: openaiApiKey 
      }).generateText({
        prompt,
        temperature,
        maxTokens,
        signal: controller.signal,
      });
      
      return response.text;
    } else {
      throw new Error(`Invalid AI provider configuration: ${preferredProvider}`);
    }
  } catch (error) {
    console.error('AI generation error:', error);
    
    if (error.name === 'AbortError') {
      throw new Error('Request timed out after 2 minutes. The AI model took too long to respond.');
    }
    
    // Enhance error with provider information
    const providerInfo = preferredProvider === 'anthropic' ? 'Anthropic Claude' : 'OpenAI GPT';
    
    if (error.status === 401 || error.message?.includes('auth')) {
      throw new Error(`Authentication failed with ${providerInfo}. Please check your API key.`);
    } else if (error.status === 429) {
      throw new Error(`Rate limit exceeded for ${providerInfo}. Please try again later.`);
    } else if (error.status === 500) {
      throw new Error(`${providerInfo} service error. Please try again later.`);
    }
    
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}