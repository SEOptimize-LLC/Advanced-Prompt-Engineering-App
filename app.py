import streamlit as st
import json
import re
from datetime import datetime
import pandas as pd
from typing import Dict, List, Tuple
import hashlib
import base64
from io import BytesIO
import os

# Page configuration
st.set_page_config(
    page_title="Advanced Prompt Engineering Tool",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, modern design
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    .technique-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: #f0f2ff;
        color: #667eea;
        border-radius: 20px;
        font-size: 0.875rem;
        margin: 0.25rem;
    }
    .provider-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px 10px 0 0;
        font-weight: bold;
    }
    .optimized-prompt {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0 0 10px 10px;
        padding: 1.5rem;
    }
    div[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'prompt_history' not in st.session_state:
    st.session_state.prompt_history = []
if 'current_prompt' not in st.session_state:
    st.session_state.current_prompt = ""
if 'optimized_prompts' not in st.session_state:
    st.session_state.optimized_prompts = {}
if 'applied_techniques_dict' not in st.session_state:
    st.session_state.applied_techniques_dict = {}
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {}
if 'optimization_mode' not in st.session_state:
    st.session_state.optimization_mode = "auto"

# Load API keys from Streamlit secrets
def load_api_keys():
    """Load API keys from Streamlit secrets or environment variables"""
    api_keys = {}
    
    if hasattr(st, 'secrets'):
        try:
            if 'api_keys' in st.secrets:
                api_keys['openai'] = st.secrets.api_keys.get('OPENAI_API_KEY', '')
                api_keys['anthropic'] = st.secrets.api_keys.get('ANTHROPIC_API_KEY', '')
                api_keys['google'] = st.secrets.api_keys.get('GOOGLE_API_KEY', '')
        except:
            pass
    
    # Fallback to environment variables
    if not api_keys.get('openai'):
        api_keys['openai'] = os.getenv('OPENAI_API_KEY', '')
    if not api_keys.get('anthropic'):
        api_keys['anthropic'] = os.getenv('ANTHROPIC_API_KEY', '')
    if not api_keys.get('google'):
        api_keys['google'] = os.getenv('GOOGLE_API_KEY', '')
    
    return api_keys

st.session_state.api_keys = load_api_keys()

# Simplified prompt engineering techniques
OPTIMIZATION_MODES = {
    "auto": {
        "name": "🤖 Auto-Optimize",
        "description": "Automatically apply best techniques based on prompt analysis",
        "icon": "🤖"
    },
    "reasoning": {
        "name": "🧠 Enhanced Reasoning",
        "description": "Best for complex problem-solving, analysis, and logical tasks",
        "icon": "🧠"
    },
    "creative": {
        "name": "🎨 Creative Writing",
        "description": "Optimized for stories, content creation, and imaginative tasks",
        "icon": "🎨"
    },
    "coding": {
        "name": "💻 Code Generation",
        "description": "Structured for programming, debugging, and technical tasks",
        "icon": "💻"
    },
    "data": {
        "name": "📊 Data Analysis",
        "description": "Formatted for data science, statistics, and insights",
        "icon": "📊"
    },
    "minimal": {
        "name": "⚡ Minimal Enhancement",
        "description": "Light optimization for simple, straightforward tasks",
        "icon": "⚡"
    }
}

# Provider configurations
PROVIDERS = {
    "Claude": {
        "color": "#764ba2",
        "strengths": ["Complex reasoning", "Long context", "Structured output"],
        "model": "Claude 3"
    },
    "GPT": {
        "color": "#10a37f",
        "strengths": ["Versatility", "Function calling", "JSON mode"],
        "model": "GPT-4"
    },
    "Gemini": {
        "color": "#4285f4",
        "strengths": ["Multimodal", "Long context", "Speed"],
        "model": "Gemini 1.5"
    }
}

def analyze_prompt_intent(prompt: str) -> str:
    """Analyze prompt to determine best optimization mode"""
    prompt_lower = prompt.lower()
    
    # Check for coding indicators
    if any(word in prompt_lower for word in ['code', 'function', 'program', 'debug', 'implement', 'algorithm', 'script']):
        return "coding"
    
    # Check for data/analysis indicators
    if any(word in prompt_lower for word in ['analyze', 'data', 'statistics', 'metrics', 'visualize', 'chart', 'graph']):
        return "data"
    
    # Check for creative indicators
    if any(word in prompt_lower for word in ['story', 'write', 'creative', 'poem', 'article', 'blog', 'narrative']):
        return "creative"
    
    # Check for reasoning indicators
    if any(word in prompt_lower for word in ['explain', 'why', 'how', 'solve', 'reason', 'think', 'logic']):
        return "reasoning"
    
    # Default to auto for general prompts
    return "auto"

def optimize_prompt(original_prompt: str, mode: str, provider: str) -> Tuple[str, List[str]]:
    """Apply optimization techniques based on mode and provider"""
    
    techniques_applied = []
    
    # Auto mode - analyze and apply best techniques
    if mode == "auto":
        detected_mode = analyze_prompt_intent(original_prompt)
        if detected_mode != "auto":
            mode = detected_mode
    
    # Apply mode-specific optimizations
    if mode == "reasoning":
        techniques_applied = ["Chain of Thought", "Step-by-step reasoning", "Self-verification"]
        
        if provider == "Claude":
            optimized = f"""<context>
You are an expert problem solver with strong analytical and reasoning capabilities.
</context>

<task>
{original_prompt}
</task>

<approach>
Please approach this systematically:
1. First, break down the problem into its core components
2. Analyze each component carefully
3. Show your reasoning step-by-step
4. Verify your logic at each step
5. Provide a clear, well-reasoned conclusion
</approach>

Let's think through this step-by-step."""
        
        elif provider == "GPT":
            optimized = f"""You are an expert analyst. Please solve this step-by-step.

Task: {original_prompt}

Instructions:
1. Break down the problem systematically
2. Show your reasoning at each step
3. Consider alternative approaches
4. Validate your conclusions

Please think through this carefully and show your work."""
        
        else:  # Gemini
            optimized = f"""**Expert Analysis Required**

**Task:** {original_prompt}

**Approach:**
• Break down into components
• Analyze each part thoroughly
• Show step-by-step reasoning
• Verify conclusions

Please provide a detailed, logical analysis."""
    
    elif mode == "creative":
        techniques_applied = ["Creative persona", "Vivid descriptions", "Narrative structure"]
        
        if provider == "Claude":
            optimized = f"""<role>
You are a talented creative writer with a gift for engaging storytelling and vivid descriptions.
</role>

<task>
{original_prompt}
</task>

<guidelines>
• Use rich, descriptive language
• Create engaging narrative flow
• Include sensory details
• Build emotional connection
• Maintain consistent tone and style
</guidelines>

Please create something original and captivating."""
        
        elif provider == "GPT":
            optimized = f"""You are a creative writing expert. 

Task: {original_prompt}

Style Guidelines:
- Use vivid, engaging language
- Create compelling narrative
- Include rich details
- Maintain consistent voice
- Focus on originality

Please craft something memorable and impactful."""
        
        else:  # Gemini
            optimized = f"""**Creative Writing Task**

**Request:** {original_prompt}

**Creative Parameters:**
• Engaging and original content
• Rich descriptive language
• Strong narrative structure
• Emotional resonance

Craft something unique and compelling."""
    
    elif mode == "coding":
        techniques_applied = ["Code structure", "Documentation", "Error handling", "Best practices"]
        
        if provider == "Claude":
            optimized = f"""<role>
You are an expert software engineer with deep knowledge of best practices and clean code principles.
</role>

<task>
{original_prompt}
</task>

<requirements>
• Write clean, efficient code
• Include detailed comments
• Handle edge cases and errors
• Follow language best practices
• Provide usage examples
• Explain time/space complexity if relevant
</requirements>

Please provide a complete, production-ready solution."""
        
        elif provider == "GPT":
            optimized = f"""You are an expert programmer.

Task: {original_prompt}

Requirements:
1. Clean, well-documented code
2. Error handling included
3. Follow best practices
4. Include usage examples
5. Explain approach and complexity

Provide production-quality code with explanations."""
        
        else:  # Gemini
            optimized = f"""**Programming Task**

**Requirement:** {original_prompt}

**Code Standards:**
• Clean, readable code
• Comprehensive comments
• Error handling
• Best practices
• Example usage

Deliver professional-grade code with documentation."""
    
    elif mode == "data":
        techniques_applied = ["Statistical rigor", "Visualization suggestions", "Insights extraction"]
        
        if provider == "Claude":
            optimized = f"""<role>
You are a data scientist with expertise in statistical analysis and data visualization.
</role>

<task>
{original_prompt}
</task>

<analysis_framework>
1. Data overview and summary statistics
2. Pattern and trend identification
3. Statistical significance testing
4. Visualization recommendations
5. Actionable insights and recommendations
</analysis_framework>

Please provide a thorough data analysis with clear insights."""
        
        elif provider == "GPT":
            optimized = f"""You are a data analysis expert.

Task: {original_prompt}

Analysis Framework:
- Summary statistics
- Trend analysis
- Pattern recognition
- Visualization suggestions
- Key insights
- Recommendations

Provide comprehensive analysis with actionable insights."""
        
        else:  # Gemini
            optimized = f"""**Data Analysis Task**

**Objective:** {original_prompt}

**Analysis Structure:**
• Statistical summary
• Trends and patterns
• Key findings
• Visualization recommendations
• Actionable insights

Deliver thorough analysis with clear conclusions."""
    
    else:  # minimal
        techniques_applied = ["Clear instructions", "Structured format"]
        
        if provider == "Claude":
            optimized = f"""<task>
{original_prompt}
</task>

Please provide a clear, comprehensive response."""
        
        elif provider == "GPT":
            optimized = f"""Task: {original_prompt}

Please provide a helpful and accurate response."""
        
        else:  # Gemini
            optimized = f"""**Task:** {original_prompt}

Please provide a clear and helpful response."""
    
    return optimized, techniques_applied

def calculate_metrics(text: str) -> Dict:
    """Calculate text metrics"""
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    sentences = re.findall(r'[.!?]+', text)
    sentence_count = len(sentences) if sentences else 1
    
    # Estimate tokens (rough approximation)
    estimated_tokens = int(word_count * 1.3)
    
    # Simple clarity score based on average sentence length
    avg_sentence_length = word_count / sentence_count
    if avg_sentence_length < 10:
        clarity = "Very Clear"
    elif avg_sentence_length < 20:
        clarity = "Clear"
    elif avg_sentence_length < 30:
        clarity = "Moderate"
    else:
        clarity = "Complex"
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "sentence_count": sentence_count,
        "estimated_tokens": estimated_tokens,
        "clarity": clarity
    }

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">Advanced Prompt Engineering Tool</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Transform your prompts using proven AI optimization techniques</p>', unsafe_allow_html=True)
    
    # Sidebar - Simplified
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Optimization mode selection with cards
        st.markdown("#### Optimization Mode")
        
        mode = st.radio(
            "Choose optimization style:",
            options=list(OPTIMIZATION_MODES.keys()),
            format_func=lambda x: f"{OPTIMIZATION_MODES[x]['icon']} {OPTIMIZATION_MODES[x]['name'].replace(OPTIMIZATION_MODES[x]['icon'], '').strip()}",
            index=0,
            help="Select how you want your prompt optimized"
        )
        
        st.info(OPTIMIZATION_MODES[mode]['description'])
        
        st.divider()
        
        # Target providers
        st.markdown("#### Target AI Models")
        providers = st.multiselect(
            "Select providers:",
            options=list(PROVIDERS.keys()),
            default=["Claude", "GPT"],
            help="Choose which AI models to optimize for"
        )
        
        st.divider()
        
        # API Status (collapsed by default)
        with st.expander("API Status", expanded=False):
            if st.session_state.api_keys.get('anthropic'):
                st.success("✓ Claude API ready")
            else:
                st.info("○ Claude API not configured")
            
            if st.session_state.api_keys.get('openai'):
                st.success("✓ GPT API ready")
            else:
                st.info("○ GPT API not configured")
            
            if st.session_state.api_keys.get('google'):
                st.success("✓ Gemini API ready")
            else:
                st.info("○ Gemini API not configured")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["✨ Optimize", "📊 Analysis", "📚 Examples"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Enter Your Prompt")
            prompt_input = st.text_area(
                "What would you like the AI to do?",
                value=st.session_state.current_prompt,
                height=150,
                placeholder="Example: Write a blog post about the future of AI in healthcare...",
                label_visibility="hidden"
            )
        
        with col2:
            if prompt_input:
                metrics = calculate_metrics(prompt_input)
                
                # Display metrics in a clean card
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("### 📊 Quick Stats")
                st.metric("Words", metrics['word_count'])
                st.metric("Clarity", metrics['clarity'])
                st.metric("Est. Tokens", metrics['estimated_tokens'])
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Optimize button
        if st.button("🚀 Optimize My Prompt", type="primary", use_container_width=True):
            if prompt_input and providers:
                with st.spinner("Applying advanced optimization techniques..."):
                    optimized_prompts = {}
                    techniques_dict = {}
                    
                    for provider in providers:
                        optimized, techniques = optimize_prompt(prompt_input, mode, provider)
                        optimized_prompts[provider] = optimized
                        techniques_dict[provider] = techniques
                    
                    st.session_state.optimized_prompts = optimized_prompts
                    st.session_state.applied_techniques_dict = techniques_dict
                    st.session_state.current_prompt = prompt_input
                    
                    # Add to history
                    st.session_state.prompt_history.append({
                        "timestamp": datetime.now(),
                        "original": prompt_input,
                        "optimized": optimized_prompts,
                        "techniques": techniques_dict,
                        "mode": mode
                    })
                    
                    st.success("✨ Optimization complete!")
            elif not providers:
                st.error("Please select at least one provider from the sidebar")
            else:
                st.error("Please enter a prompt to optimize")
        
        # Display optimized prompts
        if st.session_state.optimized_prompts:
            st.markdown("---")
            st.markdown("### 🎯 Optimized Prompts")
            
            # Show applied techniques
            st.markdown("#### Applied Techniques")
            cols = st.columns(len(st.session_state.applied_techniques_dict))
            for i, (provider, techniques) in enumerate(st.session_state.applied_techniques_dict.items()):
                with cols[i]:
                    st.markdown(f"**{provider}:**")
                    for tech in techniques:
                        st.markdown(f'<span class="technique-badge">{tech}</span>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display optimized prompts in columns
            cols = st.columns(len(st.session_state.optimized_prompts))
            
            for i, (provider, optimized) in enumerate(st.session_state.optimized_prompts.items()):
                with cols[i]:
                    # Provider header with color
                    color = PROVIDERS[provider]['color']
                    st.markdown(f"""
                        <div style="background: {color}; color: white; padding: 10px; border-radius: 10px 10px 0 0; text-align: center; font-weight: bold;">
                            {provider} Optimized
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Optimized prompt in a text area
                    st.text_area(
                        f"{provider} Version",
                        value=optimized,
                        height=300,
                        key=f"display_{provider}",
                        label_visibility="hidden"
                    )
                    
                    # Action buttons
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.download_button(
                            label="📥 Download",
                            data=optimized,
                            file_name=f"{provider.lower()}_optimized.txt",
                            mime="text/plain",
                            key=f"download_{provider}"
                        )
                    with col_b:
                        if st.button("📋 Copy", key=f"copy_{provider}"):
                            st.code(optimized, language="text")
                            st.info("Select all (Ctrl+A) and copy (Ctrl+C)")
    
    with tab2:
        st.markdown("### 📊 Prompt Analysis")
        
        if prompt_input:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Structure Analysis")
                metrics = calculate_metrics(prompt_input)
                st.metric("Words", metrics['word_count'])
                st.metric("Sentences", metrics['sentence_count'])
                st.metric("Characters", metrics['char_count'])
            
            with col2:
                st.markdown("#### Detected Intent")
                detected = analyze_prompt_intent(prompt_input)
                mode_info = OPTIMIZATION_MODES.get(detected, OPTIMIZATION_MODES["auto"])
                st.info(f"{mode_info['icon']} {mode_info['name']}")
                st.caption(mode_info['description'])
            
            with col3:
                st.markdown("#### Recommendations")
                if metrics['word_count'] < 15:
                    st.warning("💡 Add more context for better results")
                elif metrics['word_count'] > 200:
                    st.info("✂️ Consider breaking into smaller tasks")
                else:
                    st.success("✓ Good prompt length")
                
                if metrics['clarity'] in ["Very Clear", "Clear"]:
                    st.success("✓ Clear structure")
                else:
                    st.warning("💡 Simplify sentence structure")
        else:
            st.info("Enter a prompt to see analysis")
    
    with tab3:
        st.markdown("### 📚 Example Prompts")
        
        examples = {
            "Data Analysis": "Analyze sales data from Q1-Q4 2023, identify trends, seasonality patterns, and provide recommendations for Q1 2024 strategy",
            "Creative Writing": "Write a short story about a time traveler who can only move forward in 5-minute increments",
            "Code Generation": "Create a Python function that efficiently finds all prime numbers up to n using the Sieve of Eratosthenes",
            "Problem Solving": "Design a sustainable water management system for a city of 500,000 people in a semi-arid climate",
            "Simple Question": "What are the main benefits of renewable energy?"
        }
        
        st.markdown("Click any example to load it:")
        
        cols = st.columns(2)
        for i, (title, prompt) in enumerate(examples.items()):
            with cols[i % 2]:
                if st.button(f"📝 {title}", key=f"example_{i}", use_container_width=True):
                    st.session_state.current_prompt = prompt
                    st.rerun()
                with st.expander(f"Preview: {title}"):
                    st.write(prompt)

if __name__ == "__main__":
    main()
