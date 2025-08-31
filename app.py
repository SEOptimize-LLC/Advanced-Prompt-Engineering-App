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

# Custom CSS for better styling (removed problematic emojis)
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .provider-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .technique-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .copy-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
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
if 'saved_templates' not in st.session_state:
    st.session_state.saved_templates = []
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {}
if 'applied_techniques' not in st.session_state:
    st.session_state.applied_techniques = []

# Load API keys from Streamlit secrets (if available)
def load_api_keys():
    """Load API keys from Streamlit secrets or environment variables"""
    api_keys = {}
    
    # Try to load from Streamlit secrets first
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

# Load API keys on startup
st.session_state.api_keys = load_api_keys()

# REAL Prompt Engineering Techniques based on best practices
PROMPT_TECHNIQUES = {
    "Claude Best Practices": {
        "xml_tags": {
            "name": "XML Tag Structure",
            "description": "Use XML tags for clear structure and parsing",
            "example": "Transform prompt into XML-tagged sections for clarity",
            "apply": lambda p: f"""<task>
{p}
</task>

<instructions>
Please provide a comprehensive response following these guidelines:
- Be specific and detailed in your answer
- Use structured formatting where appropriate
- Include examples when helpful
</instructions>"""
        },
        "thinking_tags": {
            "name": "Chain of Thought with Thinking Tags",
            "description": "Add thinking tags for complex reasoning",
            "example": "Encourages step-by-step reasoning",
            "apply": lambda p: f"""<task>
{p}
</task>

<thinking_process>
Before answering, please:
1. Break down the key components of this request
2. Consider multiple approaches
3. Identify potential challenges or edge cases
4. Formulate a comprehensive response
</thinking_process>

Please think through this step-by-step and provide your reasoning."""
        },
        "role_definition": {
            "name": "Clear Role Definition",
            "description": "Define a specific expert role",
            "example": "You are an expert in [domain]...",
            "apply": lambda p: f"""You are an expert assistant with deep knowledge across multiple domains. Your role is to provide accurate, helpful, and well-structured responses.

<task>
{p}
</task>

Approach this task with expertise and attention to detail."""
        },
        "prefill_technique": {
            "name": "Assistant Prefilling",
            "description": "Start the assistant's response to guide format",
            "example": "Begin response with structure",
            "apply": lambda p: f"""{p}

Please structure your response as follows:
1. **Overview**: Brief summary of the approach
2. **Detailed Analysis**: Step-by-step breakdown
3. **Key Insights**: Important points to consider
4. **Recommendations**: Actionable next steps

Let me help you with this:"""
        }
    },
    "OpenAI Best Practices": {
        "system_message": {
            "name": "System Message Optimization",
            "description": "Clear system-level instructions",
            "example": "Separate system context from user prompt",
            "apply": lambda p: f"""System: You are a helpful, accurate, and creative AI assistant. Follow these principles:
- Provide detailed, well-structured responses
- Use examples to illustrate complex points
- Admit uncertainty when appropriate
- Focus on being helpful and constructive

User request:
{p}"""
        },
        "few_shot": {
            "name": "Few-Shot Examples",
            "description": "Provide examples of desired output",
            "example": "Show 2-3 examples of good responses",
            "apply": lambda p: f"""Here are examples of the type of response I'm looking for:

Example 1:
Input: [Similar task]
Output: [Detailed, well-structured response]

Example 2:
Input: [Another similar task]
Output: [Another detailed response]

Now, for my actual request:
{p}

Please follow the same detailed, structured approach as shown in the examples."""
        },
        "json_mode": {
            "name": "Structured Output Format",
            "description": "Request specific output format",
            "example": "Specify JSON or markdown structure",
            "apply": lambda p: f"""{p}

Please provide your response in the following structured format:
```
### Main Points
- Point 1: [Details]
- Point 2: [Details]

### Analysis
[Your detailed analysis]

### Conclusion
[Summary and recommendations]
```"""
        },
        "temperature_guidance": {
            "name": "Temperature and Parameter Hints",
            "description": "Suggest optimal parameters",
            "example": "Indicate if creative or factual response needed",
            "apply": lambda p: f"""[This task requires balanced creativity and accuracy]

{p}

Note: Please provide a response that balances factual accuracy with creative insights."""
        }
    },
    "Universal Techniques": {
        "chain_of_thought": {
            "name": "Chain of Thought (CoT)",
            "description": "Add 'think step by step' instruction",
            "example": "Let's approach this step-by-step",
            "apply": lambda p: f"""{p}

Let's think through this step-by-step:
1. First, identify the key components
2. Then, analyze each part carefully
3. Finally, synthesize a comprehensive response

Please show your reasoning process."""
        },
        "task_decomposition": {
            "name": "Task Decomposition",
            "description": "Break complex tasks into subtasks",
            "example": "Divide into manageable components",
            "apply": lambda p: f"""This is a complex request that we'll break down into parts:

Main Task: {p}

Let's address this by:
Part A: [First component]
Part B: [Second component]
Part C: [Third component]

Please address each part thoroughly and then provide an integrated conclusion."""
        },
        "constraints_and_requirements": {
            "name": "Clear Constraints",
            "description": "Specify limitations and requirements",
            "example": "Must/must not instructions",
            "apply": lambda p: f"""{p}

Requirements:
- Be comprehensive but concise
- Use specific examples
- Cite sources when making claims
- Structure the response clearly
- Focus on practical applications

Constraints:
- Avoid jargon without explanation
- Keep response focused on the query
- Ensure accuracy over speculation"""
        },
        "self_consistency": {
            "name": "Self-Consistency Check",
            "description": "Request verification of response",
            "example": "Double-check accuracy",
            "apply": lambda p: f"""{p}

After providing your response, please:
1. Verify the accuracy of any facts or figures
2. Ensure logical consistency throughout
3. Check that all parts of the question are addressed
4. Confirm the response is helpful and actionable"""
        },
        "role_play_expert": {
            "name": "Expert Role-Playing",
            "description": "Assume specific expert persona",
            "example": "Act as domain expert",
            "apply": lambda p: f"""You are a world-class expert in the relevant field for this query. Drawing on your extensive knowledge and experience:

{p}

Please provide an expert-level response that demonstrates deep understanding and practical insights."""
        },
        "emotional_appeal": {
            "name": "Motivation Enhancement",
            "description": "Add importance/urgency to prompt",
            "example": "This is important for my project",
            "apply": lambda p: f"""{p}

This is a critical task that requires your best analysis. Please provide a thorough, thoughtful response that addresses all aspects of the query. Your insights will be valuable for important decision-making."""
        }
    },
    "Advanced Techniques": {
        "tree_of_thoughts": {
            "name": "Tree of Thoughts (ToT)",
            "description": "Explore multiple solution paths",
            "example": "Consider alternative approaches",
            "apply": lambda p: f"""{p}

Please approach this by:
1. Considering multiple possible solutions or interpretations
2. Evaluating the pros and cons of each approach
3. Selecting the most promising path(s)
4. Providing a detailed exploration of the best option(s)

Show your thought process for each alternative considered."""
        },
        "react_pattern": {
            "name": "ReAct (Reasoning + Acting)",
            "description": "Combine reasoning with action steps",
            "example": "Think, then act, then observe",
            "apply": lambda p: f"""{p}

Use the following approach:
Thought: What do I need to understand first?
Action: What information or analysis is needed?
Observation: What insights does this provide?
Thought: Based on this, what's next?
[Continue until complete]

Please show this reasoning-action cycle in your response."""
        },
        "meta_prompting": {
            "name": "Meta-Prompting",
            "description": "Prompt about how to approach the prompt",
            "example": "First improve the question itself",
            "apply": lambda p: f"""Before answering, let's first ensure we're addressing the right question:

Original request: {p}

Please:
1. Identify any ambiguities or assumptions in the request
2. Clarify what would make the most helpful response
3. Then provide a comprehensive answer to the refined question"""
        },
        "analogical_reasoning": {
            "name": "Analogical Reasoning",
            "description": "Use analogies and comparisons",
            "example": "Relate to familiar concepts",
            "apply": lambda p: f"""{p}

In your response:
1. Draw analogies to similar, well-understood concepts
2. Use comparative analysis where helpful
3. Provide concrete examples and metaphors
4. Connect abstract ideas to practical applications"""
        }
    }
}

# Model configurations with best practices
MODELS = {
    "Anthropic": {
        "models": ["Claude 3 Opus", "Claude 3 Sonnet", "Claude 3.5 Sonnet", "Claude 3 Haiku"],
        "max_tokens": 200000,
        "best_techniques": ["xml_tags", "thinking_tags", "role_definition", "prefill_technique", "chain_of_thought"],
        "pricing": {"input": 0.015, "output": 0.075}
    },
    "OpenAI": {
        "models": ["GPT-4 Turbo", "GPT-4", "GPT-3.5 Turbo"],
        "max_tokens": 128000,
        "best_techniques": ["system_message", "few_shot", "json_mode", "chain_of_thought", "task_decomposition"],
        "pricing": {"input": 0.01, "output": 0.03}
    },
    "Google": {
        "models": ["Gemini 1.5 Pro", "Gemini 1.5 Flash", "Gemini 1.0 Pro"],
        "max_tokens": 2000000,
        "best_techniques": ["chain_of_thought", "task_decomposition", "role_play_expert", "constraints_and_requirements"],
        "pricing": {"input": 0.00125, "output": 0.005}
    }
}

# Utility functions
def calculate_metrics(text: str) -> Dict:
    """Calculate various text metrics"""
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len(re.findall(r'[.!?]+', text))
    avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)
    
    # Clarity score (simplified heuristic)
    clarity_score = min(100, max(0, 100 - abs(15 - avg_word_length) * 5 - abs(20 - (word_count / max(sentence_count, 1))) * 2))
    
    # Estimate tokens (rough approximation)
    estimated_tokens = int(word_count * 1.3)
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "sentence_count": sentence_count,
        "avg_word_length": round(avg_word_length, 2),
        "clarity_score": round(clarity_score, 1),
        "estimated_tokens": estimated_tokens
    }

def apply_prompt_engineering_techniques(prompt: str, provider: str, selected_techniques: List[str]) -> Tuple[str, List[str]]:
    """Apply real prompt engineering techniques based on provider and selection"""
    
    optimized = prompt
    applied = []
    
    # Get provider-specific recommended techniques
    if provider in MODELS:
        recommended = MODELS[provider].get("best_techniques", [])
    else:
        recommended = ["chain_of_thought", "task_decomposition", "constraints_and_requirements"]
    
    # Apply selected techniques
    for technique_id in selected_techniques:
        # Find the technique across all categories
        for category, techniques in PROMPT_TECHNIQUES.items():
            if technique_id in techniques:
                technique = techniques[technique_id]
                optimized = technique["apply"](optimized)
                applied.append(f"{technique['name']} ({category})")
                break
    
    # If no techniques selected, apply recommended ones
    if not selected_techniques and recommended:
        for technique_id in recommended[:3]:  # Apply top 3 recommended
            for category, techniques in PROMPT_TECHNIQUES.items():
                if technique_id in techniques:
                    technique = techniques[technique_id]
                    optimized = technique["apply"](optimized)
                    applied.append(f"{technique['name']} ({category})")
                    break
    
    return optimized, applied

# Main App
def main():
    st.title("🚀 Advanced Prompt Engineering Tool")
    st.markdown("Transform your prompts using proven techniques from OpenAI, Anthropic, and Google's best practices")
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # API Key Status
        with st.expander("API Keys Status", expanded=False):
            st.markdown("**Configure in `.streamlit/secrets.toml`**")
            
            # Check API keys
            if st.session_state.api_keys.get('openai'):
                st.success("✓ OpenAI API configured")
            else:
                st.warning("✗ OpenAI API not configured")
            
            if st.session_state.api_keys.get('anthropic'):
                st.success("✓ Anthropic API configured")
            else:
                st.warning("✗ Anthropic API not configured")
            
            if st.session_state.api_keys.get('google'):
                st.success("✓ Google API configured")
            else:
                st.warning("✗ Google API not configured")
            
            st.info("API keys enable testing features")
        
        st.subheader("Select Providers")
        selected_providers = st.multiselect(
            "Target LLM Providers",
            options=list(MODELS.keys()),
            default=["Anthropic", "OpenAI"],
            help="Select which LLM providers to optimize for"
        )
        
        st.subheader("Prompt Engineering Techniques")
        st.markdown("Select techniques to apply:")
        
        selected_techniques = []
        
        # Display techniques by category
        for category, techniques in PROMPT_TECHNIQUES.items():
            st.markdown(f"**{category}**")
            for tech_id, tech_info in techniques.items():
                if st.checkbox(tech_info["name"], key=f"tech_{tech_id}", help=tech_info["description"]):
                    selected_techniques.append(tech_id)
        
        st.divider()
        
        # Quick presets
        st.subheader("Quick Presets")
        if st.button("Apply Best for Reasoning"):
            selected_techniques = ["chain_of_thought", "thinking_tags", "tree_of_thoughts", "self_consistency"]
        
        if st.button("Apply Best for Creative"):
            selected_techniques = ["role_play_expert", "analogical_reasoning", "few_shot", "emotional_appeal"]
        
        if st.button("Apply Best for Analysis"):
            selected_techniques = ["task_decomposition", "react_pattern", "meta_prompting", "xml_tags"]
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Optimize", "Templates", "Analysis", "Compare", "History"])
    
    with tab1:
        st.header("Prompt Optimization Workshop")
        
        # Input area
        col1, col2 = st.columns([3, 1])
        with col1:
            prompt_input = st.text_area(
                "Enter your prompt",
                value=st.session_state.current_prompt,
                height=200,
                placeholder="Enter your prompt here... Example: 'Write a blog post about AI'",
                key="main_prompt_input"
            )
        
        with col2:
            st.markdown("### Quick Stats")
            if prompt_input:
                metrics = calculate_metrics(prompt_input)
                st.metric("Words", metrics['word_count'])
                st.metric("Characters", metrics['char_count'])
                st.metric("Clarity Score", f"{metrics['clarity_score']}%")
                st.metric("Est. Tokens", metrics['estimated_tokens'])
        
        # Optimization button
        if st.button("🎯 Optimize Prompt", type="primary", use_container_width=True):
            if prompt_input:
                st.session_state.current_prompt = prompt_input
                
                # Generate optimized versions using REAL techniques
                with st.spinner("Applying advanced prompt engineering techniques..."):
                    optimized_prompts = {}
                    applied_techniques_dict = {}
                    
                    for provider in selected_providers:
                        optimized, applied = apply_prompt_engineering_techniques(
                            prompt_input, 
                            provider, 
                            selected_techniques
                        )
                        optimized_prompts[provider] = optimized
                        applied_techniques_dict[provider] = applied
                    
                    st.session_state.optimized_prompts = optimized_prompts
                    st.session_state.applied_techniques = applied_techniques_dict
                    
                    # Add to history
                    st.session_state.prompt_history.append({
                        "timestamp": datetime.now(),
                        "original": prompt_input,
                        "optimized": optimized_prompts,
                        "techniques": applied_techniques_dict,
                        "metrics": metrics
                    })
        
        # Display optimized versions
        if st.session_state.optimized_prompts:
            st.divider()
            st.subheader("🎯 Optimized Versions")
            
            # Show applied techniques
            if st.session_state.applied_techniques:
                with st.expander("Applied Techniques", expanded=True):
                    for provider, techniques in st.session_state.applied_techniques.items():
                        st.markdown(f"**{provider}:**")
                        for tech in techniques:
                            st.markdown(f"  • {tech}")
            
            for provider, optimized in st.session_state.optimized_prompts.items():
                with st.expander(f"**{provider}** - Optimized Prompt", expanded=True):
                    # Display the optimized prompt
                    st.text_area(
                        f"Optimized for {provider}",
                        value=optimized,
                        height=300,
                        key=f"opt_{provider}_display",
                        disabled=True
                    )
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        # Copy button - shows text area for manual copying
                        if st.button(f"📋 Show for Copy", key=f"copy_btn_{provider}"):
                            st.session_state[f"show_copy_{provider}"] = True
                    
                    with col2:
                        # Download button
                        st.download_button(
                            label="⬇ Download",
                            data=optimized,
                            file_name=f"{provider}_optimized_prompt.txt",
                            mime="text/plain",
                            key=f"download_{provider}"
                        )
                    
                    with col3:
                        # Metrics
                        opt_metrics = calculate_metrics(optimized)
                        est_cost = (opt_metrics['estimated_tokens'] / 1000) * MODELS[provider]["pricing"]["input"]
                        st.metric("Est. Cost", f"${est_cost:.4f}")
                    
                    # Show copyable text area when button clicked
                    if st.session_state.get(f"show_copy_{provider}", False):
                        st.info("Select all text below and copy (Ctrl+C / Cmd+C):")
                        st.code(optimized, language="text")
    
    with tab2:
        st.header("📚 Prompt Templates Library")
        
        # Pre-built optimized templates
        templates = {
            "Technical Documentation": {
                "description": "Optimized for creating technical docs",
                "template": """<task>
Create comprehensive technical documentation for {topic}
</task>

<requirements>
- Target audience: {audience_level} developers
- Documentation type: {doc_type}
- Include: Code examples, API references, troubleshooting guide
- Style: Clear, concise, technically accurate
</requirements>

<structure>
1. Overview and Purpose
2. Prerequisites and Setup
3. Core Concepts
4. Implementation Guide
5. API Reference
6. Examples and Use Cases
7. Troubleshooting
8. Best Practices
</structure>

Please think step-by-step through each section and provide detailed, practical information."""
            },
            "Data Analysis": {
                "description": "Optimized for data analysis tasks",
                "template": """You are an expert data analyst. 

<task>
Analyze the following data/scenario: {data_description}
</task>

<analysis_framework>
1. Data Overview: Summarize key characteristics
2. Statistical Analysis: Identify patterns, trends, outliers
3. Insights: Extract meaningful findings
4. Visualizations: Suggest appropriate charts/graphs
5. Recommendations: Provide actionable insights
</analysis_framework>

<requirements>
- Use statistical rigor
- Explain methodology
- Quantify findings where possible
- Consider limitations and biases
- Provide confidence levels for conclusions
</requirements>

Let's approach this systematically, showing all reasoning."""
            },
            "Creative Content": {
                "description": "Optimized for creative writing",
                "template": """You are a creative writing expert with deep understanding of narrative techniques.

<task>
Create {content_type} about {topic}
</task>

<parameters>
- Tone: {tone}
- Style: {style}
- Length: {length}
- Target audience: {audience}
</parameters>

<creative_guidelines>
1. Hook: Start with compelling opening
2. Development: Build narrative/argument progressively
3. Engagement: Use vivid language and sensory details
4. Structure: Maintain clear flow and pacing
5. Resolution: Provide satisfying conclusion
</creative_guidelines>

Please craft something original and engaging, showing your creative process."""
            },
            "Problem Solving": {
                "description": "Optimized for complex problem solving",
                "template": """<problem>
{problem_description}
</problem>

<context>
{additional_context}
</context>

Let's solve this using a structured approach:

1. **Problem Analysis**: Break down the core components
2. **Constraints Identification**: List limitations and requirements
3. **Solution Exploration**: Consider multiple approaches
4. **Trade-off Analysis**: Evaluate pros/cons of each
5. **Recommendation**: Select optimal solution with justification
6. **Implementation Plan**: Provide step-by-step execution guide

Please think through this methodically, showing your reasoning at each step."""
            }
        }
        
        # Template selection
        selected_template = st.selectbox(
            "Select Template",
            options=list(templates.keys())
        )
        
        if selected_template:
            template_data = templates[selected_template]
            st.info(template_data["description"])
            
            st.markdown("### Template Structure")
            st.code(template_data["template"], language="markdown")
            
            st.markdown("### Customize Template")
            
            # Extract variables
            template_text = template_data["template"]
            variables = re.findall(r'\{(\w+)\}', template_text)
            
            if variables:
                custom_values = {}
                cols = st.columns(min(3, len(variables)))
                for i, var in enumerate(variables):
                    with cols[i % len(cols)]:
                        custom_values[var] = st.text_input(
                            f"{var.replace('_', ' ').title()}",
                            key=f"template_var_{var}"
                        )
                
                if st.button("Generate Customized Prompt"):
                    try:
                        custom_prompt = template_text.format(**custom_values)
                        st.session_state.current_prompt = custom_prompt
                        st.success("Template applied! Go to Optimize tab to enhance further.")
                        st.text_area("Generated Prompt", value=custom_prompt, height=300)
                    except KeyError:
                        st.error("Please fill in all template variables")
    
    with tab3:
        st.header("📊 Prompt Analysis Dashboard")
        
        if prompt_input:
            # Advanced analysis
            col1, col2, col3 = st.columns(3)
            
            metrics = calculate_metrics(prompt_input)
            
            with col1:
                st.markdown("### Structure Analysis")
                st.metric("Sentences", metrics['sentence_count'])
                st.metric("Avg Word Length", metrics['avg_word_length'])
                st.metric("Words per Sentence", round(metrics['word_count'] / max(metrics['sentence_count'], 1), 1))
                
                # Improvement suggestions based on analysis
                suggestions = []
                if metrics['word_count'] < 20:
                    suggestions.append("🔍 Add more context and details")
                if metrics['sentence_count'] < 2:
                    suggestions.append("📝 Break into multiple sentences for clarity")
                if metrics['avg_word_length'] > 6:
                    suggestions.append("✂️ Simplify vocabulary for better understanding")
                if "?" not in prompt_input and "how" not in prompt_input.lower() and "what" not in prompt_input.lower():
                    suggestions.append("❓ Consider framing as a clear question")
                
                if suggestions:
                    st.markdown("### Improvement Suggestions")
                    for suggestion in suggestions:
                        st.info(suggestion)
            
            with col2:
                st.markdown("### Prompt Engineering Potential")
                
                # Analyze which techniques would be most beneficial
                recommendations = []
                
                if "step" not in prompt_input.lower() and "think" not in prompt_input.lower():
                    recommendations.append("**Chain of Thought**: Add step-by-step reasoning")
                
                if len(prompt_input.split()) > 50:
                    recommendations.append("**Task Decomposition**: Break into subtasks")
                
                if not any(role in prompt_input.lower() for role in ["you are", "act as", "expert"]):
                    recommendations.append("**Role Definition**: Add expert persona")
                
                if "example" not in prompt_input.lower():
                    recommendations.append("**Few-Shot Learning**: Include examples")
                
                for rec in recommendations[:4]:
                    st.markdown(f"• {rec}")
            
            with col3:
                st.markdown("### Complexity & Cost Analysis")
                
                # Token and cost estimation for each provider
                for provider in ["OpenAI", "Anthropic", "Google"]:
                    tokens = metrics['estimated_tokens']
                    cost = (tokens / 1000) * MODELS[provider]["pricing"]["input"]
                    
                    st.markdown(f"**{provider}**")
                    st.markdown(f"• Tokens: ~{tokens}")
                    st.markdown(f"• Est. Cost: ${cost:.5f}")
                    st.markdown("---")
    
    with tab4:
        st.header("🔄 Provider Comparison")
        
        if st.session_state.optimized_prompts:
            # Comparison metrics
            comparison_data = []
            
            for provider, optimized in st.session_state.optimized_prompts.items():
                metrics = calculate_metrics(optimized)
                techniques = st.session_state.applied_techniques.get(provider, [])
                
                comparison_data.append({
                    "Provider": provider,
                    "Original Length": len(prompt_input),
                    "Optimized Length": len(optimized),
                    "Improvement Factor": f"{(len(optimized) / len(prompt_input)):.1f}x",
                    "Techniques Applied": len(techniques),
                    "Est. Tokens": metrics['estimated_tokens'],
                    "Est. Cost": f"${(metrics['estimated_tokens'] / 1000) * MODELS[provider]['pricing']['input']:.5f}"
                })
            
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True)
            
            # Visual comparison
            st.subheader("Optimization Techniques by Provider")
            
            cols = st.columns(len(st.session_state.optimized_prompts))
            for i, (provider, techniques) in enumerate(st.session_state.applied_techniques.items()):
                with cols[i]:
                    st.markdown(f"### {provider}")
                    for tech in techniques:
                        st.markdown(f"✓ {tech}")
        else:
            st.info("Optimize a prompt first to see comparisons")
    
    with tab5:
        st.header("📈 Prompt History")
        
        if st.session_state.prompt_history:
            # Display history
            for i, item in enumerate(reversed(st.session_state.prompt_history[-10:])):
                with st.expander(
                    f"📝 {item['timestamp'].strftime('%Y-%m-%d %H:%M')} - {item['original'][:50]}...",
                    expanded=False
                ):
                    st.markdown("**Original Prompt:**")
                    st.text(item['original'])
                    
                    st.markdown("**Applied Techniques:**")
                    for provider, techs in item.get('techniques', {}).items():
                        st.markdown(f"*{provider}:* {', '.join(techs)}")
                    
                    if st.button(f"Reuse This Prompt", key=f"reuse_{i}"):
                        st.session_state.current_prompt = item['original']
                        st.session_state.optimized_prompts = item['optimized']
                        st.success("Prompt loaded!")
                        st.rerun()
        else:
            st.info("No prompt history yet. Start optimizing prompts to build your history!")

if __name__ == "__main__":
    main()
