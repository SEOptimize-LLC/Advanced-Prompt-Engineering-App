# Advanced Prompt Engineering Tool 🚀

A powerful Streamlit application for optimizing prompts across all major LLM providers (Anthropic, OpenAI, and Google) using proven prompt engineering techniques.

## Features ✨

### Core Functionality
- **🎯 Smart Prompt Optimization** - AI-powered suggestions using Chain-of-Thought, Few-Shot Learning, and more
- **⏱️ Real-time Analysis** - Word count, character count, clarity scoring, readability metrics
- **🛠️ Provider-specific Formatting** - Optimized for Claude, GPT, and Gemini models
- **📊 Token & Cost Estimation** - Real-time cost calculations for each provider
- **📚 Template Library** - Pre-built templates for common tasks
- **💾 Export Options** - JSON export, copy functionality, and report generation
- **📈 Prompt History** - Track all your optimizations with search functionality

### Advanced Features
- **Provider Comparison** - Side-by-side analysis with cost-benefit recommendations
- **Template System** - Customizable templates with variable substitution
- **Advanced Analytics** - Keyword density, readability scores, issue detection
- **Multi-tab Interface** - Organized workflow across multiple specialized tabs

## Installation 🛠️

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/advanced-prompt-engineering-tool.git
cd advanced-prompt-engineering-tool
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API keys (Optional - for API testing features)**

Create a `.streamlit/secrets.toml` file in your project directory:

```toml
# .streamlit/secrets.toml

[api_keys]
OPENAI_API_KEY = "your-openai-api-key-here"
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
GOOGLE_API_KEY = "your-google-api-key-here"

# Optional: Set default models
[models]
default_openai_model = "gpt-4-turbo-preview"
default_anthropic_model = "claude-3-opus-20240229"
default_google_model = "gemini-1.5-pro"
```

4. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Deployment 🚀

### Deploy to Streamlit Cloud

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set up secrets in the Streamlit Cloud dashboard
   - Click Deploy!

### Deploy to Heroku

1. **Create `Procfile`**
```
web: sh setup.sh && streamlit run app.py
```

2. **Create `setup.sh`**
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

3. **Deploy**
```bash
heroku create your-app-name
git push heroku main
```

## Usage Guide 📖

### 1. Optimize Tab
- Enter your prompt in the text area
- Select target providers from the sidebar
- Choose optimization focus areas
- Click "Optimize Prompt" to generate enhanced versions
- Copy optimized prompts with one click

### 2. Templates Tab
- Browse pre-built templates for common tasks
- Customize templates with your variables
- Generate task-specific prompts instantly

### 3. Analysis Tab
- View detailed metrics about your prompt
- Get AI-powered suggestions for improvement
- Analyze readability and complexity scores
- Identify potential issues

### 4. Compare Tab
- Compare optimized prompts across providers
- View cost-benefit analysis
- Get recommendations for best value and clarity

### 5. History Tab
- Browse your prompt optimization history
- Search and filter past prompts
- Reuse successful optimizations
- Export history as JSON

## Prompt Engineering Techniques Applied 🧠

The tool automatically applies these proven techniques:

### Basic Optimizations
- **Clear Instructions** - Converts vague prompts to specific, actionable instructions
- **Role Definition** - Adds appropriate persona/system prompts
- **Output Formatting** - Specifies structure, length, and style
- **Delimiter Usage** - Adds XML tags or markdown for clarity

### Advanced Techniques
- **Chain-of-Thought (CoT)** - Adds step-by-step reasoning
- **Few-Shot Learning** - Injects relevant examples
- **Task Decomposition** - Breaks complex prompts into subtasks
- **Self-Consistency** - Generates multiple reasoning paths
- **ReAct Pattern** - Combines reasoning with action steps

### Provider-Specific
- **Claude/Anthropic**: XML tags, thinking tags, structured formatting
- **GPT/OpenAI**: System messages, function calling, JSON mode
- **Gemini/Google**: Multimodal optimization, long context handling

## Configuration ⚙️

### Customization Options

Edit the following in `app.py`:

```python
# Model configurations
MODELS = {
    "Anthropic": {
        "models": ["Claude 3 Opus", "Claude 3 Sonnet"],
        "max_tokens": 200000,
        # Add your models
    }
}

# Focus areas
focus_areas = [
    "Structure",
    "Clarity", 
    "Specificity",
    # Add custom areas
]
```

## API Integration 🔌

To enable API testing features:

1. Add your API keys to `.streamlit/secrets.toml`
2. The app will automatically enable providers with valid keys
3. Test prompts directly through the interface
4. Compare outputs side-by-side

## Contributing 🤝

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## Troubleshooting 🔧

### Common Issues

**App won't start**
- Ensure Python 3.8+ is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify no port conflicts on 8501

**API features not working**
- Verify API keys are correctly set in secrets
- Check API key permissions and quotas
- Ensure proper formatting in secrets.toml

**Performance issues**
- Clear browser cache
- Restart Streamlit server
- Check system resources

## License 📄

MIT License - see LICENSE file for details

## Support 💬

- Report issues on [GitHub Issues](https://github.com/yourusername/repo/issues)
- Documentation: [Wiki](https://github.com/yourusername/repo/wiki)
- Email: support@yourapp.com

## Roadmap 🗺️

### Planned Features
- [ ] Batch prompt processing
- [ ] Custom technique creation
- [ ] Team collaboration features
- [ ] Advanced A/B testing
- [ ] Integration with LangChain
- [ ] Prompt versioning system
- [ ] Performance tracking dashboard
- [ ] Custom model fine-tuning support

## Acknowledgments 🙏

Built using:
- [Streamlit](https://streamlit.io/)
- [OpenAI API](https://openai.com/api/)
- [Anthropic API](https://anthropic.com/)
- [Google AI](https://ai.google/)

Based on research from:
- OpenAI's Prompt Engineering Guide
- Anthropic's Claude Best Practices
- Google's Gemini Documentation
- Academic papers on CoT, ToT, and ReAct

---

**Made with ❤️ for the AI community**