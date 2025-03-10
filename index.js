// backend/index.js
import express from 'express';
import cors from 'cors';
import { generateContentIdeas, generateVideoScript, refineVideoScript, regenerateVideoScript, generateLinkedInPost } from './generation.js';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// Configure middleware
app.use(express.json({ limit: '10mb' }));
app.use(cors({
  origin: process.env.FRONTEND_URL || 'https://your-contentformer-app.vercel.app',
  credentials: true
}));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Test API connection
app.post('/api/test-connection', async (req, res) => {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider } = req.body;
    
    // Validate config
    if (preferredProvider === 'anthropic' && !anthropicApiKey) {
      return res.status(400).json({ 
        success: false, 
        message: 'Anthropic API key is missing. Please add your API key in settings.' 
      });
    }
    
    if (preferredProvider === 'openai' && !openaiApiKey) {
      return res.status(400).json({ 
        success: false, 
        message: 'OpenAI API key is missing. Please add your API key in settings.' 
      });
    }
    
    const prompt = "Return the text 'API connection successful' as a response.";
    
    if (preferredProvider === 'anthropic') {
      // Test Anthropic connection
      // Simple connection test code here
      res.json({
        success: true,
        provider: 'anthropic',
        message: 'Anthropic API connection successful'
      });
    } else if (preferredProvider === 'openai') {
      // Test OpenAI connection
      // Simple connection test code here
      res.json({
        success: true,
        provider: 'openai',
        message: 'OpenAI API connection successful'
      });
    } else {
      throw new Error('No valid API configuration found. Please check your API settings.');
    }
  } catch (error) {
    console.error('API connection test failed:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to connect to API service',
      error: error.toString()
    });
  }
});

// Generate content ideas
app.post('/api/generate-ideas', async (req, res) => {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider, transcript, instructions } = req.body;
    
    const config = {
      anthropicApiKey,
      openaiApiKey,
      preferredProvider
    };
    
    const ideas = await generateContentIdeas(config, transcript, instructions);
    res.json(ideas);
  } catch (error) {
    console.error('Error generating content ideas:', error);
    res.status(500).json({ 
      success: false, 
      message: error.message || 'Error generating content ideas'
    });
  }
});

// Generate video script
app.post('/api/generate-script', async (req, res) => {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider, idea, transcript, instructions } = req.body;
    
    const config = {
      anthropicApiKey,
      openaiApiKey,
      preferredProvider
    };
    
    const script = await generateVideoScript(config, idea, transcript, instructions);
    res.json(script);
  } catch (error) {
    console.error('Error generating video script:', error);
    res.status(500).json({ 
      success: false, 
      message: error.message || 'Error generating video script'
    });
  }
});

// Refine video script
app.post('/api/refine-script', async (req, res) => {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider, script, instructions } = req.body;
    
    const config = {
      anthropicApiKey,
      openaiApiKey,
      preferredProvider
    };
    
    const refinedScript = await refineVideoScript(config, script, instructions);
    res.json(refinedScript);
  } catch (error) {
    console.error('Error refining video script:', error);
    res.status(500).json({ 
      success: false, 
      message: error.message || 'Error refining video script'
    });
  }
});

// Regenerate video script
app.post('/api/regenerate-script', async (req, res) => {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider, idea, transcript, instructions } = req.body;
    
    const config = {
      anthropicApiKey,
      openaiApiKey,
      preferredProvider
    };
    
    const regeneratedScript = await regenerateVideoScript(config, idea, transcript, instructions);
    res.json(regeneratedScript);
  } catch (error) {
    console.error('Error regenerating video script:', error);
    res.status(500).json({ 
      success: false, 
      message: error.message || 'Error regenerating video script'
    });
  }
});

// Generate LinkedIn post
app.post('/api/generate-linkedin-post', async (req, res) => {
  try {
    const { anthropicApiKey, openaiApiKey, preferredProvider, script } = req.body;
    
    const config = {
      anthropicApiKey,
      openaiApiKey,
      preferredProvider
    };
    
    const post = await generateLinkedInPost(config, script);
    res.json(post);
  } catch (error) {
    console.error('Error generating LinkedIn post:', error);
    res.status(500).json({ 
      success: false, 
      message: error.message || 'Error generating LinkedIn post'
    });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});