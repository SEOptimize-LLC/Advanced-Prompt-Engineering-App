import streamlit as st
import json
import re
from datetime import datetime
import pandas as pd
from typing import Dict, List, Tuple
import hashlib
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Advanced Prompt Engineering Tool",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .highlight {
        background-color: #ffd700;
        padding: 2px 5px;
        border-radius: 3px;
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

# Model configurations
MODELS = {
    "Anthropic": {
        "models": ["Claude 4 Opus", "Claude 4 Sonnet", "Claude 3.5 Sonnet", "Claude 3 Haiku"],
        "max_tokens": 200000,
        "pricing": {"input": 0.015, "output": 0.075},  # per 1K tokens
        "strengths": ["Complex reasoning", "Creative writing", "Code generation", "Long context"],
        "formatting_tips": [
            "Use XML tags for structure",
            "Provide clear role definitions",
            "Use step-by-step instructions",
            "Include examples when possible"
        ]
    },
    "OpenAI": {
        "models": ["GPT-4 Turbo", "GPT-4", "GPT-3.5 Turbo"],
        "max_tokens": 128000,
        "pricing": {"input": 0.01, "output": 0.03},
        "strengths": ["General knowledge", "Function calling", "JSON mode", "Vision capabilities"],
        "formatting_tips": [
            "Use system messages effectively",
            "Specify output format clearly",
            "Use temperature for creativity control",
            "Leverage function calling for structured outputs"
        ]
    },
    "Google": {
        "models": ["Gemini 2.5 Pro", "Gemini 2.5 Flash", "Gemini 2.0", "Gemini 1.5 Pro"],
        "max_tokens": 2000000,
        "pricing": {"input": 0.00125, "output": 0.005},
        "strengths": ["Multimodal understanding", "Long context", "Speed", "Cost efficiency"],
        "formatting_tips": [
            "Use clear task descriptions",
            "Leverage multimodal capabilities",
            "Provide context upfront",
            "Use structured prompts for complex tasks"
        ]
    }
}

# Sample prompts library
SAMPLE_PROMPTS = {
    "Code Generation": {
        "description": "Optimized for generating clean, efficient code",
        "template": """You are an expert software engineer. Your task is to:

1. Understand the requirements completely
2. Write clean, efficient, and well-documented code
3. Follow best practices and design patterns
4. Include error handling and edge cases

Requirements: {requirements}

Please provide:
- Complete implementation
- Code comments explaining complex logic
- Usage examples
- Time and space complexity analysis where relevant"""
    },
    "Data Analysis": {
        "description": "Structured approach for data analysis tasks",
        "template": """Analyze the following data with a systematic approach:

Dataset: {dataset_description}

Your analysis should include:
1. **Data Overview**: Key statistics and patterns
2. **Insights**: Notable findings and correlations
3. **Anomalies**: Unusual patterns or outliers
4. **Recommendations**: Actionable insights based on analysis
5. **Limitations**: Any constraints or caveats

Use clear visualizations descriptions and quantitative metrics."""
    },
    "Creative Writing": {
        "description": "Enhanced creativity with structure",
        "template": """Create a compelling {content_type} with these parameters:

Theme: {theme}
Tone: {tone}
Target Audience: {audience}

Requirements:
- Engaging opening that hooks the reader
- Rich, vivid descriptions
- Strong character development (if applicable)
- Clear narrative arc
- Satisfying conclusion

Additional constraints: {constraints}"""
    },
    "Research & Synthesis": {
        "description": "Comprehensive research and information synthesis",
        "template": """Conduct thorough research on: {topic}

Provide a comprehensive analysis including:

## Executive Summary
Brief overview of key findings

## Detailed Analysis
- Current state of knowledge
- Key stakeholders and perspectives
- Recent developments and trends
- Challenges and opportunities

## Evidence and Sources
Cite credible sources and data points

## Conclusions
Synthesize findings into actionable insights

## Future Outlook
Predictions and recommendations

Depth level: {depth_level}
Focus areas: {focus_areas}"""
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

def optimize_prompt(prompt: str, provider: str, focus_areas: List[str]) -> str:
    """Optimize prompt based on provider and focus areas"""
    optimized = prompt
    
    # Provider-specific optimizations
    if provider == "Anthropic":
        if "Structure" in focus_areas:
            optimized = f"<task>\n{optimized}\n</task>"
        if "Clarity" in focus_areas:
            optimized = re.sub(r'\n{3,}', '\n\n', optimized)
            optimized = optimized.replace("Please ", "").replace("Could you ", "")
    
    elif provider == "OpenAI":
        if "Structure" in focus_areas:
            optimized = f"### Task\n{optimized}\n\n### Requirements\n- Provide detailed response\n- Use clear formatting"
        if "JSON Output" in focus_areas:
            optimized += "\n\nRespond with valid JSON format."
    
    elif provider == "Google":
        if "Structure" in focus_areas:
            optimized = f"**Task Description:**\n{optimized}\n\n**Expected Output:**\nProvide comprehensive response with clear sections."
    
    # Universal optimizations
    if "Specificity" in focus_areas:
        # Add specificity hints
        if "explain" in optimized.lower() and "how" not in optimized.lower():
            optimized = optimized.replace("explain", "explain step-by-step how")
        if "write" in optimized.lower() and "code" in optimized.lower():
            optimized += "\nInclude comments and error handling."
    
    if "Examples" in focus_areas:
        optimized += "\n\nProvide specific examples to illustrate your points."
    
    if "Constraints" in focus_areas:
        optimized += "\n\nConstraints: Be concise, focus on practical applications, avoid jargon."
    
    return optimized

def generate_prompt_hash(prompt: str) -> str:
    """Generate a unique hash for a prompt"""
    return hashlib.md5(prompt.encode()).hexdigest()[:8]

def export_prompt_report(prompt_data: Dict) -> str:
    """Generate a downloadable report"""
    report = f"""# Prompt Engineering Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Original Prompt
{prompt_data.get('original', '')}

## Metrics
- Word Count: {prompt_data.get('metrics', {}).get('word_count', 0)}
- Character Count: {prompt_data.get('metrics', {}).get('char_count', 0)}
- Clarity Score: {prompt_data.get('metrics', {}).get('clarity_score', 0)}%
- Estimated Tokens: {prompt_data.get('metrics', {}).get('estimated_tokens', 0)}

## Optimized Versions

"""
    for provider, optimized in prompt_data.get('optimized', {}).items():
        report += f"### {provider}\n```\n{optimized}\n```\n\n"
    
    return report

# Main App
def main():
    st.title("?? Advanced Prompt Engineering Tool")
    st.markdown("Optimize your prompts across all major LLM providers with AI-powered suggestions")
    
    # Sidebar
    with st.sidebar:
        st.header("?? Configuration")
        
        selected_providers = st.multiselect(
            "Select Providers",
            options=list(MODELS.keys()),
            default=list(MODELS.keys())
        )
        
        st.subheader("?? Focus Areas")
        focus_areas = st.multiselect(
            "Select optimization focus",
            ["Structure", "Clarity", "Specificity", "Examples", "Constraints", "JSON Output"],
            default=["Structure", "Clarity"]
        )
        
        st.subheader("?? Token & Cost Estimator")
        if selected_providers:
            st.info("Token estimates and costs will appear after entering a prompt")
        
        st.divider()
        
        st.subheader("?? Quick Actions")
        if st.button("?? Load Sample Prompt"):
            st.session_state.show_samples = True
        
        if st.button("?? View History"):
            st.session_state.show_history = True
        
        if st.button("?? Export All"):
            st.session_state.export_all = True
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["? Optimize", "?? Templates", "?? Analysis", "?? Compare", "?? History"])
    
    with tab1:
        st.header("Prompt Optimization Workshop")
        
        # Input area
        col1, col2 = st.columns([3, 1])
        with col1:
            prompt_input = st.text_area(
                "Enter your prompt",
                value=st.session_state.current_prompt,
                height=200,
                placeholder="Type or paste your prompt here...",
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
        if st.button("?? Optimize Prompt", type="primary", use_container_width=True):
            if prompt_input:
                st.session_state.current_prompt = prompt_input
                
                # Generate optimized versions
                with st.spinner("Optimizing for each provider..."):
                    optimized_prompts = {}
                    for provider in selected_providers:
                        optimized = optimize_prompt(prompt_input, provider, focus_areas)
                        optimized_prompts[provider] = optimized
                    
                    st.session_state.optimized_prompts = optimized_prompts
                    
                    # Add to history
                    st.session_state.prompt_history.append({
                        "timestamp": datetime.now(),
                        "original": prompt_input,
                        "optimized": optimized_prompts,
                        "metrics": metrics,
                        "focus_areas": focus_areas
                    })
        
        # Display optimized versions
        if st.session_state.optimized_prompts:
            st.divider()
            st.subheader("?? Optimized Versions")
            
            for provider, optimized in st.session_state.optimized_prompts.items():
                with st.expander(f"**{provider}** - Optimized Prompt", expanded=True):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.text_area(
                            f"Optimized for {provider}",
                            value=optimized,
                            height=150,
                            key=f"opt_{provider}"
                        )
                        
                        # Provider-specific tips
                        with st.container():
                            st.markdown("**Optimization Tips Applied:**")
                            for tip in MODELS[provider]["formatting_tips"][:2]:
                                st.markdown(f" {tip}")
                    
                    with col2:
                        st.markdown("**Provider Strengths:**")
                        for strength in MODELS[provider]["strengths"][:2]:
                            st.markdown(f"? {strength}")
                        
                        # Cost estimation
                        est_tokens = calculate_metrics(optimized)['estimated_tokens']
                        est_cost = (est_tokens / 1000) * MODELS[provider]["pricing"]["input"]
                        st.metric("Est. Cost", f"${est_cost:.4f}")
                        
                        if st.button(f"?? Copy", key=f"copy_{provider}"):
                            st.success(f"Copied {provider} prompt!")
    
    with tab2:
        st.header("?? Prompt Templates Library")
        
        # Template categories
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_template = st.selectbox(
                "Select Template Category",
                options=list(SAMPLE_PROMPTS.keys())
            )
        
        with col2:
            if selected_template:
                st.info(SAMPLE_PROMPTS[selected_template]["description"])
        
        if selected_template:
            st.divider()
            
            # Display template
            st.markdown("### Template Structure")
            template_text = SAMPLE_PROMPTS[selected_template]["template"]
            st.code(template_text, language="markdown")
            
            # Template customization
            st.markdown("### Customize Template")
            
            # Extract variables from template
            variables = re.findall(r'\{(\w+)\}', template_text)
            
            if variables:
                custom_values = {}
                cols = st.columns(min(3, len(variables)))
                for i, var in enumerate(variables):
                    with cols[i % len(cols)]:
                        custom_values[var] = st.text_input(
                            f"{var.replace('_', ' ').title()}",
                            key=f"var_{var}"
                        )
                
                if st.button("Generate Custom Prompt", type="primary"):
                    try:
                        custom_prompt = template_text.format(**custom_values)
                        st.session_state.current_prompt = custom_prompt
                        st.success("Template applied! Go to Optimize tab to continue.")
                        st.text_area("Generated Prompt", value=custom_prompt, height=200)
                    except KeyError:
                        st.error("Please fill in all template variables")
    
    with tab3:
        st.header("?? Prompt Analysis Dashboard")
        
        if prompt_input:
            # Detailed metrics
            col1, col2, col3 = st.columns(3)
            
            metrics = calculate_metrics(prompt_input)
            
            with col1:
                st.markdown("### Structure Analysis")
                st.metric("Sentences", metrics['sentence_count'])
                st.metric("Avg Word Length", metrics['avg_word_length'])
                
                # Check for common issues
                issues = []
                if metrics['word_count'] < 10:
                    issues.append("? Very short prompt")
                if metrics['sentence_count'] < 2:
                    issues.append("? Consider adding more detail")
                if metrics['avg_word_length'] > 7:
                    issues.append("?? Complex vocabulary")
                
                if issues:
                    st.warning("Potential Issues:")
                    for issue in issues:
                        st.markdown(issue)
            
            with col2:
                st.markdown("### Token & Cost Analysis")
                
                for provider in selected_providers:
                    tokens = metrics['estimated_tokens']
                    cost = (tokens / 1000) * MODELS[provider]["pricing"]["input"]
                    
                    st.markdown(f"**{provider}**")
                    st.markdown(f" Tokens: ~{tokens}")
                    st.markdown(f" Cost: ${cost:.5f}")
                    st.markdown("---")
            
            with col3:
                st.markdown("### Optimization Suggestions")
                
                suggestions = []
                if metrics['clarity_score'] < 70:
                    suggestions.append("?? Simplify sentence structure")
                if "?" not in prompt_input and "question" not in prompt_input.lower():
                    suggestions.append("? Consider framing as a clear question")
                if metrics['word_count'] > 500:
                    suggestions.append("?? Consider breaking into sub-tasks")
                if not any(keyword in prompt_input.lower() for keyword in ['please', 'provide', 'create', 'generate', 'write']):
                    suggestions.append("?? Add clear action verbs")
                
                if suggestions:
                    for suggestion in suggestions:
                        st.info(suggestion)
                else:
                    st.success("? Prompt structure looks good!")
            
            # Advanced analysis
            st.divider()
            st.subheader("?? Advanced Analysis")
            
            # Complexity analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Keyword Density")
                words = prompt_input.lower().split()
                word_freq = {}
                for word in words:
                    if len(word) > 4:  # Only significant words
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                if word_freq:
                    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
                    df = pd.DataFrame(sorted_words, columns=['Keyword', 'Frequency'])
                    st.dataframe(df, use_container_width=True)
            
            with col2:
                st.markdown("### Readability Metrics")
                
                # Flesch Reading Ease approximation
                syllables_per_word = metrics['avg_word_length'] / 3  # Rough estimate
                words_per_sentence = metrics['word_count'] / max(metrics['sentence_count'], 1)
                
                flesch_score = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
                flesch_score = max(0, min(100, flesch_score))
                
                st.metric("Readability Score", f"{flesch_score:.1f}/100")
                
                if flesch_score > 60:
                    st.success("Easy to read")
                elif flesch_score > 30:
                    st.warning("Moderate difficulty")
                else:
                    st.error("Difficult to read")
        else:
            st.info("Enter a prompt in the Optimize tab to see detailed analysis")
    
    with tab4:
        st.header("?? Provider Comparison")
        
        if st.session_state.optimized_prompts:
            # Side-by-side comparison
            cols = st.columns(len(st.session_state.optimized_prompts))
            
            for i, (provider, optimized) in enumerate(st.session_state.optimized_prompts.items()):
                with cols[i]:
                    st.markdown(f"### {provider}")
                    
                    # Mini metrics
                    metrics = calculate_metrics(optimized)
                    st.metric("Tokens", metrics['estimated_tokens'])
                    
                    cost = (metrics['estimated_tokens'] / 1000) * MODELS[provider]["pricing"]["input"]
                    st.metric("Est. Cost", f"${cost:.5f}")
                    
                    # Strengths for this use case
                    st.markdown("**Best for:**")
                    for strength in MODELS[provider]["strengths"][:2]:
                        st.markdown(f" {strength}")
                    
                    # Show optimized prompt
                    with st.expander("View Prompt"):
                        st.text(optimized[:500] + "..." if len(optimized) > 500 else optimized)
            
            # Comparison chart
            st.divider()
            st.subheader("?? Cost-Benefit Analysis")
            
            # Create comparison dataframe
            comparison_data = []
            for provider in st.session_state.optimized_prompts.keys():
                metrics = calculate_metrics(st.session_state.optimized_prompts[provider])
                comparison_data.append({
                    "Provider": provider,
                    "Tokens": metrics['estimated_tokens'],
                    "Cost ($)": (metrics['estimated_tokens'] / 1000) * MODELS[provider]["pricing"]["input"],
                    "Max Context": MODELS[provider]["max_tokens"],
                    "Clarity Score": metrics['clarity_score']
                })
            
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True)
            
            # Recommendation
            best_value = df.loc[df['Cost ($)'].idxmin()]
            best_clarity = df.loc[df['Clarity Score'].idxmax()]
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"?? Best Value: **{best_value['Provider']}** (${best_value['Cost ($)']:.5f})")
            with col2:
                st.success(f"? Best Clarity: **{best_clarity['Provider']}** ({best_clarity['Clarity Score']:.1f}%)")
        else:
            st.info("Optimize a prompt first to see provider comparisons")
    
    with tab5:
        st.header("?? Prompt History")
        
        if st.session_state.prompt_history:
            # History controls
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                search_term = st.text_input("?? Search history", placeholder="Search prompts...")
            
            with col2:
                if st.button("Clear History"):
                    st.session_state.prompt_history = []
                    st.rerun()
            
            with col3:
                if st.button("Export History"):
                    # Create JSON export
                    history_json = json.dumps(
                        [
                            {
                                "timestamp": item["timestamp"].isoformat(),
                                "original": item["original"],
                                "optimized": item["optimized"],
                                "metrics": item["metrics"]
                            }
                            for item in st.session_state.prompt_history
                        ],
                        indent=2
                    )
                    st.download_button(
                        label="Download JSON",
                        data=history_json,
                        file_name=f"prompt_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            # Display history
            filtered_history = st.session_state.prompt_history
            if search_term:
                filtered_history = [
                    item for item in filtered_history
                    if search_term.lower() in item["original"].lower()
                ]
            
            for i, item in enumerate(reversed(filtered_history[-10:])):  # Show last 10
                with st.expander(
                    f"?? {item['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
                    f"{item['original'][:50]}...",
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown("**Original Prompt:**")
                        st.text(item['original'])
                        
                        st.markdown("**Optimized Versions:**")
                        for provider, optimized in item['optimized'].items():
                            st.markdown(f"*{provider}:*")
                            st.text(optimized[:200] + "..." if len(optimized) > 200 else optimized)
                    
                    with col2:
                        st.markdown("**Metrics:**")
                        for key, value in item['metrics'].items():
                            st.markdown(f" {key}: {value}")
                        
                        if st.button(f"Reuse", key=f"reuse_{i}"):
                            st.session_state.current_prompt = item['original']
                            st.session_state.optimized_prompts = item['optimized']
                            st.success("Prompt loaded!")
                            st.rerun()
        else:
            st.info("No prompt history yet. Start optimizing prompts to build your history!")
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("?? **Tip:** Use XML tags for Claude, JSON for GPT models")
    with col2:
        st.markdown("?? **Stats:** Optimized {0} prompts today".format(len(st.session_state.prompt_history)))
    with col3:
        st.markdown("?? **Version:** 1.0.0 | Updated: 2024")

if __name__ == "__main__":
    main()